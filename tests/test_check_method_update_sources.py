import importlib.util
import subprocess
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


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _committed_repo(path: Path, branch: str = "master") -> Path:
    path.mkdir()
    _git(path, "init", "-b", branch)
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test User")
    (path / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(path, "add", "README.md")
    _git(path, "commit", "-m", "fixture")
    return path


def _track_remote(repo: Path, remote: Path, *, name: str, branch: str) -> None:
    remote.mkdir()
    _git(remote, "init", "--bare")
    _git(repo, "remote", "add", name, str(remote))
    _git(repo, "push", "--set-upstream", name, branch)


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
    hermes = mod.GitReport(
        path="hermes",
        exists=True,
        is_git_repo=True,
        dirty_count=2,
        ahead=0,
        behind=1778,
        comparison_ref="origin/main",
    )
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


def test_workflow_pack_report_handles_nested_promoted_skills(tmp_path):
    mod = _load_module()
    root = tmp_path / "mattpocock-skills"

    domain = root / "skills" / "engineering" / "domain-modeling"
    domain.mkdir(parents=True)
    (domain / "SKILL.md").write_text(
        "---\nname: domain-modeling\ndescription: Build and sharpen a domain model.\n---\n\n# Domain Modeling\n",
        encoding="utf-8",
    )
    (domain / "agents").mkdir()
    (domain / "agents" / "openai.yaml").write_text(
        "interface:\n  display_name: Domain Modeling\n",
        encoding="utf-8",
    )

    wayfinder = root / "skills" / "engineering" / "wayfinder"
    wayfinder.mkdir(parents=True)
    (wayfinder / "SKILL.md").write_text(
        "---\nname: wayfinder\ndescription: Map a long-horizon decision space.\ndisable-model-invocation: true\n---\n\n# Wayfinder\n",
        encoding="utf-8",
    )
    (wayfinder / "agents").mkdir()
    (wayfinder / "agents" / "openai.yaml").write_text(
        "interface:\n  display_name: Wayfinder\npolicy:\n  allow_implicit_invocation: false\n",
        encoding="utf-8",
    )

    draft = root / "skills" / "in-progress" / "wizard"
    draft.mkdir(parents=True)
    (draft / "SKILL.md").write_text(
        "---\nname: wizard\ndescription: Draft wizard workflow.\n---\n\n# Wizard\n",
        encoding="utf-8",
    )

    (root / "docs" / "engineering").mkdir(parents=True)
    (root / "docs" / "engineering" / "domain-modeling.md").write_text("# Domain Modeling\n", encoding="utf-8")
    (root / "docs" / "engineering" / "wayfinder.md").write_text("# Wayfinder\n", encoding="utf-8")
    (root / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "plugin.json").write_text(
        '{"version":"1.2.0","skills":["./skills/engineering/domain-modeling","./skills/engineering/wayfinder"]}',
        encoding="utf-8",
    )
    (root / "package.json").write_text('{"version":"1.1.0"}', encoding="utf-8")
    (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")

    report = mod.agent_skills_report(root, source_id="mattpocock-skills")

    assert report.source_id == "mattpocock-skills"
    assert report.skill_count == 3
    assert report.bucket_counts == {"engineering": 2, "in-progress": 1}
    assert report.promoted_skill_count == 2
    assert report.plugin_skill_count == 2
    assert report.user_invoked_skill_count == 1
    assert report.model_invoked_skill_count == 2
    assert report.openai_metadata_count == 2
    assert report.missing_plugin_skills == []
    assert report.missing_promoted_docs == []
    assert report.invalid_invocation_policies == []
    assert report.plugin_version == "1.2.0"
    assert report.package_version == "1.1.0"
    assert report.version_mismatch is True


def test_workflow_pack_report_detects_manifest_and_invocation_drift(tmp_path):
    mod = _load_module()
    root = tmp_path / "workflow-pack"
    skill = root / "skills" / "engineering" / "human-only"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: human-only\ndescription: Human-triggered workflow.\ndisable-model-invocation: true\n---\n\n# Human Only\n",
        encoding="utf-8",
    )
    (skill / "agents").mkdir()
    (skill / "agents" / "openai.yaml").write_text(
        "interface:\n  display_name: Human Only\n",
        encoding="utf-8",
    )
    (root / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "plugin.json").write_text(
        '{"version":"1.0.0","skills":["./skills/engineering/human-only","./skills/engineering/missing"]}',
        encoding="utf-8",
    )
    (root / "package.json").write_text('{"name":"mattpocock-skills"}', encoding="utf-8")

    report = mod.agent_skills_report(root, source_id="workflow-pack")

    assert report.missing_plugin_skills == ["skills/engineering/missing"]
    assert report.missing_promoted_docs == ["docs/engineering/human-only.md"]
    assert report.invalid_invocation_policies == [
        "skills/engineering/human-only: Claude user-invoked policy is not mirrored in agents/openai.yaml"
    ]


def test_parse_args_accepts_generic_workflow_pack(monkeypatch, tmp_path):
    mod = _load_module()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_method_update_sources.py",
            "--workflow-pack-root",
            str(tmp_path),
            "--workflow-pack-id",
            "mattpocock-skills",
            "--json",
        ],
    )

    args = mod.parse_args()

    assert args.workflow_pack_root == str(tmp_path)
    assert args.workflow_pack_id == "mattpocock-skills"
    assert args.json is True


