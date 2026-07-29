# Hermes Skills

This directory contains Hermes skills that are maintained with the harness-method reference repository so they can be reinstalled on a new machine.

## Install into the active Hermes profile

From the repository root:

```bash
python3 scripts/install_harness_skills.py --skill a-philosophy-of-software-design
```

By default the script installs into `$HERMES_HOME/skills` when `HERMES_HOME` is set, otherwise `~/.hermes/skills`.
Use `--dry-run` to preview the copy.

Author or adapt skills according to `docs/runbooks/harness-skill-authoring.md`: check for existing equivalents first, review invocation boundaries, preserve external-source attribution, and validate through a temporary install before touching an active Hermes profile.

## Included skills

- `software-development/a-philosophy-of-software-design`: software design, API/module design, refactoring, code review, and programming lens derived from John Ousterhout's *A Philosophy of Software Design*. This skill also carries a durable archived copy of the `aposd2e-zh` translation under `references/aposd2e-zh-archive/`, so the source material remains available after installing the skill on a new machine.
