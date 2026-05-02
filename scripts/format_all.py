#!/usr/bin/env python3
"""
Normalize text files in the repo: UTF-8, LF newlines, trim trailing whitespace,
single trailing newline at EOF. Safe for .cfg / .md / .mdc / .ini.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTENSIONS = {".cfg", ".md", ".mdc", ".ini", ".json", ".yml", ".yaml"}
ROOT_NAMES = {".gitattributes", ".editorconfig"}
SKIP_DIR_NAMES = {".git", "__pycache__", ".venv", "node_modules"}


def should_skip(path: Path) -> bool:
    if not path.is_file():
        return True
    if path.name not in ROOT_NAMES and path.suffix.lower() not in EXTENSIONS:
        return True
    for part in path.parts:
        if part in SKIP_DIR_NAMES:
            return True
    return False


def format_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def format_file(path: Path) -> bool:
    raw = path.read_bytes()
    if not raw:
        path.write_bytes(b"\n")
        return True
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        print(f"skip (not utf-8): {path.relative_to(ROOT)}", file=sys.stderr)
        return False
    new_text = format_text(text)
    new_bytes = new_text.encode("utf-8")
    if new_bytes != raw:
        path.write_bytes(new_bytes)
        return True
    return False


def main() -> int:
    changed: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if should_skip(path):
            continue
        try:
            if format_file(path):
                changed.append(path)
        except OSError as e:
            print(f"error: {path}: {e}", file=sys.stderr)
            return 1
    for p in changed:
        print(p.relative_to(ROOT))
    print(f"format_all: {len(changed)} file(s) updated", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