def test_agent_skills_report_preserves_flat_missing_skill_detection(tmp_path):
    mod = _load_module()
    root = tmp_path / "agent-skills"
    valid = root / "skills" / "valid-skill"
    valid.mkdir(parents=True)
    (valid / "SKILL.md").write_text(
        "---\nname: valid-skill\ndescription: Valid workflow.\n---\n\n# Valid\n",
        encoding="utf-8",
    )
    (root / "skills" / "missing-skill").mkdir()

    report = mod.agent_skills_report(root)

    assert report.skill_count == 2
    assert report.invalid_skills == ["missing-skill: missing SKILL.md"]


def test_workflow_pack_report_rejects_unsafe_manifest_paths(tmp_path):
    mod = _load_module()
    root = tmp_path / "workflow-pack"
    safe = root / "skills" / "engineering" / "safe"
    safe.mkdir(parents=True)
    (safe / "SKILL.md").write_text(
        "---\nname: safe\ndescription: Safe workflow.\n---\n\n# Safe\n",
        encoding="utf-8",
    )
    (root / "docs" / "engineering").mkdir(parents=True)
    (root / "docs" / "engineering" / "safe.md").write_text("# Safe\n", encoding="utf-8")
    (root / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "plugin.json").write_text(
        '{"skills":["../../outside","/tmp/outside","./skills/engineering/safe"]}',
        encoding="utf-8",
    )

    report = mod.agent_skills_report(root, source_id="workflow-pack")

    assert report.missing_plugin_skills == []
    assert report.manifest_errors == [
        ".claude-plugin/plugin.json: unsafe skill path: ../../outside",
        ".claude-plugin/plugin.json: unsafe skill path: /tmp/outside",
    ]


def test_workflow_pack_report_rejects_duplicate_and_symlink_escape(tmp_path):
    mod = _load_module()
    root = tmp_path / "workflow-pack"
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "SKILL.md").write_text(
        "---\nname: escape\ndescription: Outside workflow.\n---\n",
        encoding="utf-8",
    )
    (root / "skills" / "engineering").mkdir(parents=True)
    (root / "skills" / "engineering" / "escape").symlink_to(outside, target_is_directory=True)
    (root / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "plugin.json").write_text(
        '{"skills":["./skills/engineering/escape","skills/engineering/escape/"]}',
        encoding="utf-8",
    )

    report = mod.agent_skills_report(root, source_id="workflow-pack")

    assert report.promoted_skill_count == 0
    assert report.manifest_errors == [
        ".claude-plugin/plugin.json: unsafe skill path: ./skills/engineering/escape",
        ".claude-plugin/plugin.json: duplicate skill path: skills/engineering/escape",
    ]


