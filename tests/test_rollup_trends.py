from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from electri_city_ops.learning import build_learning_notes
from electri_city_ops.models import CycleResult, Metric
from electri_city_ops.storage import Storage


class RollupTrendTests(unittest.TestCase):
    def test_rollup_contains_response_and_html_trends(self) -> None:
        with TemporaryDirectory() as tmp:
            storage = Storage(Path(tmp) / "ops.sqlite3")
            storage.initialize()

            first = CycleResult(
                run_id="run-1",
                started_at="2026-03-29T07:00:00+00:00",
                finished_at="2026-03-29T07:00:10+00:00",
                mode="observe_only",
                status="validated",
                metrics=[
                    Metric("configured_domains", 1.0, scope="system", source="audit"),
                    Metric("response_ms", 200.0, unit="ms", scope="example.com", source="target"),
                    Metric("html_bytes", 1000.0, unit="bytes", scope="example.com", source="target"),
                ],
                summary={},
            )
            second = CycleResult(
                run_id="run-2",
                started_at="2026-03-29T08:00:00+00:00",
                finished_at="2026-03-29T08:00:10+00:00",
                mode="observe_only",
                status="validated",
                metrics=[
                    Metric("configured_domains", 1.0, scope="system", source="audit"),
                    Metric("response_ms", 150.0, unit="ms", scope="example.com", source="target"),
                    Metric("html_bytes", 1100.0, unit="bytes", scope="example.com", source="target"),
                ],
                summary={},
            )

            storage.upsert_cycle(first)
            storage.upsert_cycle(second)

            rollup = storage.build_rollup(365)

            self.assertEqual(rollup["domain_trends"]["example.com"]["response_ms"]["direction"], "improving")
            self.assertEqual(rollup["domain_trends"]["example.com"]["html_bytes"]["direction"], "worsening")

    def test_learning_notes_explain_legacy_runs_without_target_domain(self) -> None:
        with TemporaryDirectory() as tmp:
            storage = Storage(Path(tmp) / "ops.sqlite3")
            storage.initialize()

            legacy = CycleResult(
                run_id="legacy-no-domain",
                started_at="2026-03-28T07:00:00+00:00",
                finished_at="2026-03-28T07:00:05+00:00",
                mode="observe_only",
                status="validated",
                metrics=[Metric("configured_domains", 0.0, scope="system", source="audit")],
                summary={},
            )
            current = CycleResult(
                run_id="current-domain",
                started_at="2026-03-29T07:00:00+00:00",
                finished_at="2026-03-29T07:00:05+00:00",
                mode="observe_only",
                status="validated",
                metrics=[Metric("configured_domains", 1.0, scope="system", source="audit")],
                summary={},
            )

            storage.upsert_cycle(legacy)
            current.target_results = []
            notes_without_targets = build_learning_notes(storage, current)
            self.assertFalse(any("Legacy observe-only baseline without target domains" == note.title for note in notes_without_targets))

            current.target_results = [
                # Shape is irrelevant for this test; only presence matters.
                type("Snapshot", (), {"fetch_error": "", "homepage_status_code": 200})()
            ]
            notes_with_targets = build_learning_notes(storage, current)
            self.assertTrue(any("Legacy observe-only baseline without target domains" == note.title for note in notes_with_targets))


if __name__ == "__main__":
    unittest.main()
