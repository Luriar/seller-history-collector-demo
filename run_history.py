"""Execute the sample time-series collection without accessing a website."""
import argparse
import json
from pathlib import Path
from history_engine import HistoryStore, load_fixture


def main():
    parser=argparse.ArgumentParser(description="Offline activity snapshot demo")
    parser.add_argument("--input",default=str(Path(__file__).parent/"fixtures"/"observations.json"))
    parser.add_argument("--db",default=":memory:")
    parser.add_argument("--export")
    args=parser.parse_args()
    db=HistoryStore(args.db)
    try:
        observations=load_fixture(args.input)
        changes=db.add(observations)
        if args.export:
            db.export_csv(args.export)
        print(json.dumps({
            "progress":changes,
            "sample_trend":db.trend("fictional-01"),
            "synthetic_only":True,
        },ensure_ascii=False,indent=2))
    finally:
        db.close()


if __name__=="__main__":
    main()