def test_openai_metadata_uses_all_or_none_coverage_and_ignores_comments(tmp_path):
    mod = _load_module()
    root = tmp_path / "mattpocock-skills"
    promoted = []
    for name, user_invoked in [("model", False), ("human", True), ("missing", True)]:
        skill = root / "skills" / "engineering" / name
        skill.mkdir(parents=True)
        frontmatter = f"---\nname: {name}\ndescription: {name} workflow.\n"
        if user_invoked:
            frontmatter += "disable-model-invocation: true\n"
        (skill / "SKILL.md").write_text(frontmatter + "---\n", encoding="utf-8")
        promoted.append(f"./skills/engineering/{name}")
    model_metadata = root / "skills" / "engineering" / "model" / "agents"
    model_metadata.mkdir()
    (model_metadata / "openai.yaml").write_text(
        "policy:\n  # allow_implicit_invocation: false\n  allow_implicit_invocation: true # model-triggered\n",
        encoding="utf-8",
    )
    human_metadata = root / "skills" / "engineering" / "human" / "agents"
    human_metadata.mkdir()
    (human_metadata / "openai.yaml").write_text(
        "policy:\n  allow_implicit_invocation: false # user-triggered\n",
        encoding="utf-8",
    )
    (root / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "plugin.json").write_text(
        '{"name":"mattpocock-skills","skills":' + repr(promoted).replace("'", '"') + "}",
        encoding="utf-8",
    )

    report = mod.agent_skills_report(root)

    assert report.openai_metadata_count == 2
    assert report.missing_openai_metadata == ["skills/engineering/missing/agents/openai.yaml"]
    assert report.invalid_invocation_policies == []


def test_generic_pack_does_not_inherit_mattpocock_docs_contract(tmp_path):
    mod = _load_module()
    root = tmp_path / "generic-pack"
    skill = root / "skills" / "engineering" / "generic"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: generic\ndescription: Generic workflow.\n---\n",
        encoding="utf-8",
    )
    (root / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "plugin.json").write_text(
        '{"name":"another-pack","skills":["./skills/engineering/generic"]}',
        encoding="utf-8",
    )

    report = mod.agent_skills_report(root, source_id="mattpocock-skills")

    assert report.adapter == "generic"
    assert report.missing_promoted_docs == []


def test_workflow_pack_version_status_distinguishes_partial_and_mismatch(tmp_path):
    mod = _load_module()
    partial = tmp_path / "partial"
    partial.mkdir()
    (partial / "package.json").write_text('{"version":"1.1.0"}', encoding="utf-8")
    partial_report = mod.agent_skills_report(partial, source_id="workflow-pack")

    absent = tmp_path / "absent"
    absent.mkdir()
    absent_report = mod.agent_skills_report(absent, source_id="workflow-pack")

    matched = tmp_path / "matched"
    (matched / ".claude-plugin").mkdir(parents=True)
    (matched / ".claude-plugin" / "plugin.json").write_text('{"version":"1.1.0"}', encoding="utf-8")
    (matched / "package.json").write_text('{"version":"1.1.0"}', encoding="utf-8")
    matched_report = mod.agent_skills_report(matched, source_id="workflow-pack")

    mismatch = tmp_path / "mismatch"
    (mismatch / ".claude-plugin").mkdir(parents=True)
    (mismatch / ".claude-plugin" / "plugin.json").write_text('{"version":"1.2.0"}', encoding="utf-8")
    (mismatch / "package.json").write_text('{"version":"1.1.0"}', encoding="utf-8")
    mismatch_report = mod.agent_skills_report(mismatch, source_id="workflow-pack")

    assert partial_report.version_status == "partial"
    assert partial_report.version_mismatch is False
    assert absent_report.version_status == "absent"
    assert matched_report.version_status == "match"
    assert matched_report.version_mismatch is False
    assert mismatch_report.version_status == "mismatch"
    assert mismatch_report.version_mismatch is True


