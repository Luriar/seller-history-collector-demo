"""Independent offline activity snapshot example."""
from dataclasses import dataclass
from statistics import mean

@dataclass(frozen=True)
class Post:
    likes: int
    comments: int

def summarize(account_code, posts, external_links=()):
    """Return a fictional activity snapshot with conservative empty handling."""
    if not account_code:
        raise ValueError("account_code is required")
    cleaned = sorted(set(x for x in external_links if x.startswith("https://")))
    return {
        "account_code":account_code,
        "post_count":len(posts),
        "avg_likes":round(mean(p.likes for p in posts),2) if posts else None,
        "avg_comments":round(mean(p.comments for p in posts),2) if posts else None,
        "link_count":len(cleaned),
    }

if __name__ == "__main__":
    print(summarize("fictional-creator",[Post(12,2),Post(20,4)],
                    ["https://example.invalid/landing","https://example.invalid/landing"]))
