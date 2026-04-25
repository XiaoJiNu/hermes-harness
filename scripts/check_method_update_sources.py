#!/usr/bin/env python3
"""Inspect local Hermes/Harness update sources for method-sync reviews.

This script is intentionally read-only by default. It reports whether the
harness reference repo and the local Hermes Agent source tree appear to have
upstream changes or dirty local work that should be reviewed before adopting
new methods.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DEFAULT_HERMES_AGENT_CANDIDATES = [
    Path("~/yr/code/harness-engineering-all/hermes-agent").expanduser(),
    Path("~/code/harness-engineering-all/hermes-agent").expanduser(),
]


@dataclass
class GitReport:
    path: str
    exists: bool
    is_git_repo: bool
    branch_status: str = ""
    ahead: Optional[int] = None
    behind: Optional[int] = None
    dirty_count: int = 0
    dirty_paths: Optional[List[str]] = None
    latest_tag: str = ""
    head: str = ""
    error: str = ""


@dataclass
class HermesCliReport:
    hermes_bin: Optional[str]
    first_line: str
    update_line: str
    error: str = ""


@dataclass
class MethodUpdateReport:
    harness_repo: GitReport
    hermes_agent_repo: Optional[GitReport]
    hermes_cli: HermesCliReport
    recommendations: List[str]


def run(cmd: List[str], *, cwd: Optional[Path] = None, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def parse_left_right_count(text: str) -> Tuple[Optional[int], Optional[int]]:
    parts = text.strip().split()
    if len(parts) != 2:
        return None, None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None, None


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def detect_hermes_agent_root(explicit: str) -> Optional[Path]:
    if explicit:
        return Path(explicit).expanduser()
    env_root = os.getenv("HERMES_AGENT_SOURCE_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser()
    for candidate in DEFAULT_HERMES_AGENT_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def git_report(path: Path, *, fetch: bool = False, dirty_limit: int = 20) -> GitReport:
    report = GitReport(path=str(path), exists=path.exists(), is_git_repo=False, dirty_paths=[])
    if not path.exists():
        report.error = "path does not exist"
        return report

    inside = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=path)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        report.error = inside.stderr.strip() or "not a git repository"
        return report
    report.is_git_repo = True

    if fetch:
        fetched = run(["git", "fetch", "--all", "--prune"], cwd=path, timeout=120)
        if fetched.returncode != 0:
            report.error = fetched.stderr.strip() or fetched.stdout.strip() or "git fetch failed"

    status = run(["git", "status", "--short", "--branch"], cwd=path)
    if status.returncode == 0:
        lines = status.stdout.splitlines()
        report.branch_status = lines[0] if lines else ""
        dirty = [line for line in lines[1:] if line.strip()]
        report.dirty_count = len(dirty)
        report.dirty_paths = dirty[:dirty_limit]

    counts = run(["git", "rev-list", "--left-right", "--count", "HEAD...origin/main"], cwd=path)
    if counts.returncode == 0:
        report.ahead, report.behind = parse_left_right_count(counts.stdout)

    tag = run(["git", "tag", "--sort=-creatordate"], cwd=path)
    if tag.returncode == 0:
        report.latest_tag = first_nonempty_line(tag.stdout)

    head = run(["git", "rev-parse", "--short", "HEAD"], cwd=path)
    if head.returncode == 0:
        report.head = head.stdout.strip()

    return report


def hermes_cli_report() -> HermesCliReport:
    hermes_bin = shutil.which("hermes")
    if not hermes_bin:
        return HermesCliReport(hermes_bin=None, first_line="", update_line="", error="hermes not found on PATH")
    try:
        result = run([hermes_bin, "--version"], timeout=40)
    except subprocess.TimeoutExpired:
        return HermesCliReport(hermes_bin=hermes_bin, first_line="", update_line="", error="hermes --version timed out")
    text = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    update_line = ""
    for line in text.splitlines():
        if "Update available" in line:
            update_line = line.strip()
            break
    return HermesCliReport(
        hermes_bin=hermes_bin,
        first_line=first_nonempty_line(text),
        update_line=update_line,
        error="" if result.returncode == 0 else text.strip(),
    )


def build_recommendations(harness: GitReport, hermes_agent: Optional[GitReport], cli: HermesCliReport) -> List[str]:
    recommendations: List[str] = []
    if harness.behind:
        recommendations.append("Harness repo is behind origin/main; review upstream before editing method docs.")
    if harness.dirty_count:
        recommendations.append("Harness repo has local changes; keep method-sync edits companion-surface complete before committing.")
    if hermes_agent is None:
        recommendations.append("No Hermes Agent source repo detected; pass --hermes-agent-root when reviewing runtime deltas.")
    else:
        if hermes_agent.behind:
            recommendations.append(
                f"Hermes Agent source is behind origin/main by {hermes_agent.behind} commits; inspect release notes before adopting runtime-specific methods."
            )
        if hermes_agent.dirty_count:
            recommendations.append(
                "Hermes Agent source has uncommitted work; do not run hermes update or rebase until those changes are reviewed/stashed."
            )
    if cli.update_line:
        recommendations.append(cli.update_line)
    if not recommendations:
        recommendations.append("No obvious update pressure detected; continue normal harness maintenance review.")
    return recommendations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Hermes/Harness update sources for method-sync reviews.")
    parser.add_argument("--repo", default=".", help="Harness reference repo path. Defaults to current directory.")
    parser.add_argument("--hermes-agent-root", default="", help="Local Hermes Agent source repo path.")
    parser.add_argument("--fetch", action="store_true", help="Run git fetch --all --prune before reporting.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    harness_path = Path(args.repo).expanduser().resolve()
    hermes_root = detect_hermes_agent_root(args.hermes_agent_root)

    harness = git_report(harness_path, fetch=args.fetch)
    hermes_agent = git_report(hermes_root, fetch=args.fetch) if hermes_root else None
    cli = hermes_cli_report()
    report = MethodUpdateReport(
        harness_repo=harness,
        hermes_agent_repo=hermes_agent,
        hermes_cli=cli,
        recommendations=build_recommendations(harness, hermes_agent, cli),
    )

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
        return 0

    print("Hermes/Harness Method Update Sources")
    print(f"- harness: {harness.branch_status or harness.path}")
    if harness.ahead is not None and harness.behind is not None:
        print(f"  ahead/behind origin/main: {harness.ahead}/{harness.behind}")
    print(f"  dirty files: {harness.dirty_count}")
    if hermes_agent:
        print(f"- hermes-agent: {hermes_agent.branch_status or hermes_agent.path}")
        if hermes_agent.ahead is not None and hermes_agent.behind is not None:
            print(f"  ahead/behind origin/main: {hermes_agent.ahead}/{hermes_agent.behind}")
        print(f"  latest tag: {hermes_agent.latest_tag or 'unknown'}")
        print(f"  dirty files: {hermes_agent.dirty_count}")
    else:
        print("- hermes-agent: not detected")
    print(f"- hermes cli: {cli.first_line or cli.error or 'unknown'}")
    if cli.update_line:
        print(f"  {cli.update_line}")
    print("Recommendations:")
    for item in report.recommendations:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
