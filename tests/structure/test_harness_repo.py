from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_required_control_plane_files_exist():
    required_paths = [
        "README.md",
        "AGENTS.md",
        "ARCHITECTURE.md",
        "CONTRIBUTING.md",
        "Makefile",
        "docs/README.md",
        "docs/hermes-harness-operating-model.md",
        "docs/hermes-harness-general-playbook.md",
        "docs/hermes-harness-algorithm-engineer-playbook.md",
        "docs/playbooks/ai-paper-reproduction.md",
        "docs/hermes使用harness.md",
        "docs/specs/repo-charter.md",
        "docs/catalog/project-types.md",
        "docs/templates/project-type-playbook-template.md",
        "docs/templates/ai-paper-reproduction-project-template.md",
        "docs/runbooks/add-project-type-playbook.md",
        "docs/runbooks/maintenance-review.md",
        "docs/runbooks/hermes-codex-runtime-recovery.md",
        "docs/runbooks/hermes-method-update-sync.md",
        "docs/runbooks/agent-skills-method-intake.md",
        "docs/decisions/0001-hermes-default-runtime-not-exclusive.md",
        "docs/decisions/0002-agent-skills-external-method-source.md",
        "docs/references/agent-skills-crosswalk.md",
        "docs/references/ai-paper-reproduction-sources.md",
        "docs/plans/completed/2026-04-24-hermes-codex-runtime-recovery.md",
        "docs/plans/completed/2026-04-25-hermes-harness-method-sync.md",
        "docs/plans/completed/2026-04-25-agent-skills-method-intake.md",
        "docs/audits/2026-04-14-initial-state.md",
        "docs/tech-debt-tracker.md",
        "docs/QUALITY_SCORE.md",
        "docs/playbooks/software-product.md",
        "docs/playbooks/data-pipeline.md",
        "docs/playbooks/benchmark-eval-repo.md",
        "docs/playbooks/deployment-platform.md",
        "docs/playbooks/multi-agent-product-ops.md",
        "scripts/check_control_plane.py",
        "scripts/hermes_codex_runtime_recovery.py",
        "scripts/check_method_update_sources.py",
        ".github/workflows/ci.yml",
    ]

    missing = [path for path in required_paths if not (ROOT / path).exists()]
    assert not missing, f"Missing required control-plane paths: {missing}"


def test_docs_index_links_to_key_playbooks_and_runbooks():
    docs_index = (ROOT / "docs/README.md").read_text(encoding="utf-8")
    required_refs = [
        "docs/hermes-harness-operating-model.md",
        "docs/hermes-harness-general-playbook.md",
        "docs/hermes-harness-algorithm-engineer-playbook.md",
        "docs/playbooks/ai-paper-reproduction.md",
        "docs/catalog/project-types.md",
        "docs/playbooks/software-product.md",
        "docs/playbooks/data-pipeline.md",
        "docs/playbooks/benchmark-eval-repo.md",
        "docs/playbooks/deployment-platform.md",
        "docs/playbooks/multi-agent-product-ops.md",
        "docs/runbooks/add-project-type-playbook.md",
        "docs/runbooks/maintenance-review.md",
        "docs/runbooks/hermes-codex-runtime-recovery.md",
        "docs/runbooks/hermes-method-update-sync.md",
        "docs/runbooks/agent-skills-method-intake.md",
        "docs/decisions/0002-agent-skills-external-method-source.md",
        "docs/references/agent-skills-crosswalk.md",
        "docs/references/ai-paper-reproduction-sources.md",
        "docs/templates/ai-paper-reproduction-project-template.md",
        "docs/plans/completed/2026-04-24-hermes-codex-runtime-recovery.md",
        "docs/plans/completed/2026-04-25-hermes-harness-method-sync.md",
        "docs/plans/completed/2026-04-25-agent-skills-method-intake.md",
        "scripts/hermes_codex_runtime_recovery.py",
        "scripts/check_method_update_sources.py",
    ]

    missing_refs = [ref for ref in required_refs if ref not in docs_index]
    assert not missing_refs, f"docs/README.md is missing references: {missing_refs}"


def test_operating_model_is_repo_specific_and_not_flux4d_specific():
    operating_model = (ROOT / "docs/hermes-harness-operating-model.md").read_text(encoding="utf-8")
    forbidden_terms = ["Flux4D", "/home/yr/yr/code/cv/AutoLabel/SSL/Flux4D"]
    present = [term for term in forbidden_terms if term in operating_model]
    assert not present, f"Operating model still contains stale repo-specific terms: {present}"


