from __future__ import annotations

from electri_city_ops.models import CycleResult, LearningNote
from electri_city_ops.storage import Storage


def build_learning_notes(storage: Storage, result: CycleResult) -> list[LearningNote]:
    notes: list[LearningNote] = []
    rollup_30 = storage.build_rollup(30)
    rollup_365 = storage.build_rollup(365)
    legacy_no_domain_runs = storage.count_observe_only_runs_without_targets(exclude_run_id=result.run_id)

    recurring = rollup_30.get("top_recurring_findings", [])
    if recurring and recurring[0]["count"] >= 2:
        top = recurring[0]
        notes.append(
            LearningNote(
                title="Recurring issue pattern detected",
                detail=(
                    f"Top recurring finding in 30 days: {top['title']} "
                    f"({top['count']} observations)."
                ),
            )
        )
    else:
        notes.append(
            LearningNote(
                title="Insufficient historical recurrence data",
                detail="The history window is still too small for stable recurrence heuristics.",
            )
        )

    if result.target_results and legacy_no_domain_runs:
        notes.append(
            LearningNote(
                title="Legacy observe-only baseline without target domains",
                detail=(
                    f"{legacy_no_domain_runs} older observe_only run(s) had no configured target domains. "
                    "Learning notes from those runs describe system-level baseline state and not this domain's content."
                ),
            )
        )

    if not result.metrics:
        notes.append(
            LearningNote(
                title="Metrics coverage is minimal",
                detail="No numeric metrics were captured in this cycle; keep the system in observe_only until inputs improve.",
            )
        )

    yearly_runs = rollup_365.get("run_count", 0)
    notes.append(
        LearningNote(
            title="Historical depth",
            detail=f"The history currently covers {yearly_runs} recorded run(s) inside the 365-day window.",
        )
    )
    return notes
