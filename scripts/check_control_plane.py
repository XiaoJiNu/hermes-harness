from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    'README.md',
    'AGENTS.md',
    'ARCHITECTURE.md',
    'CONTRIBUTING.md',
    'Makefile',
    'docs/README.md',
    'docs/hermes-harness-operating-model.md',
    'docs/hermes-harness-general-playbook.md',
    'docs/hermes-harness-algorithm-engineer-playbook.md',
    'docs/hermes使用harness.md',
    'docs/specs/repo-charter.md',
    'docs/catalog/project-types.md',
    'docs/templates/project-type-playbook-template.md',
    'docs/runbooks/add-project-type-playbook.md',
    'docs/runbooks/maintenance-review.md',
    'docs/runbooks/hermes-codex-runtime-recovery.md',
    'docs/runbooks/hermes-method-update-sync.md',
    'docs/runbooks/agent-skills-method-intake.md',
    'docs/decisions/0001-hermes-default-runtime-not-exclusive.md',
    'docs/decisions/0002-agent-skills-external-method-source.md',
    'docs/references/agent-skills-crosswalk.md',
    'docs/plans/completed/2026-04-24-hermes-codex-runtime-recovery.md',
    'docs/plans/completed/2026-04-25-hermes-harness-method-sync.md',
    'docs/plans/completed/2026-04-25-agent-skills-method-intake.md',
    'docs/audits/2026-04-14-initial-state.md',
    'docs/tech-debt-tracker.md',
    'docs/QUALITY_SCORE.md',
    'docs/playbooks/software-product.md',
    'docs/playbooks/data-pipeline.md',
    'docs/playbooks/benchmark-eval-repo.md',
    'docs/playbooks/deployment-platform.md',
    'docs/playbooks/multi-agent-product-ops.md',
    'scripts/hermes_codex_runtime_recovery.py',
    'scripts/check_method_update_sources.py',
    '.github/workflows/ci.yml',
]

REQUIRED_DOC_INDEX_REFS = [
    'docs/hermes-harness-operating-model.md',
    'docs/hermes-harness-general-playbook.md',
    'docs/hermes-harness-algorithm-engineer-playbook.md',
    'docs/catalog/project-types.md',
    'docs/playbooks/software-product.md',
    'docs/playbooks/data-pipeline.md',
    'docs/playbooks/benchmark-eval-repo.md',
    'docs/playbooks/deployment-platform.md',
    'docs/playbooks/multi-agent-product-ops.md',
    'docs/runbooks/add-project-type-playbook.md',
    'docs/runbooks/maintenance-review.md',
    'docs/runbooks/hermes-codex-runtime-recovery.md',
    'docs/runbooks/hermes-method-update-sync.md',
    'docs/runbooks/agent-skills-method-intake.md',
    'docs/decisions/0002-agent-skills-external-method-source.md',
    'docs/references/agent-skills-crosswalk.md',
    'docs/plans/completed/2026-04-24-hermes-codex-runtime-recovery.md',
    'docs/plans/completed/2026-04-25-hermes-harness-method-sync.md',
    'docs/plans/completed/2026-04-25-agent-skills-method-intake.md',
    'scripts/hermes_codex_runtime_recovery.py',
    'scripts/check_method_update_sources.py',
]

FORBIDDEN_OPERATING_MODEL_TERMS = [
    'Flux4D',
    '/home/yr/yr/code/cv/AutoLabel/SSL/Flux4D',
]


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    sys.exit(1)


def main() -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        fail(f'missing required control-plane paths: {missing}')

    docs_index = (ROOT / 'docs/README.md').read_text(encoding='utf-8')
    missing_refs = [ref for ref in REQUIRED_DOC_INDEX_REFS if ref not in docs_index]
    if missing_refs:
        fail(f'docs/README.md is missing references: {missing_refs}')

    operating_model = (ROOT / 'docs/hermes-harness-operating-model.md').read_text(encoding='utf-8')
    stale_terms = [term for term in FORBIDDEN_OPERATING_MODEL_TERMS if term in operating_model]
    if stale_terms:
        fail(f'operating model still contains stale terms: {stale_terms}')

    project_types = (ROOT / 'docs/catalog/project-types.md').read_text(encoding='utf-8')
    for required_phrase in ['新增该项目类型的 playbook', '选择哪个 harness 方法']:
        if required_phrase not in project_types:
            fail(f'docs/catalog/project-types.md is missing phrase: {required_phrase}')

    for required_ref in [
        'docs/playbooks/benchmark-eval-repo.md',
        'docs/playbooks/deployment-platform.md',
        'docs/playbooks/multi-agent-product-ops.md',
    ]:
        if required_ref not in project_types:
            fail(f'docs/catalog/project-types.md missing project type reference: {required_ref}')

    entry_doc = (ROOT / 'docs/hermes使用harness.md').read_text(encoding='utf-8')
    for required_ref in [
        'docs/hermes-harness-operating-model.md',
        'docs/hermes-harness-general-playbook.md',
        'docs/hermes-harness-algorithm-engineer-playbook.md',
        'docs/catalog/project-types.md',
    ]:
        if required_ref not in entry_doc:
            fail(f'entry doc missing canonical reference: {required_ref}')

    print('PASS: control plane checks succeeded')


if __name__ == '__main__':
    main()
