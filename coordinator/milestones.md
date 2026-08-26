# Milestones

Each milestone is one independently buildable/evaluable unit. Generator
reads the full spec but works only the current milestone; Evaluator checks
current scope plus regressions in passed milestones.

Full context/rationale for this sequencing lives in `plan.md` in the
deliverable repo — this file is the operational, per-milestone
scope/done-criteria breakdown the Coordinator actually drives from.

## M1: Resumable backfill checkpoint, proven in isolation

**Scope:** Build the "GitHub Backfill Checkpoint" Fulcra record type
(`DurationAnnotation` base per `architecture.md`) and read/write
functions, tested against fake work items only — no GitHub API calls.

**Requirements:** Spec req. 4 (resumability/extensibility foundation).

**Done when:** A real kill-mid-process/restart-from-fresh-process test
against fake items proves correct resume (no reprocessing, no skipped
items). Per-repo tag-based checkpoint tracking design is exercised with
fake repo names.

## M2: GitHub API spike — existence pre-check and ingestion shape

**Scope:** Live spike against a real GitHub account to identify and
verify concrete endpoint(s) for the existence pre-check and per-item
retrieval of each in-scope activity type. Also spike whether the
`agg/day` Fulcra endpoint can serve the existence pre-check.

**Requirements:** Spec req. 1, 2.

**Done when:** A written, verified answer exists for which real
endpoint(s) will be used for each purpose — not assumed API knowledge.

## M3: Real raw ingestion — one repo, real Fulcra writes

**Scope:** Ingest one real, bounded window of one real repo's activity
into "GitHub Activity Raw" records using M2's endpoints, wired into
M1's checkpoint mechanism.

**Requirements:** Spec req. 1, 3, 4, 9.

**Done when:** Real per-item Fulcra records exist with correct
`recorded_at` (real event time), tags (`activity_type`, `repo`,
`github_identity`), and `sources`, verified by querying them back.

## M4: Full multi-repo, multi-year backfill at real scale

**Scope:** Extend M3 to real multi-repo (public+private,
contributed-to-only) discovery and uniform daily-granularity ingestion
across a real multi-year window against the real test account from
`decisions.md`.

**Requirements:** Spec req. 1, 2, 3, 4.

**Done when:** A real kill-mid-backfill/resume-from-fresh-session test
passes at this real scale (not just M1's fake-item version), and real
volume/cost numbers (record count, wall time, API call count) for a
real 1/2/3-year window are measured and recorded.

## M5: Backward/forward extension

**Scope:** Prove extending an existing backfill further into the past,
and separately forward for newer activity, without reprocessing or
duplicating already-covered ranges/repos.

**Requirements:** Spec req. 4.

**Done when:** Both directions demonstrated against real checkpoint
state with no duplication/reprocessing.

## M6: Rollup layer — day through year

**Scope:** Build "Activity Rollup" generation for all five period types
from real "GitHub Activity Raw" records, hand-rolled aggregation (no
Fulcra aggregation endpoint dependency for content), real `sources`
provenance chains. Numeric aggregation only — no model call.

**Requirements:** Spec req. 5, 9.

**Done when:** Real rollup records exist for all five period types with
correct provenance chains verified by tracing back to raw records.

## M7: Harness-side rollup summarization

**Scope:** Prove the concrete mechanism for "the model already running
the skill performs the summarization step" against real M6 rollups —
task-prompt shape, structured-input handoff, deterministic write-back
into the rollup's `note` field.

**Requirements:** Spec req. 5 (summary text), Generation Rules
(no-bundled-provider constraint).

**Done when:** Real summary text is written into real rollup records
via this mechanism, with no Gemini/bundled-provider API key used
anywhere in the path.

## M8: Notability signal (first pass)

**Scope:** Implement a first-pass notability/eventfulness formula as
"Notability Signal" records (`NumericAnnotation`, score in `value`,
detail in `note`).

**Requirements:** Spec req. 6.

**Done when:** Real signal records exist for real rollup periods with a
concrete, documented formula and real baseline-comparison detail in
`note`.

## M9: Narrative generation

**Scope:** Build the generation-time flow: ask for range, read
rollups+signals, produce one paced markdown document with a provenance
appendix, name the file per the chosen range.

**Requirements:** Spec req. 7.

**Done when:** A real generated document is actually read end to end
(not just "a file was produced") and its provenance appendix correctly
traces back to real records.

## M10: Packaging as an installable, agent-agnostic skill

**Scope:** Root-level `SKILL.md`, README, directly-runnable `app/` CLI
per spec req. 10.

**Done when:** The concrete first-usage test passes: a genuinely fresh
environment, agent installed, pointed at the repo, "I want to try this
skill out," including GitHub device-code auth (with the
already-logged-in-`gh` confirmation step) and Fulcra auth, with no
other setup assumed.
