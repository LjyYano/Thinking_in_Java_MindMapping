#!/usr/bin/env python3
"""
Generate the README article navigation block.

Rules:
- Scan top-level directories (non-dot, excluding "scripts").
- For each top-level directory, render a collapsible <details> block.
- If the top-level dir has direct *.md files, render a "(根目录)" table.
- If it has subdirectories, each subdirectory gets its own table.
- Table columns: 标题 (relative link), 日期 (from YAML front matter `date:`).
- Replace the block between <!-- AUTO-ARTICLE-NAV:START --> and <!-- AUTO-ARTICLE-NAV:END -->.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple
from urllib.parse import quote

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"

START_MARK = "<!-- AUTO-ARTICLE-NAV:START -->"
END_MARK = "<!-- AUTO-ARTICLE-NAV:END -->"
TOC_START = "<!-- AUTO-TOC:START -->"
TOC_END = "<!-- AUTO-TOC:END -->"


def iter_markdown_files(directory: Path) -> Iterable[Path]:
    for path in directory.iterdir():
        if path.is_file() and path.suffix.lower() == ".md":
            yield path


def parse_date_from_front_matter(path: Path) -> str:
    """
    Parse YAML front matter looking for `date:`. Reads the first 80 lines at most.
    Returns '' if not found.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            # Read at most 80 lines without failing on short files
            lines = []
            for _, line in zip(range(80), f):
                lines.append(line)
    except FileNotFoundError:
        return ""
    except Exception:
        return ""

    content = "".join(lines)
    if not content.startswith("---"):
        return ""

    # Extract block between the first two '---'
    fm_match = re.match(r"---(.*?)---", content, re.DOTALL)
    if not fm_match:
        return ""

    front_matter = fm_match.group(1)
    for line in front_matter.splitlines():
        line = line.strip()
        if line.lower().startswith("date:"):
            return line.split(":", 1)[1].strip()
    return ""


