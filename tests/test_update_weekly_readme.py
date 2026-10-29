"""Dependency-free regression tests for the README-only Weekly synchronization."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from update_weekly_readme import END, START, main, render_latest, replace_block  # noqa: E402


def issue(number, name, published):
    return {
        "issue": number,
        "title": f"第 {number} 期 - {name}",
        "date": published,
        "url": f"https://weekly.yano.blog/posts/{number}",
    }


ISSUES = [
    issue(6, "理财思考", "2026/09/20"),
    issue(8, "游戏翻译", "2026/10/18"),
    issue(5, "虎邦辣酱", "2026/09/20"),
    issue(7, "AI 竞争力", "2026-10-11T00:00:00.000Z"),
]


class WeeklyReadmeTests(unittest.TestCase):
    def test_newest_three_are_sorted_and_dates_normalized(self):
        result = render_latest({"issues": ISSUES})
        self.assertEqual(
            result.splitlines(),
            [
                "- [第 8 期 - 游戏翻译](https://weekly.yano.blog/posts/8) · 2026-10-18",
                "- [第 7 期 - AI 竞争力](https://weekly.yano.blog/posts/7) · 2026-10-11",
                "- [第 6 期 - 理财思考](https://weekly.yano.blog/posts/6) · 2026-09-20",
            ],
        )

    def test_escape_markdown_in_a_title(self):
        item = issue(9, "[测试]*重要*", "2026-10-26")
        self.assertIn(r"\[测试\]\*重要\*", render_latest({"issues": [item, ISSUES[1], ISSUES[0]]}))

    def test_rejects_broken_feeds_and_untrusted_urls(self):
        for payload in ({}, {"issues": []}, {"issues": [ISSUES[0]]}, {"issues": [issue(8, "A", "2026/10/18")] * 3}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                render_latest(payload)
        for changes in (
            {"url": "https://example.com/posts/8"},
            {"url": "https://weekly.yano.blog/posts/8?redirect=1"},
            {"url": "https://weekly.yano.blog/posts/7"},
            {"date": "not-a-date"},
            {"date": "2026/02/30"},
            {"title": ""},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                render_latest({"issues": [{**ISSUES[1], **changes}, ISSUES[0], ISSUES[3]]})

    def test_replaces_only_marked_section_and_is_idempotent(self):
        original = f"# Yano's Notes\n\nIntro\n\n{START}\nold\n{END}\n\n[INDEX.md](INDEX.md)\n"
        updated = replace_block(original, render_latest({"issues": ISSUES}))
        self.assertTrue(updated.startswith("# Yano's Notes\n\nIntro\n"))
        self.assertTrue(updated.endswith("\n\n[INDEX.md](INDEX.md)\n"))
        self.assertEqual(replace_block(updated, render_latest({"issues": ISSUES})), updated)
        self.assertNotIn("old\n", updated)
        for broken in ("no markers", f"{START}\nno end", f"{END}\n{START}"):
            with self.subTest(broken=broken), self.assertRaises(ValueError):
                replace_block(broken, "text")

    def test_cli_offline_check_sync_and_index_untouched(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            readme = root / "README.md"
            index = root / "INDEX.md"
            feed = root / "feed.json"
            original = f"# Notes\n{START}\nold\n{END}\n"
            readme.write_text(original, encoding="utf-8")
            index.write_text("Do not modify this index!\n", encoding="utf-8")
            feed.write_text(json.dumps({"issues": ISSUES}, ensure_ascii=False), encoding="utf-8")
            args = ["--readme", str(readme), "--feed-file", str(feed)]
            self.assertEqual(main(args + ["--check"]), 1)
            self.assertEqual(readme.read_text(encoding="utf-8"), original)
            self.assertEqual(main(args), 0)
            synchronized = readme.read_text(encoding="utf-8")
            self.assertEqual(main(args + ["--check"]), 0)
            self.assertEqual(main(args), 0)
            self.assertEqual(readme.read_text(encoding="utf-8"), synchronized)
            self.assertEqual(index.read_text(encoding="utf-8"), "Do not modify this index!\n")

    def test_checked_in_readme_has_one_ordered_marker_pair(self):
        readme_path = Path(__file__).resolve().parents[1] / "README.md"
        if readme_path.exists():
            text = readme_path.read_text(encoding="utf-8")
            self.assertEqual(text.count(START), 1)
            self.assertEqual(text.count(END), 1)
            self.assertLess(text.index(START), text.index(END))


if __name__ == "__main__":
    unittest.main()
