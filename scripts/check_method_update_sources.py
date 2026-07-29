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
import re
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

MAX_EXTERNAL_FILE_BYTES = 1024 * 1024


@dataclass
class GitReport:
    path: str
    exists: bool
    is_git_repo: bool
    branch_status: str = ""
    comparison_ref: str = ""
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
    source_id: str = "agent-skills"
    adapter: str = "generic"
    skill_count: int = 0
    command_count: int = 0
    persona_count: int = 0
    hook_count: int = 0
    reference_count: int = 0
    license: str = ""
    invalid_skills: Optional[List[str]] = None
    bucket_counts: Optional[Dict[str, int]] = None
    promoted_skill_count: int = 0
    plugin_skill_count: int = 0
    user_invoked_skill_count: int = 0
    model_invoked_skill_count: int = 0
    openai_metadata_count: int = 0
    missing_openai_metadata: Optional[List[str]] = None
    missing_plugin_skills: Optional[List[str]] = None
    missing_promoted_docs: Optional[List[str]] = None
    invalid_invocation_policies: Optional[List[str]] = None
    plugin_version: str = ""
    package_version: str = ""
    version_mismatch: bool = False
    version_status: str = "absent"
    manifest_errors: Optional[List[str]] = None
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


def safe_read_external_text(
    path: Path,
    *,
    root: Path,
    max_bytes: int = MAX_EXTERNAL_FILE_BYTES,
) -> Tuple[Optional[str], Optional[str]]:
    """Read a bounded regular file that is physically contained in an external pack."""
    if path.is_symlink():
        return None, "symlink is not allowed"
    if not path.exists():
        return None, None
    try:
        root_resolved = root.resolve(strict=True)
        resolved = path.resolve(strict=True)
        resolved.relative_to(root_resolved)
        if not resolved.is_file():
            return None, "not a regular file"
        size = resolved.stat().st_size
        if size > max_bytes:
            return None, f"file size {size} exceeds {max_bytes} bytes"
        return resolved.read_text(encoding="utf-8"), None
    except ValueError:
        return None, "path escapes workflow-pack root"
    except (OSError, UnicodeError, RuntimeError) as exc:
        return None, str(exc)


def append_error(current: str, message: str) -> str:
    return "; ".join(item for item in [current, message] if item)


def count_external_files(
    directory: Path,
    *,
    root: Path,
    pattern: str,
    excluded_names: Optional[set[str]] = None,
) -> Tuple[int, Optional[str]]:
    if directory.is_symlink():
        return 0, "symlink directory is not allowed"
    if not directory.exists():
        return 0, None
    if not os.access(directory, os.R_OK | os.X_OK):
        return 0, "directory is not readable"
    try:
        directory.resolve(strict=True).relative_to(root.resolve(strict=True))
        files = [
            candidate
            for candidate in directory.glob(pattern)
            if candidate.is_file()
            and not candidate.is_symlink()
            and candidate.name not in (excluded_names or set())
        ]
        return len(files), None
    except ValueError:
        return 0, "directory escapes workflow-pack root"
    except (OSError, RuntimeError) as exc:
        return 0, str(exc)


def detect_license(path: Path, errors: Optional[List[str]] = None) -> str:
    for name in ["LICENSE", "LICENSE.md", "COPYING"]:
        license_path = path / name
        if not license_path.exists() and not license_path.is_symlink():
            continue
        text, error = safe_read_external_text(license_path, root=path)
        if error:
            if errors is not None:
                errors.append(f"{name}: {error}")
            continue
        assert text is not None
        text = text[:2000].lower()
        if "mit license" in text:
            return "MIT"
        if "apache license" in text:
            return "Apache"
        if "bsd" in text:
            return "BSD"
        return first_nonempty_line(text) or "present"
    return ""


def skill_frontmatter_fields(
    skill_file: Path, *, root: Path
) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    if not skill_file.exists() and not skill_file.is_symlink():
        return None, "missing SKILL.md"
    text, read_error = safe_read_external_text(skill_file, root=root)
    if read_error:
        return None, read_error
    assert text is not None
    if not text.startswith("---\n"):
        return None, "missing frontmatter"
    try:
        _, frontmatter, _ = text.split("---", 2)
    except ValueError:
        return None, "malformed frontmatter"
    fields: Dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields, None