def test_invalid_invocation_booleans_are_errors_not_model_invocation(tmp_path):
    mod = _load_module()
    root = tmp_path / "mattpocock-skills"
    bad_frontmatter = root / "skills" / "engineering" / "bad-frontmatter"
    bad_frontmatter.mkdir(parents=True)
    (bad_frontmatter / "SKILL.md").write_text(
        "---\nname: bad-frontmatter\ndescription: Invalid boolean.\ndisable-model-invocation: maybe\n---\n",
        encoding="utf-8",
    )
    bad_openai = root / "skills" / "engineering" / "bad-openai"
    (bad_openai / "agents").mkdir(parents=True)
    (bad_openai / "SKILL.md").write_text(
        "---\nname: bad-openai\ndescription: Invalid OpenAI policy.\n---\n",
        encoding="utf-8",
    )
    (bad_openai / "agents" / "openai.yaml").write_text(
        "policy:\n  allow_implicit_invocation: maybe\n",
        encoding="utf-8",
    )

    report = mod.agent_skills_report(root)

    assert report.invalid_skills == [
        "bad-frontmatter: disable-model-invocation must be true or false"
    ]
    assert report.user_invoked_skill_count == 0
    assert report.model_invoked_skill_count == 1
    assert report.invalid_invocation_policies == [
        "skills/engineering/bad-openai/agents/openai.yaml: allow_implicit_invocation must be true or false"
    ]


def test_manifest_reports_non_string_versions_and_invalid_utf8(tmp_path):
    mod = _load_module()
    root = tmp_path / "workflow-pack"
    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "plugin.json").write_text(
        '{"version":12,"skills":[]}', encoding="utf-8"
    )
    (root / "package.json").write_bytes(b"\xff")

    report = mod.agent_skills_report(root, source_id="workflow-pack")

    assert report.version_status == "absent"
    assert ".claude-plugin/plugin.json: version must be a string" in report.manifest_errors
    assert any(error.startswith("package.json: ") for error in report.manifest_errors)


def test_git_report_uses_configured_non_main_upstream(tmp_path):
    mod = _load_module()
    repo = _committed_repo(tmp_path / "repo")
    _track_remote(repo, tmp_path / "remote.git", name="origin", branch="master")

    report = mod.git_report(repo)

    assert report.comparison_ref == "origin/master"
    assert (report.ahead, report.behind) == (0, 0)
    assert report.error == ""


def test_git_report_supports_custom_remote_upstream(tmp_path):
    mod = _load_module()
    repo = _committed_repo(tmp_path / "repo", branch="trunk")
    _track_remote(repo, tmp_path / "remote.git", name="company", branch="trunk")

    report = mod.git_report(repo)

    assert report.comparison_ref == "company/trunk"
    assert (report.ahead, report.behind) == (0, 0)


def test_git_report_falls_back_to_remote_head_when_detached(tmp_path):
    mod = _load_module()
    repo = _committed_repo(tmp_path / "repo")
    _track_remote(repo, tmp_path / "remote.git", name="origin", branch="master")
    _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/master")
    _git(repo, "checkout", "--detach")

    report = mod.git_report(repo)

    assert report.comparison_ref == "origin/master"
    assert (report.ahead, report.behind) == (0, 0)


def test_git_report_explains_when_no_comparison_ref_exists(tmp_path):
    mod = _load_module()
    repo = _committed_repo(tmp_path / "repo")

    report = mod.git_report(repo)

    assert report.comparison_ref == ""
    assert report.ahead is None
    assert report.behind is None
    assert "unable to determine Git comparison ref" in report.error


