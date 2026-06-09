---
name: a-philosophy-of-software-design
description: "Use whenever doing software design, API/module design, refactoring, code review, or programming. Applies John Ousterhout's A Philosophy of Software Design: manage complexity, prefer deep modules, hide information, design twice, write comments as design, keep code obvious, and invest strategically before implementation."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [software-design, api-design, architecture, refactoring, programming, complexity]
    related_skills: [writing-plans, test-driven-development, systematic-debugging, code-review]
  source:
    title: A Philosophy of Software Design, 2nd Edition
    author: John Ousterhout
    local_reference: /home/yr/yr/code/cv/object_detection/3D_OD/MV2DFusion-gly/aposd2e-zh
    translated_reference: https://github.com/yingang/aposd2e-zh
---

# A Philosophy of Software Design for Hermes

## Overview

Use this skill as the default design lens for software work. The source book's central claim is that software design is primarily the management of complexity. A program that merely works is not enough; the design should make future understanding and change cheaper.

The practical rule for Hermes work is:

> Before implementing, reduce future complexity. During implementation, keep abstractions deep. Before finishing, scan for complexity signals and fix the small ones before they accumulate.

This skill is not a pattern catalog. It is a judgment system for deciding how to split modules, how to define APIs, where to put knowledge, how to comment, when to combine or separate code, and how to modify existing systems without slowly making them worse.

## When to Use

Use this skill for:

- software architecture, module design, API design, class/function design
- writing implementation plans before coding
- refactoring existing code
- code review and design review
- debugging that reveals poor structure or hidden dependencies
- adding features to a mature codebase
- performance-sensitive design decisions
- writing or improving comments, names, conventions, and interface documentation

Use it even for small programming tasks when the change may affect public APIs, module boundaries, state ownership, error semantics, or future maintainability.

Do not use it as an excuse for speculative over-engineering. The book's preferred design is usually simple, somewhat general, and grounded in current needs.

## Core Mental Model

### Complexity is the enemy

Complexity is anything that makes a system hard to understand or modify. It shows up as:

1. **Change amplification**: a small conceptual change requires edits in many places.
2. **Cognitive load**: a developer must know too much before making progress.
3. **Unknown unknowns**: the dangerous missing facts are not visible, so changes silently break things.

Complexity usually grows incrementally from many small tactical choices. Treat every small leak, vague name, shallow wrapper, and avoidable dependency as a seed of future cost.

### Strategic programming beats tactical programming

Tactical programming optimizes for getting today's feature working quickly. Strategic programming accepts a small ongoing design investment so that future work remains fast.

Default Hermes behavior:

- Spend design effort before changing interfaces or module boundaries.
- Budget time for small refactors while implementing features.
- Do not stop at "it works" if the change leaves extra coupling, unclear names, shallow modules, or duplicated design knowledge.
- For non-trivial code changes, verify with tests or gates so refactoring remains safe.

### Deep modules are the main design target

A deep module provides a lot of functionality behind a simple interface. A shallow module exposes nearly as much interface complexity as the implementation it hides.

Prefer:

- small, stable, easy-to-use interfaces
- implementations that absorb messy details internally
- modules that hide design decisions and expose only what callers need

Avoid:

- many tiny classes or wrappers that mostly pass through calls
- APIs that force callers to understand rare cases or internal representation
- getters/setters that expose representation instead of offering behavior

## Design Workflow

### 1. Rebuild the local control plane first

For repository work, first read the repo's own source of truth: README, AGENTS, architecture docs, specs, tests, runbooks, and existing conventions. This skill should improve the current repo design, not override established constraints blindly.

Ask:

- What is the current module boundary?
- What information is already centralized?
- Which names, conventions, and abstractions are already established?
- Which verification gates protect refactoring?

### 2. Name the complexity symptoms before designing

Before choosing a design, identify the complexity you are trying to reduce:

- What change currently amplifies across files?
- What does a developer need to know that should be hidden?
- Which facts are likely to become unknown unknowns?
- Which design decision is repeated in multiple modules?
- Which interface forces callers to handle internals or rare cases?

If you cannot state the complexity symptom, the proposed refactor may be aesthetic rather than useful.

### 3. Decide what is important

Good design distinguishes important concepts from unimportant details.

Important things should be:

- visible in names, interfaces, architecture docs, or central modules
- minimized in number
- centralized when possible
- repeated only when repetition creates useful emphasis, not duplication of decisions

Unimportant details should be hidden inside modules, defaulted, inferred, or handled automatically.

### 4. Design twice

For every significant API, module boundary, state model, or error semantics decision, generate at least two meaningfully different designs.

For each option compare:

- interface simplicity for the common case
- amount of functionality hidden behind the interface
- information hidden versus leaked
- dependencies introduced or removed
- how future changes would land
- testability and verification cost
- consistency with existing repo conventions

Pick the option that reduces long-term complexity, or combine the best parts. Do not settle for the first plausible design.

### 5. Prefer information hiding over time-order decomposition

Do not split modules merely by the chronological order of operations such as read/parse/validate/write if those steps share the same design knowledge. That often leaks the same representation or protocol across several modules.

