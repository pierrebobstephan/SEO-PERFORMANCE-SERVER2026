from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from electri_city_ops.config import load_config
from electri_city_ops.doctrine import (
    enforce_runtime_guardrails,
    evaluate_pilot_gate,
    load_doctrine_policy,
    validate_policy_schema,
    validate_scope,
    validate_simulation_object,
)
from electri_city_ops.models import ActionPlan


def _complete_simulation_object() -> dict[str, object]:
    return {
        "pilot_id": "pilot-1",
        "connector_type": "cloudflare",
        "target_scope": "/",
        "excluded_scope": "/wp-admin",
        "baseline_window": "7d",
        "primary_metrics": ["response_ms"],
        "neighbor_signals": ["status_code"],
        "assumed_cause": "cache policy too defensive",
        "expected_gain": "faster anonymous homepage responses",
        "abort_conditions": ["status_regression"],
        "rollback_trigger": "status_regression",
        "adapt_options": ["approval_required", "blocked"],
        "final_pre_apply_gate": "approval_required",
    }


class DoctrineTests(unittest.TestCase):
    def test_builtin_policy_schema_is_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            load_result = load_doctrine_policy(Path(tmp))
            self.assertEqual(load_result.source, "builtin_default")
            self.assertEqual(validate_policy_schema(load_result.policy), [])

    def test_scope_validation_blocks_global_external_scope(self) -> None:
        with TemporaryDirectory() as tmp:
            policy = load_doctrine_policy(Path(tmp)).policy
            issues = validate_scope("global-cache-rule", policy, Path(tmp), external_effect=True)
            self.assertTrue(any("forbidden pattern" in item for item in issues))

    def test_simulation_object_requires_all_fields(self) -> None:
        with TemporaryDirectory() as tmp:
            policy = load_doctrine_policy(Path(tmp)).policy
            issues = validate_simulation_object({"pilot_id": "partial"}, policy)
            self.assertTrue(any("missing 'connector_type'" in item for item in issues))

    def test_pilot_gate_requires_approval_for_external_step_without_inputs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            policy = load_doctrine_policy(root).policy
            gate = evaluate_pilot_gate(
                {
                    "connector_type": "cloudflare",
                    "target_scope": "/",
                    "external_effect": True,
                    "requires_approval": True,
                    "approval_granted": False,
                    "secrets_available": False,
                    "reversible": True,
                    "rollback_path": "remove edge rule",
                    "rollback_trigger": "status_regression",
                    "validation_ready": True,
                    "simulation_required": True,
                    "simulation_object": _complete_simulation_object(),
                    "blast_radius": "narrow",
                    "doctrine_conformant": True,
                },
                policy,
                root,
            )
            self.assertEqual(gate.gate_state, "approval_required")
            self.assertFalse(gate.approval_ready)

    def test_pilot_gate_blocks_missing_rollback(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            policy = load_doctrine_policy(root).policy
            gate = evaluate_pilot_gate(
                {
                    "connector_type": "wordpress",
                    "target_scope": "global-template",
                    "external_effect": True,
                    "requires_approval": True,
                    "approval_granted": True,
                    "secrets_available": True,
                    "reversible": False,
                    "rollback_path": "",
                    "rollback_trigger": "",
                    "validation_ready": True,
                    "simulation_required": True,
                    "simulation_object": _complete_simulation_object(),
                    "blast_radius": "high",
                    "doctrine_conformant": True,
                },
                policy,
                root,
            )
            self.assertEqual(gate.gate_state, "blocked")
            self.assertFalse(gate.rollback_ready)

    def test_runtime_guardrails_keep_external_actions_waiting_approval(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "config"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "settings.toml"
            config_path.write_text(
                """
[system]
mode = "observe_only"

[permissions]
allow_remote_fetch = false
allow_external_changes = false

[notifications.email]
enabled = false
""",
                encoding="utf-8",
            )

            config, _ = load_config(config_path, root)
            _, guarded_actions, validations = enforce_runtime_guardrails(
                workspace_root=config.workspace_root,
                mode=config.mode,
                allow_external_changes=config.allow_external_changes,
                email_enabled=config.email.enabled,
                actions=[
                    ActionPlan(
                        identifier="a1",
                        phase="plan",
                        scope="external_target",
                        status="planned",
                        description="Future Cloudflare cache change",
                        target="https://example.com/",
                        risk="medium",
                        reversible=True,
                        requires_approval=True,
                        rollback="remove future rule",
                        validation="compare response metrics",
                    )
                ],
            )

            self.assertEqual(guarded_actions[0].status, "awaiting_approval")
            self.assertEqual(guarded_actions[0].metadata["doctrine_gate"], "approval_required")
            self.assertTrue(all(item.success for item in validations))
