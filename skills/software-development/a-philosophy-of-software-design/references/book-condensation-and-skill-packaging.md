# APOSD condensation and reusable skill packaging notes

This reference captures the useful meta-lessons from the session that turned the local Chinese translation of *A Philosophy of Software Design, 2nd Edition* into a Hermes software-design skill and then made both the skill and the source material durable across machines.

## Source used

- Durable archived translation copy: `skills/software-development/a-philosophy-of-software-design/references/aposd2e-zh-archive/`
- Archive notice and license boundary: `references/aposd2e-zh-archive/ARCHIVE_NOTICE.md`
- Upstream translation reference: `https://github.com/yingang/aposd2e-zh`
- Historical local translation directory: `/home/yr/yr/code/cv/object_detection/3D_OD/MV2DFusion-gly/aposd2e-zh` (do not rely on this path; it may be deleted)
- Canonical harness repository for durable cross-machine availability: `/home/yr/yr/code/harness-engineering-all/hermes-harness`

## Condensation strategy that worked

When converting a design book into an operational agent skill, do not summarize chapter-by-chapter. Convert the book into:

1. Trigger conditions: when the skill must be used.
2. Core mental model: the few ideas that govern decisions.
3. Stepwise workflow: how to apply the ideas before, during, and after implementation.
4. Concrete review checklists: what to verify before coding and before finishing.
5. Red flags and fixes: how to detect design smells and choose repairs.
6. Prompt/delegation snippets: how to force future agents and subagents to apply the design lens.
7. Attribution and source notes: where the original material came from, and which copy is durable.

The best shape is a class-level umbrella skill (`software-design`, `api-design`, `programming`, `refactoring`) rather than a one-session artifact. Session-specific provenance belongs in `references/`.

## APOSD ideas that should dominate future implementation work

- Manage complexity as the primary design objective.
- Identify concrete complexity symptoms: change amplification, cognitive load, unknown unknowns.
- Prefer strategic programming over tactical "make it work" patches.
- Prefer deep modules: simple interfaces hiding substantial implementation and design knowledge.
- Hide information by giving each important design decision a clear owner.
- Avoid temporal decomposition when it leaks shared knowledge across stages.
- Make interfaces somewhat general for current needs, not speculative frameworks.
- Sink complexity into modules when doing so simplifies many callers.
- Define errors out of existence where reasonable before adding exception machinery.
- Write interface comments before implementation; hard-to-write comments are design feedback.
- Use precise, consistent names; hard-to-name concepts often indicate weak design boundaries.
- Change existing code so the result looks as if the requirement had been anticipated.
- Measure before performance-driven complexity.

## Packaging pattern for cross-machine skill and source availability

For durable availability beyond the current Hermes profile, keep the skill in a versioned repo in addition to installing it locally. If the skill depends on a local source repository that may disappear, archive the licensed source material under the skill's `references/` tree rather than only storing an absolute local path.

Recommended harness-repo layout:

```text
skills/
  README.md
  software-development/
    a-philosophy-of-software-design/
      SKILL.md
      references/
        aposd2e-zh-archive/
          ARCHIVE_NOTICE.md
          ARCHIVE_MANIFEST.md
          README.md
          LICENSE
          docs/
            ch01.md
            ...
scripts/
  install_harness_skills.py
```

A reusable installer should copy selected skill directories from the repository's `skills/` tree to the active Hermes profile, preserving category paths and supporting linked files under `references/`. Include a dry-run mode and a force option so the agent can verify behavior without overwriting existing local skills unintentionally.

Future machine install pattern:

```bash
git clone git@github.com:XiaoJiNu/hermes-harness.git
cd hermes-harness
python3 scripts/install_harness_skills.py --skill a-philosophy-of-software-design
```

After installation, the archived book should be available in the active Hermes profile at:

```text
~/.hermes/skills/software-development/a-philosophy-of-software-design/references/aposd2e-zh-archive/
```

## Verification pattern

After creating or changing this kind of skill package, verify both the skill itself and the versioned distribution path:

1. `skill_view(name='a-philosophy-of-software-design')` succeeds locally.
2. Skill frontmatter parses as valid YAML.
3. Any installer script supports dry-run and reports expected destination paths.
4. Repository structure gates pass, such as `python3 scripts/check_control_plane.py` and `python3 -m pytest tests/structure -q` when working inside `hermes-harness`.
5. The commit is pushed.
6. A temporary clone or equivalent remote check confirms the skill and archived source material exist in the remote repository.

## Pitfalls

1. Do not put all book analysis into the main `SKILL.md` if it makes the skill too long for routine loading. Keep the operational workflow in `SKILL.md` and place provenance, packaging notes, transcripts, and deeper analysis in `references/`.
2. Do not rely on a local absolute path for durable source material. If the user says the source may be deleted, copy the licensed material into a versioned archive and update skill metadata to point to that archive first.
3. Do not merge licensing boundaries. The skill workflow may be MIT, while archived source material keeps its original declared license and attribution.