Split around hidden knowledge:

- file format knowledge belongs in one parser/serializer boundary
- protocol details belong in one request/response abstraction
- storage layout belongs behind one storage interface
- model/data preprocessing assumptions belong in one manifest or adapter boundary

If two modules must know the same private fact, consider combining them or introducing a deeper abstraction.

### 6. Make modules somewhat general, not speculative

A good interface is often more general than today's exact use case, but not a grand framework for imagined future needs.

Use this rule:

- Let the implementation support today's need.
- Let the interface express a clean, reusable abstraction.
- Keep special-case policy in the narrow layer where it belongs.

Examples:

- Prefer `insert(position, text)` and `delete(start, end)` over UI-specific `backspace()` in a low-level text store.
- Prefer a data adapter that hides source-specific quirks over spreading dataset-specific conditionals through training code.
- Prefer a domain method that expresses behavior over exposing raw fields with getters/setters.

### 7. Put complexity where it benefits the whole system

Sink complexity into a module when doing so simplifies many callers. It is usually better for the module implementer to handle tricky cases once than for every caller to handle them repeatedly.

Apply this especially to:

- default behavior
- parameter normalization
- parsing and serialization
- retries, idempotency, and boundary conditions
- data format conversions
- cache invalidation and resource cleanup

Be careful with configuration parameters. A configuration knob can be a complexity leak if it pushes a hard design decision onto users or operators. Prefer automatic behavior when it is reliable.

### 8. Define errors out of existence when possible

Error handling is a major complexity source. Before adding exceptions, ask whether the operation can be defined so the problematic case is normal.

Prefer, in order:

1. **Define away the error**: make the semantics total where reasonable. Example: deleting something already absent can mean success if the goal is "ensure absent".
2. **Mask low-level exceptions**: handle retries or recovery inside the lower-level module.
3. **Aggregate exceptions**: use a small number of central handlers for broad categories.
4. **Crash with diagnostics** for truly rare, unrecoverable cases where recovery code would add more complexity than value.

Do not create many fine-grained exceptions unless callers truly need distinct recovery behavior.

### 9. Write comments before code when designing abstractions

Comments are a design tool, not only documentation after the fact.

For new classes, modules, APIs, and important functions:

1. Write the interface comment first.
2. Write the public method signatures and comments.
3. Write key state variables with comments describing invariants, units, ownership, and boundary conditions.
4. Only then implement.

If the interface comment is long, tangled, or hard to write, treat that as design feedback. Redesign until the abstraction is easy to describe.

Good comments describe what code cannot express well:

- high-level intent
- why a design decision exists
- invariants and assumptions
- units, ranges, ownership, nullability, side effects
- cross-module dependencies and protocol obligations
- what callers must know without reading implementation

Bad comments repeat code or expose implementation details in interface docs.

### 10. Make names precise and consistent

A name should create a clear mental picture. Vague names create obscurity and bugs.

Use this naming checklist:

- Does the name distinguish this concept from nearby concepts?
- Does it include units or coordinate frame when relevant?
- Does it avoid generic words such as `data`, `info`, `manager`, `helper`, `status`, `value`, or `count` unless they are truly precise in context?
- Is the same concept named the same way everywhere?
- If naming is hard, is the underlying concept poorly defined?

In existing code, follow established naming conventions unless a new convention has overwhelming value and you update all affected usages consistently.

### 11. Design for readability, not writer convenience

Software is read and modified more often than it is initially written. Optimize for the future reader.

Prefer code that is obvious:

- clear names
- consistent structure
- local invariants documented near the code
- whitespace that reveals structure
- domain-specific types instead of anonymous tuples or generic containers
- straightforward control flow when possible

Avoid clever shortcuts that save a few lines but increase cognitive load.

### 12. Modify existing code as if the system had anticipated the change

When adding a feature, do not simply make the smallest patch. The final structure should look as if the new requirement had been considered during the original design.

Practical process:

1. Understand the existing abstraction and conventions.
2. Identify the design limitation exposed by the change.
3. Make the smallest coherent refactor that removes or reduces the limitation.
4. Add the feature through the improved abstraction.
5. Update comments, tests, docs, and call sites together.

If you do not improve the design while changing it, you are probably making it worse.

### 13. Treat tests as refactoring leverage

The book values unit tests because they make design improvement safe. In this Hermes environment, keep test-driven or gate-driven verification, but do not let tests force a shallow or overly specific API.

Use tests to verify behavior and protect refactors; use this skill to judge whether the API itself is deep, clear, and low-complexity.

### 14. Performance design: simple first, measure, then optimize the critical path

Simple code is often fast. Do not complicate design for speculative performance.

When performance matters:

1. Understand inherently expensive operations: I/O, network, allocation, synchronization, GPU/CPU transfers, serialization, data copies.
2. Measure before and after changes.
3. Identify the critical path for common cases.
4. Imagine the ideal minimal path.
5. Refactor so common cases approach the ideal path while preserving clear abstractions.
6. Move rare-case checks and special handling away from the critical path when possible.

## Red Flags and Fixes

