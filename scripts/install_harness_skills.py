#!/usr/bin/env python3
"""Install selected Hermes skills from this harness repository.

The script copies skill directories from ./skills/<category>/<name> into the
active Hermes profile's skills directory. It is intentionally small and
runtime-agnostic enough for a new machine bootstrap: clone the repository, run
this script, then restart Hermes or start a new session.
"""
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "skills"


def hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()


def iter_skills() -> list[Path]:
    if not SOURCE_ROOT.exists():
        return []
    return sorted(p for p in SOURCE_ROOT.glob("*/*") if (p / "SKILL.md").is_file())


def find_skill(name: str) -> Path:
    matches = [p for p in iter_skills() if p.name == name]
    if not matches:
        available = ", ".join(p.name for p in iter_skills()) or "<none>"
        raise SystemExit(f"Skill not found: {name}. Available: {available}")
    if len(matches) > 1:
        rels = ", ".join(str(p.relative_to(SOURCE_ROOT)) for p in matches)
        raise SystemExit(f"Ambiguous skill name {name!r}: {rels}")
    return matches[0]


def copy_skill(src: Path, dest_root: Path, dry_run: bool = False, force: bool = False) -> str:
    rel = src.relative_to(SOURCE_ROOT)
    dst = dest_root / rel
    if dst.exists() and not force:
        return f"skip existing {rel} -> {dst} (use --force to replace)"
    if dry_run:
        action = "replace" if dst.exists() else "install"
        return f"dry-run {action} {rel} -> {dst}"
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)
    return f"installed {rel} -> {dst}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Hermes skills from this repository")
    parser.add_argument("--skill", action="append", help="Skill name to install; repeatable. Defaults to all skills.")
    parser.add_argument("--dest", type=Path, default=None, help="Destination skills root. Defaults to $HERMES_HOME/skills or ~/.hermes/skills.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without copying.")
    parser.add_argument("--force", action="store_true", help="Replace an existing installed skill.")
    parser.add_argument("--list", action="store_true", help="List repository skills and exit.")
    args = parser.parse_args()

    skills = iter_skills()
    if args.list:
        for p in skills:
            print(p.relative_to(SOURCE_ROOT))
        return 0

    selected = [find_skill(name) for name in args.skill] if args.skill else skills
    if not selected:
        raise SystemExit("No skills found under ./skills")

    dest_root = args.dest.expanduser() if args.dest else hermes_home() / "skills"
    for src in selected:
        print(copy_skill(src, dest_root, dry_run=args.dry_run, force=args.force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
