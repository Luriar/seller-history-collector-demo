"""Synthetic, repeated observation snapshots with idempotent persistence."""
from __future__ import annotations
import csv
import json
import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import mean
from urllib.parse import urlsplit, urlunsplit


@dataclass(frozen=True)
class Activity:
    likes: int
    comments: int


@dataclass(frozen=True)
class Observation:
    code: str
    observed_on: str
    posts: tuple[Activity, ...]
    links: tuple[str, ...] = ()


def normalize_links(links: tuple[str, ...]) -> list[str]:
    """Only retain explicitly fictional HTTPS example.invalid links."""
    cleaned: set[str] = set()
    for raw in links:
        try:
            p = urlsplit(raw)
            if p.scheme != "https" or p.hostname != "example.invalid":
                continue
            cleaned.add(urlunsplit(("https", "example.invalid", p.path.rstrip("/") or "/", "", "")))
        except (ValueError, AttributeError):
            continue
    return sorted(cleaned)


def summarize(observation: Observation) -> dict:
    if not observation.code.strip():
        raise ValueError("account code required")
    date.fromisoformat(observation.observed_on)
    if any(p.likes < 0 or p.comments < 0 for p in observation.posts):
        raise ValueError("engagement cannot be negative")
    return {
        "code": observation.code,
        "observed_on": observation.observed_on,
        "post_count": len(observation.posts),
        "avg_likes": round(mean(p.likes for p in observation.posts), 2)
            if observation.posts else None,
        "avg_comments": round(mean(p.comments for p in observation.posts), 2)
            if observation.posts else None,
        "links_json": json.dumps(normalize_links(observation.links)),
    }


class HistoryStore:
    def __init__(self, path: str | Path = ":memory:"):
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS observations(
                code TEXT NOT NULL,
                observed_on TEXT NOT NULL,
                post_count INTEGER NOT NULL,
                avg_likes REAL,
                avg_comments REAL,
                links_json TEXT NOT NULL,
                PRIMARY KEY(code,observed_on)
            )
        """)
        self.db.commit()

    def add(self, observations: list[Observation]) -> dict:
        counts = {"inserted": 0, "updated": 0, "unchanged": 0}
        with self.db:
            for obs in observations:
                row = summarize(obs)
                current = self.db.execute("""
                    SELECT post_count,avg_likes,avg_comments,links_json FROM observations
                    WHERE code=? AND observed_on=?
                """, (row["code"],row["observed_on"])).fetchone()
                values = (row["post_count"],row["avg_likes"],row["avg_comments"],row["links_json"])
                if current is not None and tuple(current) == values:
                    counts["unchanged"] += 1
                    continue
                self.db.execute("""
                    INSERT INTO observations
                      (code,observed_on,post_count,avg_likes,avg_comments,links_json)
                    VALUES (?,?,?,?,?,?)
                    ON CONFLICT(code,observed_on) DO UPDATE SET
                      post_count=excluded.post_count,
                      avg_likes=excluded.avg_likes,
                      avg_comments=excluded.avg_comments,
                      links_json=excluded.links_json
                """, (row["code"],row["observed_on"])+values)
                counts["inserted" if current is None else "updated"] += 1
        return counts

    def history(self, code: str) -> list[dict]:
        return [dict(row) for row in self.db.execute(
            "SELECT * FROM observations WHERE code=? ORDER BY observed_on", (code,)
        )]

    def trend(self, code: str) -> dict | None:
        rows=self.history(code)
        if len(rows) < 2:
            return None
        first,last=rows[0],rows[-1]
        def delta(key):
            return round(last[key]-first[key],2) if (
                last[key] is not None and first[key] is not None
            ) else None
        return {
            "code": code, "first": first["observed_on"], "last": last["observed_on"],
            "avg_likes_change": delta("avg_likes"),
            "avg_comments_change": delta("avg_comments"),
            "note": "Descriptive difference only; no growth prediction",
        }

    def export_csv(self, path: str | Path) -> None:
        rows=[dict(row) for row in self.db.execute(
            "SELECT * FROM observations ORDER BY code,observed_on"
        )]
        with open(path,"w",encoding="utf-8",newline="") as out:
            writer=csv.DictWriter(out,fieldnames=(
                "code","observed_on","post_count","avg_likes","avg_comments","links_json"
            ))
            writer.writeheader()
            writer.writerows(rows)

    def close(self):
        self.db.close()


def load_fixture(path: str | Path) -> list[Observation]:
    content=json.loads(Path(path).read_text(encoding="utf-8"))
    return [Observation(
        code=str(rec["code"]), observed_on=str(rec["observed_on"]),
        posts=tuple(Activity(int(p["likes"]),int(p["comments"])) for p in rec["posts"]),
        links=tuple(str(link) for link in rec.get("links",[]))
    ) for rec in content]
