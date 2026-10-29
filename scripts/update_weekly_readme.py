#!/usr/bin/env python3
"""Sync the latest three issues from Yano Weekly's public JSON feed into README.md.

The bounded AUTO-WEEKLY block is the only content this script may change.
Failures leave the existing README unchanged.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"
FEED_URL = "https://weekly.yano.blog/api/posts.json"
START = "<!-- AUTO-WEEKLY:START -->"
END = "<!-- AUTO-WEEKLY:END -->"
MAX_FEED_BYTES = 4 * 1024 * 1024


def fetch_feed() -> object:
    """Use the published, read-only issue metadata API (no HTML scraping)."""
    request = Request(
        FEED_URL,
        headers={"Accept": "application/json", "User-Agent": "YanosNotesWeeklySync/1.0"},
    )
    with urlopen(request, timeout=20) as response:
        payload = response.read(MAX_FEED_BYTES + 1)
    if len(payload) > MAX_FEED_BYTES:
        raise ValueError("Weekly feed is unexpectedly large")
    return json.loads(payload)


def normalized_date(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Weekly issue is missing a date")
    # Astro may serialize a frontmatter date as YYYY/MM/DD or as an ISO timestamp.
    match = re.fullmatch(
        r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?",
        value,
    )
    if match is None:
        raise ValueError(f"Invalid Weekly date: {value!r}")
    return date(*(int(part) for part in match.groups()[:3])).isoformat()


def clean_title(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Weekly issue is missing a title")
    title = " ".join(value.split())
    # Escape Markdown syntax in link labels without altering ordinary issue titles.
    return re.sub(r"([\\\[\]\x60*_<>])", r"\\\1", title)


def render_latest(payload: object) -> str:
    if not isinstance(payload, dict) or not isinstance(payload.get("issues"), list):
        raise ValueError("Weekly feed is missing its issues array")

    issues = payload["issues"]
    if len(issues) < 3:
        raise ValueError("Weekly feed returned fewer than three issues")

    seen: set[int] = set()
    for issue in issues:
        if not isinstance(issue, dict):
            raise ValueError("Weekly issue must be an object")
        number = issue.get("issue")
        if isinstance(number, bool) or not isinstance(number, int) or number <= 0:
            raise ValueError("Weekly issue has an invalid issue number")
        if number in seen:
            raise ValueError(f"Duplicate Weekly issue number: {number}")
        seen.add(number)

    lines = []
    for issue in sorted(issues, key=lambda item: item["issue"], reverse=True)[:3]:
        number = issue["issue"]
        url = issue.get("url")
        if not isinstance(url, str):
            raise ValueError(f"Weekly issue {number} is missing its URL")
        parsed = urlsplit(url)
        if (
            parsed.scheme != "https"
            or parsed.netloc != "weekly.yano.blog"
            or parsed.path != f"/posts/{number}"
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(f"Unexpected Weekly issue URL: {url!r}")
        lines.append(
            f"- [{clean_title(issue.get('title'))}]({url}) · {normalized_date(issue.get('date'))}"
        )
    return "\n".join(lines)


def replace_block(readme: str, latest: str) -> str:
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("README must contain exactly one AUTO-WEEKLY marker pair")
    start = readme.index(START) + len(START)
    end = readme.index(END)
    if start >= end:
        raise ValueError("AUTO-WEEKLY markers are out of order")
    return readme[:start] + "\n" + latest + "\n" + readme[end:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=README_PATH)
    parser.add_argument("--feed-file", type=Path, help="Offline JSON feed for tests")
    parser.add_argument("--check", action="store_true", help="Check without modifying README")
    args = parser.parse_args(argv)

    # Fetch and validate completely before reading or modifying local content.
    payload = json.loads(args.feed_file.read_text(encoding="utf-8")) if args.feed_file else fetch_feed()
    latest = render_latest(payload)
    original = args.readme.read_text(encoding="utf-8")
    updated = replace_block(original, latest)
    if original == updated:
        print("Weekly latest issues are already up to date.")
        return 0
    if args.check:
        print("README Weekly latest issues are out of date.")
        return 1
    args.readme.write_text(updated, encoding="utf-8")
    print("Updated README with the latest Weekly issues.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"Weekly sync failed; README was not committed: {error}") from error
