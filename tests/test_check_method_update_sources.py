import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "check_method_update_sources.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_method_update_sources", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_left_right_count_reads_ahead_and_behind():
    mod = _load_module()
    assert mod.parse_left_right_count("0\t1778\n") == (0, 1778)
    assert mod.parse_left_right_count("3 4") == (3, 4)


def test_parse_left_right_count_rejects_malformed_input():
    mod = _load_module()
    assert mod.parse_left_right_count("") == (None, None)
    assert mod.parse_left_right_count("abc 4") == (None, None)


def test_first_nonempty_line_skips_blank_lines():
    mod = _load_module()
    assert mod.first_nonempty_line("\n\nHermes Agent v0.9.0\nUpdate available") == "Hermes Agent v0.9.0"


def test_build_recommendations_warns_before_runtime_update_when_dirty():
    mod = _load_module()
    harness = mod.GitReport(path="repo", exists=True, is_git_repo=True, dirty_count=0, ahead=0, behind=0)
    hermes = mod.GitReport(path="hermes", exists=True, is_git_repo=True, dirty_count=2, ahead=0, behind=1778)
    cli = mod.HermesCliReport(hermes_bin="hermes", first_line="Hermes Agent v0.9.0", update_line="Update available: 1778 commits behind")

    recommendations = mod.build_recommendations(harness, hermes, cli)

    assert any("behind origin/main by 1778" in item for item in recommendations)
    assert any("do not run hermes update" in item for item in recommendations)
    assert "Update available: 1778 commits behind" in recommendations


def test_detect_agent_skills_root_honors_explicit_path(tmp_path):
    mod = _load_module()
    root = tmp_path / "agent-skills"
    root.mkdir()

    assert mod.detect_agent_skills_root(str(root)) == root


def test_agent_skills_report_counts_pack_surfaces(tmp_path):
    mod = _load_module()
    root = tmp_path / "agent-skills"
    (root / "skills" / "spec-driven-development").mkdir(parents=True)
    (root / "skills" / "spec-driven-development" / "SKILL.md").write_text(
        "---\nname: spec-driven-development\ndescription: Creates specs before coding. Use when starting a feature.\n---\n",
        encoding="utf-8",
    )
    (root / ".claude" / "commands").mkdir(parents=True)
    (root / ".claude" / "commands" / "spec.md").write_text("/spec", encoding="utf-8")
    (root / "agents").mkdir()
    (root / "agents" / "code-reviewer.md").write_text("# reviewer", encoding="utf-8")
    (root / "hooks").mkdir()
    (root / "hooks" / "session-start.sh").write_text("#!/bin/bash\n", encoding="utf-8")
    (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")

    report = mod.agent_skills_report(root)

    assert report.exists is True
    assert report.skill_count == 1
    assert report.command_count == 1
    assert report.persona_count == 1
    assert report.hook_count == 1
    assert report.license == "MIT"
    assert report.invalid_skills == []
