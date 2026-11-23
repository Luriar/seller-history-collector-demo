import tempfile
import unittest
from pathlib import Path
from history_engine import Activity, Observation, HistoryStore, normalize_links


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=HistoryStore(Path(self.temp.name)/"history.sqlite")

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_snapshot_is_idempotent(self):
        obs=Observation("demo-1","2026-01-01",(Activity(10,2),))
        self.assertEqual(self.store.add([obs])["inserted"],1)
        self.assertEqual(self.store.add([obs])["unchanged"],1)
        self.assertEqual(len(self.store.history("demo-1")),1)

    def test_snapshot_upsert(self):
        self.store.add([Observation("demo-1","2026-01-01",(Activity(10,1),))])
        self.assertEqual(self.store.add(
            [Observation("demo-1","2026-01-01",(Activity(15,3),))]
        )["updated"],1)
        self.assertEqual(self.store.history("demo-1")[0]["avg_likes"],15)

    def test_trend_without_prediction(self):
        self.store.add([
            Observation("demo-1","2026-01-01",(Activity(10,2),)),
            Observation("demo-1","2026-01-08",(Activity(25,4),)),
        ])
        change=self.store.trend("demo-1")
        self.assertEqual(change["avg_likes_change"],15.0)
        self.assertIsNone(self.store.trend("nonexistent"))

    def test_invalid_metrics_rollback(self):
        with self.assertRaises(ValueError):
            self.store.add([
                Observation("valid","2026-01-01",(Activity(10,0),)),
                Observation("invalid","2026-01-01",(Activity(-5,0),)),
            ])
        self.assertEqual(self.store.history("valid"),[])

    def test_link_normalization(self):
        x=normalize_links((
            "https://example.invalid/a","https://example.invalid/a/",
            "http://example.invalid/not-https","https://another.invalid/no",
        ))
        self.assertEqual(x,["https://example.invalid/a"])

    def test_csv_export(self):
        self.store.add([Observation("x","2026-01-01",())])
        p=Path(self.temp.name)/"history.csv"
        self.store.export_csv(p)
        self.assertIn("x",p.read_text(encoding="utf-8"))


if __name__=="__main__":
    unittest.main()