def parse_date_value(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def encode_rel_path(path: Path) -> str:
    parts = [quote(p) for p in path.as_posix().split("/")]
    return "/".join(parts)


def build_table(rows: List[dict]) -> str:
    if not rows:
        return ""
    lines = [
        '<table style="width:100%; table-layout:fixed;">',
        '<thead><tr><th style="text-align:left; width:70%">标题</th><th style="text-align:left; width:30%">日期</th></tr></thead>',
        "<tbody>",
    ]
    for item in rows:
        date_cell = item["date"] or "-"
        lines.append(
            f'<tr><td><a href="{item["link"]}">{item["title"]}</a></td><td>{date_cell}</td></tr>'
        )
    lines.append("</tbody></table>")
    return "\n".join(lines)


def sort_rows(rows: List[dict]) -> List[dict]:
    """Sorting rule: title ascending (case-insensitive)."""
    return sorted(rows, key=lambda item: item["title"].casefold())


def render_top_dir(top_dir: Path) -> str:
    sections: List[str] = []

    # Root-level markdown files in this top-level directory
    root_rows = sort_rows(
        [
            {
                "title": md.name,
                "link": encode_rel_path(md.relative_to(REPO_ROOT)),
                "date": parse_date_from_front_matter(md),
            }
            for md in iter_markdown_files(top_dir)
            if md.name != "README.md"
        ]
    )
    if root_rows:
        sections.append(build_table(root_rows))

    # Subdirectories (second-level)
    for sub_dir in sorted(
        (p for p in top_dir.iterdir() if p.is_dir() and not p.name.startswith(".")),
        key=lambda p: p.name,
    ):
        rows = sort_rows(
            [
                {
                    "title": md.name,
                    "link": encode_rel_path(md.relative_to(REPO_ROOT)),
                    "date": parse_date_from_front_matter(md),
                }
                for md in iter_markdown_files(sub_dir)
            ]
        )
        if rows:
            sections.append(f"### {sub_dir.name}\n" + build_table(rows))

    if not sections:
        return ""

    inner = "\n\n".join(sections)
    return (
        "<details open>\n"
        f'<summary><h2 style="display:inline">{top_dir.name}</h2></summary>\n\n'
        f"{inner}\n\n"
        "</details>"
    )


def generate_nav_block() -> str:
    blocks: List[str] = []
    for top_dir in sorted(
        (
            p
            for p in REPO_ROOT.iterdir()
            if p.is_dir()
            and not p.name.startswith(".")
            and p.name not in {"scripts", ".git", ".github"}
        ),
        key=lambda p: p.name,
    ):
        block = render_top_dir(top_dir)
        if block:
            blocks.append(block)
    return "\n\n".join(blocks)


def ensure_markers(readme_text: str) -> str:
    if START_MARK in readme_text and END_MARK in readme_text:
        return readme_text

    # Insert empty block after '# 文章导航' heading
    heading_pattern = re.compile(r"(#\s*文章导航\s*\n)", re.IGNORECASE)
    match = heading_pattern.search(readme_text)
    if not match:
        raise SystemExit("Heading '# 文章导航' not found; cannot insert markers.")

    insert_pos = match.end()
    insertion = f"{START_MARK}\n{END_MARK}\n"
    return readme_text[:insert_pos] + insertion + readme_text[insert_pos:]


def replace_block(readme_text: str, new_block: str) -> str:
    pattern = re.compile(
        rf"{re.escape(START_MARK)}.*?{re.escape(END_MARK)}", re.DOTALL
    )
    replacement = f"{START_MARK}\n{new_block}\n{END_MARK}"
    return pattern.sub(replacement, readme_text, count=1)


def replace_block_generic(
    text: str, start: str, end: str, new_block: str, insert_pos: int = 0
) -> str:
    if start in text and end in text:
        pattern = re.compile(rf"{re.escape(start)}.*?{re.escape(end)}", re.DOTALL)
        return pattern.sub(f"{start}\n{new_block}\n{end}", text, count=1)
    # Insert when markers are absent
    return text[:insert_pos] + f"{start}\n{new_block}\n{end}\n" + text[insert_pos:]


def ensure_toc_markers(readme_text: str) -> str:
    if TOC_START in readme_text and TOC_END in readme_text:
        return readme_text
    return f"{TOC_START}\n{TOC_END}\n" + readme_text


def slugify_anchor(title: str) -> str:
    text = title.strip().lower()
    text = re.sub(r"[^\w\- ]+", "", text)
    text = text.replace(" ", "-")
    text = re.sub(r"-+", "-", text)
    return text


def strip_block(text: str, start: str, end: str) -> str:
    if start in text and end in text:
        pattern = re.compile(rf"{re.escape(start)}.*?{re.escape(end)}", re.DOTALL)
        return pattern.sub("", text, count=1)
    return text


def generate_toc(readme_text: str, max_level: int = 3) -> str:
    """Generate unordered-list TOC up to max_level headings."""
    content = strip_block(readme_text, TOC_START, TOC_END)
    lines = content.splitlines()
    toc_lines: List[str] = []
    for line in lines:
        m = re.match(r"^(#{1,%d})\s+(.+?)\s*$" % max_level, line)
        if not m:
            continue
        level = len(m.group(1))
        title = m.group(2)
        anchor = slugify_anchor(title)
        indent = "  " * (level - 1)
        toc_lines.append(f"{indent}- [{title}](#{anchor})")
    return "\n".join(toc_lines)


def main() -> None:
    readme = README_PATH.read_text(encoding="utf-8")

    # Ensure markers exist
    readme = ensure_toc_markers(readme)
    readme = ensure_markers(readme)

    # Update TOC (unordered, up to h3)
    toc_block = generate_toc(readme, max_level=3)
    readme = replace_block_generic(readme, TOC_START, TOC_END, toc_block, insert_pos=0)

    # Update article navigation
    nav_block = generate_nav_block()
    if nav_block:
        nav_block = nav_block.rstrip() + "\n\n"
    readme = replace_block(readme, nav_block)

    README_PATH.write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()

