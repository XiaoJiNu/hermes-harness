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
        "docs/hermes使用harness.md",
        "docs/specs/repo-charter.md",
        "docs/catalog/project-types.md",
        "docs/templates/project-type-playbook-template.md",
        "docs/runbooks/add-project-type-playbook.md",
        "docs/runbooks/maintenance-review.md",
        "docs/runbooks/hermes-codex-runtime-recovery.md",
        "docs/runbooks/hermes-method-update-sync.md",
        "docs/decisions/0001-hermes-default-runtime-not-exclusive.md",
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
    ]:
        assert required_ref in project_types, f"Project type catalog missing reference: {required_ref}"


def test_entry_doc_points_to_canonical_docs():
    entry_doc = (ROOT / "docs/hermes使用harness.md").read_text(encoding="utf-8")
    required_refs = [
        "docs/hermes-harness-operating-model.md",
        "docs/hermes-harness-general-playbook.md",
        "docs/hermes-harness-algorithm-engineer-playbook.md",
        "docs/catalog/project-types.md",
    ]
    missing_refs = [ref for ref in required_refs if ref not in entry_doc]
    assert not missing_refs, f"Entry doc is missing canonical references: {missing_refs}"
