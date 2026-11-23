import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import unittest
from demo import Post, summarize

class SummaryTests(unittest.TestCase):
    def test_snapshot(self):
        x=summarize("x",[Post(10,2),Post(30,4)],["https://example.invalid","http://ignore.invalid"])
        self.assertEqual(x["avg_likes"],20.0)
        self.assertEqual(x["link_count"],1)
    def test_empty(self):
        self.assertIsNone(summarize("x",[])["avg_comments"])

if __name__ == "__main__":
    unittest.main()