def validate_skill_file(skill_dir: Path, *, root: Path) -> Optional[str]:
    skill_file = skill_dir / "SKILL.md"
    fields, error = skill_frontmatter_fields(skill_file, root=root)
    if error:
        return f"{skill_dir.name}: {error}"
    assert fields is not None
    if fields.get("name") != skill_dir.name:
        return f"{skill_dir.name}: name mismatch"
    if not fields.get("description"):
        return f"{skill_dir.name}: missing description"
    invocation_value = fields.get("disable-model-invocation")
    if invocation_value is not None and invocation_value.lower() not in {"true", "false"}:
        return f"{skill_dir.name}: disable-model-invocation must be true or false"
    return None


def read_json_mapping(path: Path, *, root: Path) -> Tuple[Optional[Dict[str, object]], Optional[str]]:
    if not path.exists() and not path.is_symlink():
        return None, None
    text, read_error = safe_read_external_text(path, root=root)
    if read_error:
        return None, read_error
    assert text is not None
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, str(exc)
    if not isinstance(value, dict):
        return None, "top-level JSON value is not an object"
    return value, None


def normalize_manifest_skill_path(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/")


def manifest_skill_path_is_safe(root: Path, value: str) -> bool:
    relative = Path(value)
    if not value or relative.is_absolute() or not relative.parts or relative.parts[0] != "skills":
        return False
    if ".." in relative.parts:
        return False
    try:
        skills_root = (root / "skills").resolve()
        candidate = (root / relative).resolve()
        candidate.relative_to(skills_root)
    except (ValueError, OSError, RuntimeError):
        return False
    return candidate != skills_root


def workflow_pack_adapter(
    plugin: Optional[Dict[str, object]], package: Optional[Dict[str, object]]
) -> str:
    names = {
        value
        for mapping in (plugin, package)
        if mapping
        for value in [mapping.get("name")]
        if isinstance(value, str)
    }
    return "mattpocock" if "mattpocock-skills" in names else "generic"


def parse_openai_invocation_policy(
    path: Path, *, root: Path
) -> Tuple[Optional[bool], Optional[str]]:
    """Return whether OpenAI metadata requires explicit invocation.

    Missing `allow_implicit_invocation` means the default model-invoked policy.
    Only the constrained boolean field is parsed; comments are ignored.
    """
    values: List[bool] = []
    text, read_error = safe_read_external_text(path, root=root)
    if read_error:
        return None, read_error
    assert text is not None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or not re.match(r"^allow_implicit_invocation\s*:", line):
            continue
        raw_value = line.split(":", 1)[1].strip().lower()
        if raw_value not in {"true", "false"}:
            return None, "allow_implicit_invocation must be true or false"
        values.append(raw_value == "false")
    if len(values) > 1:
        return None, "duplicate allow_implicit_invocation values"
    return (values[0] if values else False), None


def optional_json_string(
    mapping: Optional[Dict[str, object]],
    key: str,
    label: str,
    errors: List[str],
) -> str:
    if not mapping or key not in mapping or mapping[key] is None:
        return ""
    value = mapping[key]
    if not isinstance(value, str):
        errors.append(f"{label}: {key} must be a string")
        return ""
    return value


def agent_skills_report(path: Path, *, source_id: str = "agent-skills") -> AgentSkillsReport:
    report = AgentSkillsReport(
        path=str(path),
        exists=path.exists(),
        source_id=source_id,
        invalid_skills=[],
        bucket_counts={},
        missing_openai_metadata=[],
        missing_plugin_skills=[],
        missing_promoted_docs=[],
        invalid_invocation_policies=[],
        manifest_errors=[],
    )
    if not path.exists():
        report.error = "path does not exist"
        return report

    assert report.manifest_errors is not None
    plugin_manifest = path / ".claude-plugin" / "plugin.json"
    plugin, plugin_error = read_json_mapping(plugin_manifest, root=path)
    if plugin_error:
        report.manifest_errors.append(f".claude-plugin/plugin.json: {plugin_error}")

    package, package_error = read_json_mapping(path / "package.json", root=path)
    if package_error:
        report.manifest_errors.append(f"package.json: {package_error}")

    report.adapter = workflow_pack_adapter(plugin, package)
    report.plugin_version = optional_json_string(
        plugin, "version", ".claude-plugin/plugin.json", report.manifest_errors
    )
    report.package_version = optional_json_string(
        package, "version", "package.json", report.manifest_errors
    )
    if report.plugin_version and report.package_version:
        report.version_status = "match" if report.plugin_version == report.package_version else "mismatch"
    elif report.plugin_version or report.package_version:
        report.version_status = "partial"
    report.version_mismatch = report.version_status == "mismatch"

    metadata_skills: set[str] = set()
    skills_dir = path / "skills"
    if skills_dir.is_symlink():
        report.error = append_error(report.error, "cannot inspect skills directory: symlink is not allowed")
    elif skills_dir.exists():
        try:
            direct_skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
            discovered_skill_files = sorted(p for p in skills_dir.rglob("SKILL.md") if p.is_file())
        except (OSError, RuntimeError) as exc:
            report.error = append_error(report.error, f"cannot inspect skills directory: {exc}")
            direct_skill_dirs = []
            discovered_skill_files = []
        nested_layout = report.adapter == "mattpocock" or any(
            len(skill_file.relative_to(skills_dir).parts) > 2 for skill_file in discovered_skill_files
        )
        flat_layout = not nested_layout
        if flat_layout:
            skill_dirs = direct_skill_dirs
        else:
            skill_dirs = sorted(p.parent for p in discovered_skill_files)
        report.skill_count = len(skill_dirs)
        report.invalid_skills = [
            issue for skill in skill_dirs if (issue := validate_skill_file(skill, root=path))
        ]
        for skill_dir in skill_dirs:
            relative_parts = skill_dir.relative_to(skills_dir).parts
            bucket = relative_parts[0] if len(relative_parts) > 1 else "flat"
            assert report.bucket_counts is not None
            report.bucket_counts[bucket] = report.bucket_counts.get(bucket, 0) + 1

            fields, fields_error = skill_frontmatter_fields(skill_dir / "SKILL.md", root=path)
            if fields_error or fields is None:
                continue
            invocation_value = fields.get("disable-model-invocation", "false").lower()
            if invocation_value not in {"true", "false"}:
                continue
            user_invoked = invocation_value == "true"
            relative_skill = skill_dir.relative_to(path).as_posix()
            if user_invoked:
                report.user_invoked_skill_count += 1
            else:
                report.model_invoked_skill_count += 1

            openai_metadata = skill_dir / "agents" / "openai.yaml"
            if openai_metadata.exists() or openai_metadata.is_symlink():
                report.openai_metadata_count += 1
                metadata_skills.add(relative_skill)
                openai_user_invoked, metadata_error = parse_openai_invocation_policy(
                    openai_metadata, root=path
                )
                assert report.invalid_invocation_policies is not None
                if metadata_error:
                    report.invalid_invocation_policies.append(
                        f"{relative_skill}/agents/openai.yaml: {metadata_error}"
                    )
                elif user_invoked and not openai_user_invoked:
                    assert report.invalid_invocation_policies is not None
                    report.invalid_invocation_policies.append(
                        f"{relative_skill}: Claude user-invoked policy is not mirrored in agents/openai.yaml"
                    )
                elif not user_invoked and openai_user_invoked:
                    assert report.invalid_invocation_policies is not None
                    report.invalid_invocation_policies.append(
                        f"{relative_skill}: agents/openai.yaml disables implicit invocation but SKILL.md does not"
                    )

    plugin_skills: List[str] = []
    if plugin:
        raw_plugin_skills = plugin.get("skills", [])
        if not isinstance(raw_plugin_skills, list) or not all(isinstance(item, str) for item in raw_plugin_skills):
            report.manifest_errors.append(".claude-plugin/plugin.json: skills must be a list of paths")
            raw_plugin_skills = []
        seen_plugin_skills: set[str] = set()
        for item in raw_plugin_skills:
            normalized = normalize_manifest_skill_path(item)
            if normalized in seen_plugin_skills:
                report.manifest_errors.append(
                    f".claude-plugin/plugin.json: duplicate skill path: {normalized}"
                )
                continue
            seen_plugin_skills.add(normalized)
            if not manifest_skill_path_is_safe(path, normalized):
                report.manifest_errors.append(f".claude-plugin/plugin.json: unsafe skill path: {item}")
                continue
            plugin_skills.append(normalized)
        report.plugin_skill_count = len(raw_plugin_skills)
        report.promoted_skill_count = len(plugin_skills)
        for relative_skill in plugin_skills:
            skill_dir = path / relative_skill
            if not (skill_dir / "SKILL.md").is_file():
                assert report.missing_plugin_skills is not None
                report.missing_plugin_skills.append(relative_skill)
                continue
            parts = Path(relative_skill).parts
            if (
                report.adapter == "mattpocock"
                and len(parts) >= 3
                and parts[0] == "skills"
                and parts[1] in {"engineering", "productivity"}
            ):
                docs_path = Path("docs") / parts[1] / f"{parts[-1]}.md"
                if not (path / docs_path).is_file():
                    assert report.missing_promoted_docs is not None
                    report.missing_promoted_docs.append(docs_path.as_posix())

        existing_promoted = [
            relative_skill
            for relative_skill in plugin_skills
            if (path / relative_skill / "SKILL.md").is_file()
        ]
        promoted_with_metadata = [skill for skill in existing_promoted if skill in metadata_skills]
        if promoted_with_metadata and len(promoted_with_metadata) < len(existing_promoted):
            assert report.missing_openai_metadata is not None
            report.missing_openai_metadata = [
                f"{skill}/agents/openai.yaml"
                for skill in existing_promoted
                if skill not in metadata_skills
            ]

    commands_dir = path / ".claude" / "commands"
    report.command_count, count_error = count_external_files(
        commands_dir, root=path, pattern="*.md"
    )
    if count_error:
        report.error = append_error(report.error, f"cannot inspect .claude/commands: {count_error}")

    agents_dir = path / "agents"
    report.persona_count, count_error = count_external_files(
        agents_dir, root=path, pattern="*.md", excluded_names={"README.md"}
    )
    if count_error:
        report.error = append_error(report.error, f"cannot inspect agents: {count_error}")

    hooks_dir = path / "hooks"
    report.hook_count, count_error = count_external_files(hooks_dir, root=path, pattern="*")
    if count_error:
        report.error = append_error(report.error, f"cannot inspect hooks: {count_error}")

    references_dir = path / "references"
    report.reference_count, count_error = count_external_files(
        references_dir, root=path, pattern="*.md"
    )
    if count_error:
        report.error = append_error(report.error, f"cannot inspect references: {count_error}")

    report.license = detect_license(path, report.manifest_errors)
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

    branch = run(["git", "symbolic-ref", "--quiet", "--short", "HEAD"], cwd=path)
    if branch.returncode == 0:
        upstream = run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
            cwd=path,
        )
        if upstream.returncode == 0:
            report.comparison_ref = upstream.stdout.strip()
    else:
        exact_tag = run(["git", "describe", "--tags", "--exact-match", "HEAD"], cwd=path)
        if exact_tag.returncode == 0:
            report.comparison_ref = first_nonempty_line(exact_tag.stdout)

    if not report.comparison_ref:
        remote_head = run(
            ["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"],
            cwd=path,
        )
        if remote_head.returncode == 0:
            report.comparison_ref = remote_head.stdout.strip()

    if report.comparison_ref:
        counts = run(
            ["git", "rev-list", "--left-right", "--count", f"HEAD...{report.comparison_ref}"],
            cwd=path,
        )
        if counts.returncode == 0:
            report.ahead, report.behind = parse_left_right_count(counts.stdout)
        else:
            detail = counts.stderr.strip() or counts.stdout.strip() or "comparison failed"
            report.error = "; ".join(
                item for item in [report.error, f"cannot compare HEAD with {report.comparison_ref}: {detail}"] if item
            )
    else:
        report.error = "; ".join(
            item
            for item in [
                report.error,
                "unable to determine Git comparison ref from @{upstream}, an exact HEAD tag, or origin/HEAD",
            ]
            if item
        )

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
        recommendations.append(
            f"Harness repo is behind {harness.comparison_ref or 'its upstream'}; review upstream before editing method docs."
        )
    if harness.error:
        recommendations.append(f"Harness Git comparison is incomplete: {harness.error}")
    if harness.dirty_count:
        recommendations.append("Harness repo has local changes; keep method-sync edits companion-surface complete before committing.")
    if hermes_agent is None:
        recommendations.append("No Hermes Agent source repo detected; pass --hermes-agent-root when reviewing runtime deltas.")
    else:
        if hermes_agent.behind:
            recommendations.append(
                f"Hermes Agent source is behind {hermes_agent.comparison_ref or 'its upstream'} by {hermes_agent.behind} commits; inspect release notes before adopting runtime-specific methods."
            )
        if hermes_agent.error:
            recommendations.append(f"Hermes Agent Git comparison is incomplete: {hermes_agent.error}")
        if hermes_agent.dirty_count:
            recommendations.append(
                "Hermes Agent source has uncommitted work; do not run hermes update or rebase until those changes are reviewed/stashed."
            )
    if agent_skills_repo is not None:
        if agent_skills_repo.behind:
            source_id = agent_skills.source_id if agent_skills else "agent-skills"
            recommendations.append(
                f"{source_id} source is behind {agent_skills_repo.comparison_ref or 'its upstream'} by {agent_skills_repo.behind} commits; review new workflows before updating crosswalks."
            )
        if agent_skills_repo.error:
            source_id = agent_skills.source_id if agent_skills else "agent-skills"
            recommendations.append(f"{source_id} Git comparison is incomplete: {agent_skills_repo.error}")
        if agent_skills_repo.dirty_count:
            source_id = agent_skills.source_id if agent_skills else "agent-skills"
            recommendations.append(f"{source_id} source has local changes; avoid treating it as a clean upstream snapshot.")
    if agent_skills is not None:
        source_id = agent_skills.source_id
        if agent_skills.license and agent_skills.license != "MIT":
            recommendations.append(f"{source_id} license is {agent_skills.license}; review license before copying content.")
        if agent_skills.invalid_skills:
            recommendations.append(f"{source_id} has invalid skill metadata: {agent_skills.invalid_skills[:5]}")
        if agent_skills.missing_plugin_skills:
            recommendations.append(f"{source_id} plugin references missing skills: {agent_skills.missing_plugin_skills[:5]}")
        if agent_skills.missing_promoted_docs:
            recommendations.append(f"{source_id} promoted skills are missing docs: {agent_skills.missing_promoted_docs[:5]}")
        if agent_skills.missing_openai_metadata:
            recommendations.append(
                f"{source_id} has partial OpenAI metadata coverage: {agent_skills.missing_openai_metadata[:5]}"
            )
        if agent_skills.invalid_invocation_policies:
            recommendations.append(
                f"{source_id} has invocation-policy drift: {agent_skills.invalid_invocation_policies[:5]}"
            )
        if agent_skills.version_mismatch:
            recommendations.append(
                f"{source_id} package/plugin versions differ: {agent_skills.package_version} vs {agent_skills.plugin_version}; pin a reviewed tag or commit."
            )
        if agent_skills.manifest_errors:
            recommendations.append(f"{source_id} has invalid manifests: {agent_skills.manifest_errors[:5]}")
        if agent_skills.hook_count:
            recommendations.append(f"{source_id} contains hooks/plugin packaging; adapt methods into harness docs instead of adopting hooks directly.")
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
    parser.add_argument(
        "--workflow-pack-root",
        default="",
        help="Local external workflow/skill pack path. Report remains under the backward-compatible agent_skills JSON key.",
    )
    parser.add_argument(
        "--workflow-pack-id",
        default="external-workflow-pack",
        help="Stable source identifier used in reports with --workflow-pack-root.",
    )
    parser.add_argument("--fetch", action="store_true", help="Run git fetch --all --prune before reporting.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()
    if args.agent_skills_root and args.workflow_pack_root:
        parser.error("--agent-skills-root and --workflow-pack-root are mutually exclusive")
    return args


def main() -> int:
    args = parse_args()
    harness_path = Path(args.repo).expanduser().resolve()
    hermes_root = detect_hermes_agent_root(args.hermes_agent_root)
    explicit_workflow_root = args.workflow_pack_root or args.agent_skills_root
    agent_skills_root = detect_agent_skills_root(explicit_workflow_root)
    workflow_pack_id = args.workflow_pack_id if args.workflow_pack_root else "agent-skills"

    harness = git_report(harness_path, fetch=args.fetch)
    hermes_agent = git_report(hermes_root, fetch=args.fetch) if hermes_root else None
    agent_skills_repo = git_report(agent_skills_root, fetch=args.fetch) if agent_skills_root else None
    agent_skills = agent_skills_report(agent_skills_root, source_id=workflow_pack_id) if agent_skills_root else None
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
        print(f"  ahead/behind {harness.comparison_ref}: {harness.ahead}/{harness.behind}")
    if harness.error:
        print(f"  git comparison error: {harness.error}")
    print(f"  dirty files: {harness.dirty_count}")
    if hermes_agent:
        print(f"- hermes-agent: {hermes_agent.branch_status or hermes_agent.path}")
        if hermes_agent.ahead is not None and hermes_agent.behind is not None:
            print(
                f"  ahead/behind {hermes_agent.comparison_ref}: "
                f"{hermes_agent.ahead}/{hermes_agent.behind}"
            )
        if hermes_agent.error:
            print(f"  git comparison error: {hermes_agent.error}")
        print(f"  latest tag: {hermes_agent.latest_tag or 'unknown'}")
        print(f"  dirty files: {hermes_agent.dirty_count}")
    else:
        print("- hermes-agent: not detected")
    if agent_skills:
        branch_status = agent_skills_repo.branch_status if agent_skills_repo else agent_skills.path
        print(f"- {agent_skills.source_id}: {branch_status}")
        print(f"  adapter: {agent_skills.adapter}")
        if agent_skills_repo and agent_skills_repo.ahead is not None and agent_skills_repo.behind is not None:
            print(
                f"  ahead/behind {agent_skills_repo.comparison_ref}: "
                f"{agent_skills_repo.ahead}/{agent_skills_repo.behind}"
            )
        if agent_skills_repo and agent_skills_repo.error:
            print(f"  git comparison error: {agent_skills_repo.error}")
        print(
            "  surfaces: "
            f"skills={agent_skills.skill_count}, "
            f"promoted={agent_skills.promoted_skill_count}, "
            f"commands={agent_skills.command_count}, "
            f"personas={agent_skills.persona_count}, "
            f"hooks={agent_skills.hook_count}, "
            f"references={agent_skills.reference_count}"
        )
        if agent_skills.bucket_counts:
            print(f"  skill buckets: {agent_skills.bucket_counts}")
        if agent_skills.openai_metadata_count:
            print(
                "  invocation: "
                f"user={agent_skills.user_invoked_skill_count}, "
                f"model={agent_skills.model_invoked_skill_count}, "
                f"openai_metadata={agent_skills.openai_metadata_count}"
            )
        if agent_skills.plugin_version or agent_skills.package_version:
            print(
                "  versions: "
                f"package={agent_skills.package_version or 'unknown'}, "
                f"plugin={agent_skills.plugin_version or 'unknown'}, "
                f"status={agent_skills.version_status}"
            )
        print(f"  license: {agent_skills.license or 'unknown'}")
        if agent_skills.invalid_skills:
            print(f"  invalid skills: {agent_skills.invalid_skills}")
        if agent_skills.missing_plugin_skills:
            print(f"  missing plugin skills: {agent_skills.missing_plugin_skills}")
        if agent_skills.missing_promoted_docs:
            print(f"  missing promoted docs: {agent_skills.missing_promoted_docs}")
        if agent_skills.missing_openai_metadata:
            print(f"  missing OpenAI metadata: {agent_skills.missing_openai_metadata}")
        if agent_skills.invalid_invocation_policies:
            print(f"  invocation-policy drift: {agent_skills.invalid_invocation_policies}")
        if agent_skills.manifest_errors:
            print(f"  manifest errors: {agent_skills.manifest_errors}")
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
