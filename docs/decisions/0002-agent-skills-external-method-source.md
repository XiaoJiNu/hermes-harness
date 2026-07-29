# Decision 0002: Treat agent-skills as an External Method Source

日期：2026-04-25

## Status

Accepted.

## Context

`git@github.com:addyosmani/agent-skills.git` is a public MIT-licensed collection of production-grade engineering skills for AI coding agents. It packages task-level workflows, specialist personas, Claude slash commands, hooks, and references.

This repository already defines project-level harness methods: project type selection, control-plane surfaces, plans, runbooks, decisions, validation, and runtime-agnostic operating rules. We want the useful parts of `agent-skills` without turning this repository into a Claude plugin or a mirror of that external project.

## Decision

`agent-skills` is an external method source, not source of truth for this repository.

The source of truth remains the files in `hermes-harness`: README, AGENTS, catalog, playbooks, runbooks, decisions, templates, tests, and scripts. External methods become binding only after they are reviewed, adapted, and committed into those surfaces.

We adopt these reusable ideas from `agent-skills`:

- task-level workflow selection after project-level harness selection
- `skill / persona / command` separation
- process-oriented skills with trigger conditions and exit criteria
- anti-rationalization tables that block common agent shortcuts
- red flags that make drift visible during execution
- evidence-based verification requirements
- progressive disclosure: brief index first, detailed references only when needed
- parallel fan-out with a merge step for independent review perspectives

We do not directly adopt these runtime-specific parts:

- Claude plugin packaging as a required project dependency
- `.claude/commands/` paths as canonical entrypoints
- session-start hooks that inject large context into every run
- repository-level `CLAUDE.md` / `AGENTS.md` content that would replace this repository's map
- `SPEC.md` or `tasks/` as parallel source-of-truth paths
- automatic commit behavior without project/user authorization

The integrated method must remain runtime-agnostic. Hermes is the default runtime example, but Claude Code, Codex, OpenCode, Gemini CLI, Cursor, or another agent should be able to follow the same harness surfaces.

## Consequences

- `agent-skills` updates are reviewed through `docs/runbooks/agent-skills-method-intake.md`.
- Reusable ideas are mapped in `docs/references/agent-skills-crosswalk.md` before being copied or adapted into playbooks.
- Substantial copied text must preserve MIT license attribution.
- Runtime-specific packaging stays optional and outside the harness source of truth unless we explicitly add a runtime adapter with rollback and tests.
- Future external workflow packs should follow the same intake pattern rather than being vendored blindly.

## 2026-07-29 Amendment

`https://github.com/mattpocock/skills` is the second governed external method source under this decision. Its source-specific provenance and dispositions live in `docs/references/mattpocock-skills-crosswalk.md`; the original addyosmani mapping remains in `docs/references/agent-skills-crosswalk.md`. Neither source's plugin/runtime packaging is installed or treated as canonical by this amendment.

## Verification

A valid integration must pass:

```bash
python3 scripts/check_control_plane.py
python3 -m pytest tests/structure -q
python3 -m pytest tests/test_check_method_update_sources.py -q
make test-structure
```