| Red flag | Meaning | Fix |
|---|---|---|
| Shallow module | Interface is almost as complex as implementation | Merge, deepen, or replace with a stronger abstraction |
| Information leakage | Same design decision appears in multiple modules | Centralize the decision or hide it behind one interface |
| Temporal decomposition | Modules split by operation order instead of hidden knowledge | Re-split around information ownership |
| Overexposure | API forces callers to know rare or internal details | Add defaults, narrower common-case methods, or internal handling |
| Pass-through method | Wrapper adds interface surface without new abstraction | Remove, merge, or move responsibility |
| Pass-through variable | Parameter is threaded through many layers unused | Introduce context/ownership boundary or dependency injection with care |
| Generic/special mix | Reusable mechanism entangled with one use case | Separate policy from mechanism at the right layer |
| Conjoined methods | Must read multiple methods together to understand behavior | Merge or create a deeper helper with a real abstraction |
| Too many tiny classes | Class count increases but abstraction depth does not | Combine around shared knowledge |
| Repeated code or decisions | Same logic or fact copied repeatedly | Extract a single source of truth |
| Comment repeats code | Comment adds no knowledge | Delete or replace with intent/invariant/why |
| Interface doc mentions internals | Users must learn implementation details | Rewrite around external behavior and contract |
| Vague names | Name does not carry useful information | Rename or clarify the concept |
| Hard-to-name entity | The concept itself may be muddled | Redesign the responsibility boundary |
| Hard-to-describe API | Interface comment becomes long or tangled | Redesign for a simpler abstraction |
| Non-obvious code | Behavior cannot be guessed while reading | Improve names, structure, comments, or abstraction |
| Configuration explosion | Users must solve internal design choices | Infer, default, or encapsulate choices inside the module |
| Exception explosion | Many handlers for rare cases dominate code | Define away, mask, aggregate, or crash with diagnostics |

## Review Checklist Before Implementing

- [ ] I identified the complexity symptoms this design should reduce.
- [ ] I considered at least two design options for significant decisions.
- [ ] The chosen modules are deep: simple interface, substantial hidden functionality.
- [ ] Important design knowledge has one clear owner.
- [ ] Adjacent layers expose different abstractions, not pass-through copies.
- [ ] Common use cases are simpler than rare use cases.
- [ ] General mechanism and special policy are separated.
- [ ] Error semantics are defined to minimize exceptional cases.
- [ ] Names are precise and consistent with the repo.
- [ ] Interface comments can describe the abstraction without implementation pollution.
- [ ] Tests or gates exist to protect the intended behavior and refactor.

## Review Checklist Before Finishing Code

- [ ] The change does not introduce new change amplification.
- [ ] The change reduces or at least does not increase cognitive load.
- [ ] There are no new unknown-unknown traps such as hidden shared assumptions.
- [ ] Public APIs and module comments describe what callers need to know.
- [ ] Implementation comments explain non-obvious intent, invariants, or why.
- [ ] Existing comments near changed code are updated.
- [ ] No new shallow wrappers, pass-through methods, or needless getters/setters were added.
- [ ] Special cases are not scattered through unrelated modules.
- [ ] Performance claims are measured or clearly marked as assumptions.
- [ ] Verification commands were run and reported.

## Hermes Prompt Pattern

When using Hermes on a software design or implementation task, explicitly apply this short pattern in the plan or review:

```text
APOSD design lens:
- Complexity symptoms to reduce:
- Important design knowledge and owner:
- Two design options considered:
- Chosen deep module/API:
- Information hidden from callers:
- Error semantics:
- Comments/names/conventions to update:
- Verification gate:
```

For subagents, include this requirement in the delegated goal:

```text
Use the a-philosophy-of-software-design skill. Prefer deep modules, information hiding, precise names, comments-first interface design, and design-twice comparison before implementation. Return the complexity symptoms reduced and the verification commands run.
```

## Common Pitfalls

1. **Turning the book into slogans.** Do not merely say "reduce complexity". Identify concrete change amplification, cognitive load, or unknown unknowns.

2. **Over-generalizing.** "Somewhat general" means a clean abstraction for present needs, not a framework for imaginary requirements.

3. **Splitting everything into tiny pieces.** Small methods/classes can still be shallow. Split only when the new boundary hides knowledge or creates a deeper abstraction.

4. **Moving complexity to callers.** A module that is easy to implement but hard to use is usually the wrong tradeoff.

5. **Adding configuration instead of design.** A knob may be useful, but often it is a sign the module failed to decide something it should own.

6. **Treating comments as decoration.** Comments define abstractions. Missing or hard-to-write comments are design feedback.

7. **Optimizing before measuring.** Performance work without measurement often adds complexity in the wrong place.

8. **Using tests as a substitute for design judgment.** Passing tests do not prove the abstraction is deep or maintainable.

## Source and Attribution

This skill is an applied summary and workflow derived from John Ousterhout's *A Philosophy of Software Design, 2nd Edition* and the local Chinese translation repository at `/home/yr/yr/code/cv/object_detection/3D_OD/MV2DFusion-gly/aposd2e-zh`. The translation repository is CC-BY 4.0; this skill is an original operational condensation for Hermes usage, not a replacement for the book.