def test_project_type_catalog_has_extension_rule():
    project_types = (ROOT / "docs/catalog/project-types.md").read_text(encoding="utf-8")
    assert "新增该项目类型的 playbook" in project_types
    assert "选择哪个 harness 方法" in project_types
    for required_ref in [
        "docs/playbooks/benchmark-eval-repo.md",
        "docs/playbooks/deployment-platform.md",
        "docs/playbooks/multi-agent-product-ops.md",
        "docs/playbooks/ai-paper-reproduction.md",
    ]:
        assert required_ref in project_types, f"Project type catalog missing reference: {required_ref}"


def test_entry_doc_points_to_canonical_docs():
    entry_doc = (ROOT / "docs/hermes使用harness.md").read_text(encoding="utf-8")
    required_refs = [
        "docs/hermes-harness-operating-model.md",
        "docs/hermes-harness-general-playbook.md",
        "docs/hermes-harness-algorithm-engineer-playbook.md",
        "docs/playbooks/ai-paper-reproduction.md",
        "docs/catalog/project-types.md",
    ]
    missing_refs = [ref for ref in required_refs if ref not in entry_doc]
    assert not missing_refs, f"Entry doc is missing canonical references: {missing_refs}"


def test_codex_runtime_recovery_covers_refresh_token_conflict():
    runbook = (ROOT / "docs/runbooks/hermes-codex-runtime-recovery.md").read_text(encoding="utf-8")
    for phrase in [
        "Codex refresh token was already consumed by another client",
        "hermes auth add openai-codex --type oauth",
        "ChatGPT Security Settings",
        "device-code",
        "hermes auth status openai-codex",
        "hermes chat -q",
    ]:
        assert phrase in runbook


def test_ai_paper_reproduction_method_is_actionable():
    playbook = (ROOT / "docs/playbooks/ai-paper-reproduction.md").read_text(encoding="utf-8")
    sources = (ROOT / "docs/references/ai-paper-reproduction-sources.md").read_text(encoding="utf-8")
    template = (ROOT / "docs/templates/ai-paper-reproduction-project-template.md").read_text(encoding="utf-8")
    catalog = (ROOT / "docs/catalog/project-types.md").read_text(encoding="utf-8")

    for phrase in ["复现等级", "paper-claim-matrix.md", "source-survey.md", "paper-vs-code-audit.md", "gap log", "R4", "docs/templates/ai-paper-reproduction-project-template.md"]:
        assert phrase in playbook

    for phrase in ["Reproduction Spec", "Source Survey", "Paper Claim Matrix", "Paper-vs-Code Audit", "Smoke Gates", "Run Registry", "Gap Log", "Reproduction Report"]:
        assert phrase in template

    for source in [
        "paperswithcode/paperswithcode-data",
        "labmlai/annotated_deep_learning_paper_implementations",
        "huggingface/transformers",
        "open-mmlab/mmdetection",
        "the-turing-way/the-turing-way",
    ]:
        assert source in sources

    assert "无官方代码" in catalog
    assert "docs/playbooks/ai-paper-reproduction.md" in catalog


def test_agent_skills_intake_preserves_harness_boundaries():
    decision = (ROOT / "docs/decisions/0002-agent-skills-external-method-source.md").read_text(encoding="utf-8")
    crosswalk = (ROOT / "docs/references/agent-skills-crosswalk.md").read_text(encoding="utf-8")
    runbook = (ROOT / "docs/runbooks/agent-skills-method-intake.md").read_text(encoding="utf-8")
    operating_model = (ROOT / "docs/hermes-harness-operating-model.md").read_text(encoding="utf-8")
    multi_agent = (ROOT / "docs/playbooks/multi-agent-product-ops.md").read_text(encoding="utf-8")

    assert "external method source" in decision
    assert "not source of truth" in decision
    assert "Claude plugin" in decision
    assert "runtime-agnostic" in decision

    for skill_name in [
        "using-agent-skills",
        "spec-driven-development",
        "planning-and-task-breakdown",
        "context-engineering",
        "shipping-and-launch",
    ]:
        assert skill_name in crosswalk

    for harness_surface in [
        "docs/specs/",
        "docs/plans/active/",
        "docs/runbooks/",
        "docs/playbooks/",
    ]:
        assert harness_surface in crosswalk

    assert "git@github.com:addyosmani/agent-skills.git" in runbook
    assert "license" in runbook.lower()
    assert "不直接采用" in runbook
    assert "agent-skills" in operating_model
    assert "skill / persona / command" in multi_agent
    assert "router persona" in multi_agent