def test_workflow_pack_rejects_symlinked_and_oversized_metadata(tmp_path):
    mod = _load_module()
    root = tmp_path / "workflow-pack"
    outside = tmp_path / "outside"
    outside.mkdir()
    outside_plugin = outside / "plugin.json"
    outside_plugin.write_text('{"skills":[]}', encoding="utf-8")
    outside_skill = outside / "SKILL.md"
    outside_skill.write_text(
        "---\nname: linked\ndescription: Outside pack.\n---\n", encoding="utf-8"
    )

    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "plugin.json").symlink_to(outside_plugin)
    (root / "package.json").write_bytes(b"x" * (mod.MAX_EXTERNAL_FILE_BYTES + 1))
    linked = root / "skills" / "linked"
    linked.mkdir(parents=True)
    (linked / "SKILL.md").symlink_to(outside_skill)

    report = mod.agent_skills_report(root, source_id="workflow-pack")

    assert any("symlink is not allowed" in error for error in report.manifest_errors)
    assert any("exceeds" in error for error in report.manifest_errors)
    assert report.invalid_skills == ["linked: symlink is not allowed"]


def test_workflow_pack_reports_unreadable_skill_directory(tmp_path):
    mod = _load_module()
    root = tmp_path / "workflow-pack"
    skills = root / "skills"
    skills.mkdir(parents=True)
    hooks = root / "hooks"
    hooks.mkdir()
    skills.chmod(0)
    hooks.chmod(0)

    try:
        report = mod.agent_skills_report(root, source_id="workflow-pack")
    finally:
        skills.chmod(0o755)
        hooks.chmod(0o755)

    assert report.skill_count == 0
    assert "cannot inspect skills directory" in report.error
    assert "cannot inspect hooks" in report.error


def test_workflow_pack_rejects_symlinked_surface_directories(tmp_path):
    mod = _load_module()
    outside = tmp_path / "outside"
    leaked = outside / "leaked"
    leaked.mkdir(parents=True)
    (leaked / "SKILL.md").write_text(
        "---\nname: leaked\ndescription: Must not be discovered.\n---\n",
        encoding="utf-8",
    )

    root = tmp_path / "workflow-pack"
    root.mkdir()
    (root / "skills").symlink_to(outside, target_is_directory=True)
    outside_commands = tmp_path / "outside-commands"
    outside_commands.mkdir()
    (outside_commands / "leaked.md").write_text("must not be counted", encoding="utf-8")
    (root / ".claude").mkdir()
    (root / ".claude" / "commands").symlink_to(outside_commands, target_is_directory=True)

    report = mod.agent_skills_report(root, source_id="workflow-pack")

    assert report.skill_count == 0
    assert report.command_count == 0
    assert "cannot inspect skills directory: symlink is not allowed" in report.error
    assert "cannot inspect .claude/commands: symlink directory is not allowed" in report.error


def test_git_report_detached_pinned_tag_uses_exact_tag(tmp_path):
    mod = _load_module()
    seed = _committed_repo(tmp_path / "seed")
    _git(seed, "tag", "v1.1.0")
    remote = tmp_path / "origin.git"
    remote.mkdir()
    _git(remote, "init", "--bare")
    _git(seed, "remote", "add", "origin", str(remote))
    _git(seed, "push", "origin", "master", "refs/tags/v1.1.0")

    clone = tmp_path / "pinned"
    subprocess.run(
        ["git", "clone", "--quiet", "--branch", "v1.1.0", f"file://{remote}", str(clone)],
        check=True,
        text=True,
        capture_output=True,
    )

    report = mod.git_report(clone, fetch=False)

    assert report.branch_status.startswith("## HEAD (no branch)")
    assert report.comparison_ref == "v1.1.0"
    assert report.ahead == 0
    assert report.behind == 0
    assert report.error == ""
