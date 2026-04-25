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

DEFAULT_AGENT_SKILLS_CANDIDATES = [
    Path("~/yr/code/harness-engineering-all/agent-skills").expanduser(),
    Path("~/code/harness-engineering-all/agent-skills").expanduser(),
    Path("~/yr/code/agent-skills").expanduser(),
    Path("~/code/agent-skills").expanduser(),
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
class AgentSkillsReport:
    path: str
    exists: bool
    skill_count: int = 0
    command_count: int = 0
    persona_count: int = 0
    hook_count: int = 0
    reference_count: int = 0
    license: str = ""
    invalid_skills: Optional[List[str]] = None
    error: str = ""


@dataclass
class MethodUpdateReport:
    harness_repo: GitReport
    hermes_agent_repo: Optional[GitReport]
    hermes_cli: HermesCliReport
    agent_skills_repo: Optional[GitReport]
    agent_skills: Optional[AgentSkillsReport]
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


def detect_agent_skills_root(explicit: str) -> Optional[Path]:
    if explicit:
        return Path(explicit).expanduser()
    env_root = os.getenv("AGENT_SKILLS_SOURCE_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser()
    for candidate in DEFAULT_AGENT_SKILLS_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def detect_license(path: Path) -> str:
    for name in ["LICENSE", "LICENSE.md", "COPYING"]:
        license_path = path / name
        if not license_path.exists():
            continue
        text = license_path.read_text(encoding="utf-8", errors="replace")[:2000].lower()
        if "mit license" in text:
            return "MIT"
        if "apache license" in text:
            return "Apache"
        if "bsd" in text:
            return "BSD"
        return first_nonempty_line(text) or "present"
    return ""


def validate_skill_file(skill_dir: Path) -> Optional[str]:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return f"{skill_dir.name}: missing SKILL.md"
    text = skill_file.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n"):
        return f"{skill_dir.name}: missing frontmatter"
    try:
        _, frontmatter, _ = text.split("---", 2)
    except ValueError:
        return f"{skill_dir.name}: malformed frontmatter"
    fields: Dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    if fields.get("name") != skill_dir.name:
        return f"{skill_dir.name}: name mismatch"
    if not fields.get("description"):
        return f"{skill_dir.name}: missing description"
    return None


def agent_skills_report(path: Path) -> AgentSkillsReport:
    report = AgentSkillsReport(path=str(path), exists=path.exists(), invalid_skills=[])
    if not path.exists():
        report.error = "path does not exist"
        return report

    skills_dir = path / "skills"
    if skills_dir.exists():
        skill_dirs = [p for p in skills_dir.iterdir() if p.is_dir()]
        report.skill_count = len(skill_dirs)
        report.invalid_skills = [issue for skill in skill_dirs if (issue := validate_skill_file(skill))]

    commands_dir = path / ".claude" / "commands"
    if commands_dir.exists():
        report.command_count = len([p for p in commands_dir.glob("*.md") if p.is_file()])

    agents_dir = path / "agents"
    if agents_dir.exists():
        report.persona_count = len([p for p in agents_dir.glob("*.md") if p.is_file() and p.name != "README.md"])

    hooks_dir = path / "hooks"
    if hooks_dir.exists():
        report.hook_count = len([p for p in hooks_dir.iterdir() if p.is_file()])

    references_dir = path / "references"
    if references_dir.exists():
        report.reference_count = len([p for p in references_dir.glob("*.md") if p.is_file()])

    report.license = detect_license(path)
    return report


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


def build_recommendations(
    harness: GitReport,
    hermes_agent: Optional[GitReport],
    cli: HermesCliReport,
    agent_skills_repo: Optional[GitReport] = None,
    agent_skills: Optional[AgentSkillsReport] = None,
) -> List[str]:
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
    if agent_skills_repo is not None:
        if agent_skills_repo.behind:
            recommendations.append(
                f"agent-skills source is behind origin/main by {agent_skills_repo.behind} commits; review new workflows before updating crosswalks."
            )
        if agent_skills_repo.dirty_count:
            recommendations.append("agent-skills source has local changes; avoid treating it as a clean upstream snapshot.")
    if agent_skills is not None:
        if agent_skills.license and agent_skills.license != "MIT":
            recommendations.append(f"agent-skills license is {agent_skills.license}; review license before copying content.")
        if agent_skills.invalid_skills:
            recommendations.append(f"agent-skills has invalid skill metadata: {agent_skills.invalid_skills[:5]}")
        if agent_skills.hook_count:
            recommendations.append("agent-skills contains hooks/plugin packaging; adapt methods into harness docs instead of adopting hooks directly.")
    if cli.update_line:
        recommendations.append(cli.update_line)
    if not recommendations:
        recommendations.append("No obvious update pressure detected; continue normal harness maintenance review.")
    return recommendations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Hermes/Harness update sources for method-sync reviews.")
    parser.add_argument("--repo", default=".", help="Harness reference repo path. Defaults to current directory.")
    parser.add_argument("--hermes-agent-root", default="", help="Local Hermes Agent source repo path.")
    parser.add_argument("--agent-skills-root", default="", help="Local addyosmani/agent-skills source repo path.")
    parser.add_argument("--fetch", action="store_true", help="Run git fetch --all --prune before reporting.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    harness_path = Path(args.repo).expanduser().resolve()
    hermes_root = detect_hermes_agent_root(args.hermes_agent_root)
    agent_skills_root = detect_agent_skills_root(args.agent_skills_root)

    harness = git_report(harness_path, fetch=args.fetch)
    hermes_agent = git_report(hermes_root, fetch=args.fetch) if hermes_root else None
    agent_skills_repo = git_report(agent_skills_root, fetch=args.fetch) if agent_skills_root else None
    agent_skills = agent_skills_report(agent_skills_root) if agent_skills_root else None
    cli = hermes_cli_report()
    report = MethodUpdateReport(
        harness_repo=harness,
        hermes_agent_repo=hermes_agent,
        hermes_cli=cli,
        agent_skills_repo=agent_skills_repo,
        agent_skills=agent_skills,
        recommendations=build_recommendations(harness, hermes_agent, cli, agent_skills_repo, agent_skills),
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
    if agent_skills:
        branch_status = agent_skills_repo.branch_status if agent_skills_repo else agent_skills.path
        print(f"- agent-skills: {branch_status}")
        if agent_skills_repo and agent_skills_repo.ahead is not None and agent_skills_repo.behind is not None:
            print(f"  ahead/behind origin/main: {agent_skills_repo.ahead}/{agent_skills_repo.behind}")
        print(
            "  surfaces: "
            f"skills={agent_skills.skill_count}, "
            f"commands={agent_skills.command_count}, "
            f"personas={agent_skills.persona_count}, "
            f"hooks={agent_skills.hook_count}, "
            f"references={agent_skills.reference_count}"
        )
        print(f"  license: {agent_skills.license or 'unknown'}")
        if agent_skills.invalid_skills:
            print(f"  invalid skills: {agent_skills.invalid_skills}")
    else:
        print("- agent-skills: not detected")
    print(f"- hermes cli: {cli.first_line or cli.error or 'unknown'}")
    if cli.update_line:
        print(f"  {cli.update_line}")
    print("Recommendations:")
    for item in report.recommendations:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
