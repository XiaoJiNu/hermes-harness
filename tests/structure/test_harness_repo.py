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
        "docs/runbooks/vscode-remote-ssh-ubuntu.md",
        "docs/runbooks/understand-anything-hermes-bootstrap.md",
        "docs/runbooks/hermes-method-update-sync.md",
        "docs/runbooks/agent-skills-method-intake.md",
        "docs/runbooks/requirements-discovery-and-domain-modeling.md",
        "docs/runbooks/dependency-aware-delivery-planning.md",
        "docs/runbooks/long-horizon-decision-mapping.md",
        "docs/runbooks/diff-review.md",
        "docs/runbooks/harness-skill-authoring.md",
        "docs/decisions/0001-hermes-default-runtime-not-exclusive.md",
        "docs/decisions/0002-agent-skills-external-method-source.md",
        "docs/references/agent-skills-crosswalk.md",
        "docs/references/mattpocock-skills-crosswalk.md",
        "docs/references/ai-paper-reproduction-sources.md",
        "docs/templates/active-plan-template.md",
        "docs/templates/domain-glossary-template.md",
        "docs/templates/handoff-template.md",
        "docs/templates/agent-brief-template.md",
        "docs/plans/completed/2026-04-24-hermes-codex-runtime-recovery.md",
        "docs/plans/completed/2026-04-25-hermes-harness-method-sync.md",
        "docs/plans/completed/2026-04-25-agent-skills-method-intake.md",
        "docs/plans/completed/2026-07-29-mattpocock-skills-method-intake.md",
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
        "scripts/bootstrap_understand_anything.py",
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
        "docs/runbooks/vscode-remote-ssh-ubuntu.md",
        "docs/runbooks/understand-anything-hermes-bootstrap.md",
        "docs/runbooks/hermes-method-update-sync.md",
        "docs/runbooks/agent-skills-method-intake.md",
        "docs/runbooks/requirements-discovery-and-domain-modeling.md",
        "docs/runbooks/dependency-aware-delivery-planning.md",
        "docs/runbooks/long-horizon-decision-mapping.md",
        "docs/runbooks/diff-review.md",
        "docs/runbooks/harness-skill-authoring.md",
        "docs/decisions/0002-agent-skills-external-method-source.md",
        "docs/references/agent-skills-crosswalk.md",
        "docs/references/mattpocock-skills-crosswalk.md",
        "docs/references/ai-paper-reproduction-sources.md",
        "docs/templates/active-plan-template.md",
        "docs/templates/domain-glossary-template.md",
        "docs/templates/handoff-template.md",
        "docs/templates/agent-brief-template.md",
        "docs/templates/ai-paper-reproduction-project-template.md",
        "docs/plans/completed/2026-04-24-hermes-codex-runtime-recovery.md",
        "docs/plans/completed/2026-04-25-hermes-harness-method-sync.md",
        "docs/plans/completed/2026-04-25-agent-skills-method-intake.md",
        "docs/plans/completed/2026-07-29-mattpocock-skills-method-intake.md",
        "scripts/hermes_codex_runtime_recovery.py",
        "scripts/bootstrap_understand_anything.py",
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


def test_vscode_remote_ssh_ubuntu_runbook_is_actionable():
    runbook = (ROOT / "docs/runbooks/vscode-remote-ssh-ubuntu.md").read_text(encoding="utf-8")
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs_index = (ROOT / "docs/README.md").read_text(encoding="utf-8")

    ref = "docs/runbooks/vscode-remote-ssh-ubuntu.md"
    assert ref in root_readme
    assert ref in docs_index

    for phrase in [
        "Remote-SSH",
        "openssh-server",
        "ssh-copy-id",
        "~/.ssh/config",
        "ubuntu20-dev",
        "VSCode Server",
        "PasswordAuthentication no",
        "Tailscale",
    ]:
        assert phrase in runbook


