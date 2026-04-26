from pathlib import Path
import tempfile
import unittest

from electri_city_ops.ai_governance import (
    collect_ai_governance_status,
    load_ai_impact_assessments,
    load_ai_system_register,
    load_provenance_evidence,
    load_supply_chain_evidence,
    validate_ai_impact_assessments,
    validate_ai_system_register,
    validate_provenance_evidence,
    validate_secret_hygiene,
    validate_supply_chain_evidence,
)
from electri_city_ops.doctrine import load_doctrine_policy


class AIGovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()
        self.policy = load_doctrine_policy(self.workspace_root).policy

    def test_ai_governance_artifacts_validate(self) -> None:
        register_payload = load_ai_system_register(self.workspace_root)
        impact_payload = load_ai_impact_assessments(self.workspace_root)
        provenance_payload = load_provenance_evidence(self.workspace_root)
        supply_chain_payload = load_supply_chain_evidence(self.workspace_root)

        self.assertEqual(validate_ai_system_register(register_payload, self.policy), [])
        self.assertEqual(validate_ai_impact_assessments(impact_payload, register_payload, self.policy), [])
        self.assertEqual(validate_provenance_evidence(provenance_payload, register_payload), [])
        self.assertEqual(validate_supply_chain_evidence(supply_chain_payload, register_payload), [])
        self.assertEqual(validate_secret_hygiene(self.workspace_root), [])

    def test_ai_governance_status_is_blueprint_ready(self) -> None:
        status = collect_ai_governance_status(self.workspace_root, self.policy)
        self.assertEqual(status["status"], "blueprint_ready")
        self.assertEqual(status["issues"], [])
        self.assertEqual(status["system_register_entry_count"], 5)
        self.assertEqual(status["impact_assessment_count"], 5)
        self.assertEqual(status["provenance_entry_count"], 5)
        self.assertEqual(status["supply_chain_entry_count"], 5)
        self.assertEqual(status["risk_distribution"]["R0"], 1)
        self.assertEqual(status["risk_distribution"]["R1"], 2)
        self.assertEqual(status["risk_distribution"]["R2"], 2)
        self.assertEqual(status["secret_hygiene_issues"], [])

    def test_secret_hygiene_blocks_cleartext_env_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gitignore").write_text(
                "\n".join(
                    [
                        "deploy/systemd/*.env",
                        "deploy/systemd/*.env.save",
                        "!deploy/systemd/*.env.example",
                    ]
                ),
                encoding="utf-8",
            )
            env_dir = root / "deploy" / "systemd"
            env_dir.mkdir(parents=True)
            (env_dir / "paypal-business.env").write_text(
                "PAYPAL_BUSINESS_CLIENT_SECRET=real-value-that-must-not-live-in-workspace\n",
                encoding="utf-8",
            )

            issues = validate_secret_hygiene(root)

        self.assertEqual(
            issues,
            [
                "secret hygiene deploy/systemd/paypal-business.env:1 contains a non-placeholder value for PAYPAL_BUSINESS_CLIENT_SECRET"
            ],
        )

    def test_secret_hygiene_requires_ignore_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gitignore").write_text("*.log\n", encoding="utf-8")

            issues = validate_secret_hygiene(root)

        self.assertIn("secret hygiene missing .gitignore pattern 'deploy/systemd/*.env'", issues)


if __name__ == "__main__":
    unittest.main()
