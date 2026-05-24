# -*- coding: utf-8 -*-
"""Scan frontend for encoding corruption (??). Exit 1 if issues found."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
SRC = FRONTEND / "src"
bad: list[str] = []


def check_file(p: Path) -> None:
    try:
        t = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        bad.append(f"{p.relative_to(ROOT)}: invalid UTF-8")
        return
    for i, line in enumerate(t.splitlines(), 1):
        if "AI??" in line or re.search(r"label:\s*'\?\?'", line):
            bad.append(f"{p.relative_to(ROOT)}:{i}")
            continue
        if re.search(r"['\"`][^'\"`]*\?\?[^'\"`]*['\"`]", line):
            if " ?? " in line or "?? 0" in line or "?? ''" in line or "?? null" in line:
                continue
            bad.append(f"{p.relative_to(ROOT)}:{i}")


for p in list(SRC.rglob("*.tsx")) + list(SRC.rglob("*.ts")) + [FRONTEND / "index.html"]:
    check_file(p)

if bad:
    print("ENCODING ISSUES:")
    for b in bad:
        print(" ", b)
    sys.exit(1)
print("OK: no ?? corruption detected")
