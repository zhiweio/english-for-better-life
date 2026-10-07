#!/usr/bin/env python3
"""扫描 lessons/*/vocab.md,生成 Anki 可导入的 vocabulary/anki-export.csv。

用法:
    python3 scripts/build_anki_csv.py

vocab.md 表头约定(见 .agents/skills/after-class/SKILL.md):
    | 英文 | 音标 | 中文 | 例句 | 来源 |

导入 Anki:文件 → 导入 → 选中生成的 csv → 勾选「允许 HTML 在字段中」。
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS = ROOT / "lessons"
OUT = ROOT / "vocabulary" / "anki-export.csv"

EXPECTED_COLUMNS = 5
HEADER_FIRST_CELLS = {"英文", "English"}


def parse_rows(md_path: Path):
    rows = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < EXPECTED_COLUMNS:
            continue
        if cells[0] in HEADER_FIRST_CELLS:
            continue
        if set(cells[0]) <= set("-: "):  # 表头分隔行 |---|---|
            continue
        term, ipa, meaning, example, source = (c for c in cells[:EXPECTED_COLUMNS])
        if not term:
            continue
        rows.append((term, ipa, meaning, example, source))
    return rows


def main():
    if not LESSONS.is_dir():
        sys.exit("未找到 lessons/ 目录")
    entries = []
    for lesson_dir in sorted(p for p in LESSONS.iterdir() if p.is_dir()):
        vocab = lesson_dir / "vocab.md"
        if not vocab.is_file():
            continue
        for term, ipa, meaning, example, source in parse_rows(vocab):
            entries.append((lesson_dir.name, term, ipa, meaning, example, source))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Front", "Back", "Tags"])
        for date, term, ipa, meaning, example, source in entries:
            back = "<br>".join(part for part in (ipa, meaning, example) if part)
            writer.writerow([term, back, f"english lesson-{date}"])

    print(f"共 {len(entries)} 条词汇 → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