def test_understand_anything_hermes_bootstrap_is_reproducible_without_vendoring():
    runbook = (ROOT / "docs/runbooks/understand-anything-hermes-bootstrap.md").read_text(encoding="utf-8")
    script = (ROOT / "scripts/bootstrap_understand_anything.py").read_text(encoding="utf-8")
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs_index = (ROOT / "docs/README.md").read_text(encoding="utf-8")

    runbook_ref = "docs/runbooks/understand-anything-hermes-bootstrap.md"
    script_ref = "scripts/bootstrap_understand_anything.py"
    assert runbook_ref in root_readme
    assert runbook_ref in docs_index
    assert script_ref in docs_index

    for phrase in [
        "git@github.com:Lum1104/Understand-Anything.git",
        "external method source",
        "not source of truth",
        "不 vendor",
        "~/.understand-anything/repo",
        "~/.hermes/skills/understand-anything",
        "hermes skills list",
        "pnpm --filter @understand-anything/core build",
        "pnpm --filter @understand-anything/core test",
    ]:
        assert phrase in runbook

    for phrase in [
        "DEFAULT_REPO_URL",
        "git@github.com:Lum1104/Understand-Anything.git",
        "--update",
        "--skip-tests",
        "understand-anything-plugin/skills",
        ".hermes/skills/understand-anything",
        "pnpm --filter @understand-anything/core build",
    ]:
        assert phrase in script


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


def test_mattpocock_skills_intake_is_actionable_and_runtime_agnostic():
    crosswalk = (ROOT / "docs/references/mattpocock-skills-crosswalk.md").read_text(encoding="utf-8")
    intake = (ROOT / "docs/runbooks/agent-skills-method-intake.md").read_text(encoding="utf-8")
    discovery = (ROOT / "docs/runbooks/requirements-discovery-and-domain-modeling.md").read_text(encoding="utf-8")
    delivery = (ROOT / "docs/runbooks/dependency-aware-delivery-planning.md").read_text(encoding="utf-8")
    wayfinding = (ROOT / "docs/runbooks/long-horizon-decision-mapping.md").read_text(encoding="utf-8")
    review = (ROOT / "docs/runbooks/diff-review.md").read_text(encoding="utf-8")
    active_plan = (ROOT / "docs/templates/active-plan-template.md").read_text(encoding="utf-8")
    handoff = (ROOT / "docs/templates/handoff-template.md").read_text(encoding="utf-8")
    brief = (ROOT / "docs/templates/agent-brief-template.md").read_text(encoding="utf-8")
    source_checker = (ROOT / "scripts/check_method_update_sources.py").read_text(encoding="utf-8")

    for skill_name in [
        "ask-matt",
        "diagnosing-bugs",
        "grill-with-docs",
        "triage",
        "improve-codebase-architecture",
        "setup-matt-pocock-skills",
        "tdd",
        "to-spec",
        "to-tickets",
        "wayfinder",
        "implement",
        "prototype",
        "research",
        "domain-modeling",
        "codebase-design",
        "code-review",
        "grill-me",
        "grilling",
        "handoff",
        "teach",
        "writing-great-skills",
    ]:
        assert skill_name in crosswalk

    assert "d574778f94cf620fcc8ce741584093bc650a61d3" in crosswalk

    for boundary in ["source of truth", "disable-model-invocation", "agents/openai.yaml", "reject direct"]:
        assert boundary in crosswalk

    for phrase in ["--workflow-pack-root", "--workflow-pack-id", "promoted", "package/plugin"]:
        assert phrase in intake
        assert phrase in source_checker

    for phrase in ["一次只解决一个决策", "glossary", "ADR", "synthesis"]:
        assert phrase in discovery

    assert "docs/domains/<domain>/glossary.md" in discovery

    for phrase in [
        "tracer-bullet",
        "Blocked by",
        "expand",
        "migrate",
        "contract",
        "side effects",
        "agent-brief-template.md",
    ]:
        assert phrase in delivery

    for phrase in ["Destination", "Frontier", "Fog", "decision item", "tracer bullet"]:
        assert phrase in wayfinding

    for phrase in ["Destination", "Decision Frontier", "Fog", "Decision item", "tracer bullet"]:
        assert phrase in active_plan

    assert "| - | ready |" in active_plan

    for phrase in ["review base", "Standards", "Spec", "fixed-point"]:
        assert phrase in review

    assert "git ls-files --others --exclude-standard" in review

    assert "Canonical artifacts" in handoff
    assert "Exact next action" in handoff
    assert "agent-ready" in brief
    assert "needs-info" in brief
