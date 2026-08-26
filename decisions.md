# Decisions Log

Append-only chronological record of raw user decisions. This is the
source of truth for why; `spec.md` is the formalized target.

```text
## 2026-08-26 (Intake) — [scope]
Ground-up rebuild of "Engineering Journey" as v2. Explicitly no reuse
of any prior implementation/architecture/lessons-learned from the
original "engineering-journey" project — treat it as if it doesn't
exist for the purposes of this rebuild's design decisions.

## 2026-08-26 (Intake) — [github-api-efficiency]
Backfill must run a cheap existence pre-check per repo before any
per-period ingestion, to avoid wasting hundreds/thousands of API calls
on org-associated repos with zero real contributed activity.

## 2026-08-26 (Intake) — [activity-scope]
Capture everything (commits, PR opens/merges, PR reviews, issue/PR
comments), scoped strictly to those types — GitHub Actions/CI, gists,
wikis, project-board activity explicitly excluded. Activity type stored
as a real, filterable dimension on every record.

## 2026-08-26 (Intake) — [granularity]
Uniform daily granularity across the entire requested range, not
decaying/coarser for older history (deliberate divergence from a
similarly-scoped prior concept). Backfill must be extensible in both
directions (further into the past; forward for new activity) without
requiring one giant up-front run.

## 2026-08-26 (Intake) — [rollups]
Rollups (day/week/month/quarter/year) are precomputed and stored as
durable Fulcra records, not computed fresh at generation time.
Rollup recomputation as a future feature is noted but out of scope now.

## 2026-08-26 (Intake) — [notability]
A notability/eventfulness signal per rollup period is wanted, formula
deferred to Plan/Prototype.

## 2026-08-26 (Intake) — [output-scope]
This skill includes a lightweight markdown narrative generator as its
own layer. Richer outputs (resume-overview generator, interactive
dashboard) are explicitly deferred to a future, separate project
consuming the same Fulcra records.

## 2026-08-26 (Intake) — [output-range]
Narrative generation asks the user for the desired range at generation
time (full history or a sub-range) and names the output file
accordingly.

## 2026-08-26 (Intake) — [github-auth]
Browser-based OAuth device-code flow by default; confirm with the user
if a `gh` session or other GitHub auth already exists rather than
assuming it's the right account.

## 2026-08-26 (Intake) — [llm-provider]
No bundled/dedicated LLM provider dependency. Rollup-summary and
narrative-generation steps should use whatever model is already running
the skill, not a separate provider API key requirement.

## 2026-08-26 (Intake) — [determinism]
Ingestion/backfill/rollup-aggregation math is fully deterministic, no
model involvement. The model is only invoked for rollup-summary text
and narrative generation.

## 2026-08-26 (Intake) — [resumability]
Backfill must be safely interruptible and resumable — a hard
requirement, not a nice-to-have.

## 2026-08-26 (Intake) — [multi-identity-scope]
v1 build ingests one GitHub identity per run. Multi-identity "combined
journey" support, if built later, is approached as merging
separately-ingested record sets, not one ingestion process handling
multiple identities. Schema should not actively block this later
approach (e.g. via a `github_identity` tag on every record type), but
the merge tooling itself is not built now.

## 2026-08-26 (Intake) — [test-account]
Real live testing uses a different, real, long-lived personal GitHub
account (~10 years history, multiple org memberships, hundreds of
associated repos) — test runs bounded to 1/2/3-year windows for
iteration speed, not the full ~10 years, during Prototype/Build.

## 2026-08-26 (Architecture review) — [naming]
Custom Fulcra data type names use natural spacing (e.g. "GitHub
Activity Raw") rather than PascalCase/camelCase — confirmed live that
spaced names work fine and camelCase adds no benefit for a `name` field
that isn't a code identifier.

## 2026-08-26 (Architecture review) — [notability-base-type]
"Notability Signal" uses `NumericAnnotation` (real `value` field for the
score), not `MomentAnnotation` with the score buried in `note` — `note`
remains used alongside `value` for baseline-comparison detail; the two
are not mutually exclusive on a metric-class type.

## 2026-08-26 (Architecture review) — [aggregation-endpoint]
Confirmed and adopted: a real, working per-day count-aggregation
endpoint exists for custom event types
(`event/{BaseType}/{UUID}/agg/{resolution}`, unwrapped by SDK/CLI but
reachable via `fulcra_v1_api_path()`). Used for the existence pre-check
and as a possible corroborating volume signal — not for rollup content
aggregation (per-type/per-repo breakdowns remain hand-rolled).

## 2026-08-26 (delivery packaging) — [skill-form]
Final deliverable must be an installable, agent-agnostic skill: a
root-level `SKILL.md` (sibling to `app/`/`harness/`) in the same repo
the build harness writes to (not a separate repo), following the same
pattern `fulcra-rapid-prototype` and a similarly-scoped prior concept
both used. The underlying `app/` CLI must remain directly runnable with
no agent involved and must not assume Hermes (or any particular agent
runtime) specifically. First real usage/test target: a fresh VM, agent
installed, pointed at the deliverable repo, "I want to try this skill
out," with no other setup assumed.

## 2026-08-26 (Part II operating setup) — [generator-evaluator]
Generator and Evaluator both run as genuinely separate `claude` CLI
sessions (no shared context between them) rather than a Gemini-based
provider adapter — the bundled `harness/providers/gemini.py` and its
Gemini-dependent smoke tests (`test_loop_smoke`, `test_context_smoke`)
are explicitly not part of the real operating plan and were skipped
during scaffold verification rather than obtaining a Gemini key.

## 2026-08-26 (Part II operating setup) — [workspace-name]
Fulcra Workspace team name: `workspace-engineering-journey-v2`.

## 2026-08-26 (monorepo placement) — [repo-location]
`engineering-journey-v2` was briefly merged into the
`fulcra-community-projects` monorepo (as `engineering-journey-v2/`,
mirroring v1's layout) then reverted via a clean forward revert commit
at the user's request ("maybe we shouldn't"). Current state: the
project lives only in its own standalone repo
(`schr3b3r/engineering-journey-v2`); the monorepo question may be
revisited later but is not decided as of this entry.

## 2026-08-26 (control harness tooling) — [skill-gap-fixed]
Discovered that `fulcra-rapid-prototype`'s `scaffold_control_harness.py`
only generated 8 of the 16 files SKILL.md documents as required, and
its README referenced two nonexistent scripts
(`coordinator/bootstrap.py`, `coordinator/run_milestone.py`). Filed as
`fulcradynamics/community-skills#43` and fixed via PR #44 (real working
`bootstrap.py`/`run_milestone.py`, all missing templates, 9 new tests).
This project's own control harness was rescaffolded from the fixed
version rather than hand-built.
```
