from pathlib import Path
import unittest

from electri_city_ops.automation_contracts import (
    attach_contract,
    build_automation_contract_state,
    candidate_contract_issues,
    get_automation_contract,
    load_automation_contracts,
    validate_automation_contracts,
)


class AutomationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()
        self.registry = load_automation_contracts(self.workspace_root)

    def test_automation_contract_registry_is_deny_by_default_and_valid(self) -> None:
        issues = validate_automation_contracts(self.registry)
        self.assertEqual(issues, [])
        state = build_automation_contract_state(self.registry, issues)
        self.assertEqual(state["status"], "valid")
        self.assertEqual(state["default_policy"], "deny_by_default")
        self.assertEqual(state["allowed_action_types"], ["rank_math_meta_description_update"])

    def test_rank_math_meta_description_contract_requires_admin_and_rollback(self) -> None:
        contract = get_automation_contract(self.registry, "rank_math_meta_description_update")
        self.assertIsNotNone(contract)
        assert contract is not None
        self.assertEqual(contract["contract_id"], "ac-rank-math-meta-description-update-v1")
        self.assertTrue(contract["requires_admin_confirmation"])
        self.assertTrue(contract["requires_before_state_capture"])
        self.assertTrue(contract["requires_rollback"])
        self.assertIn("recommend_only", contract["allowed_runtime_gates"])
        self.assertIn("rank_math_description", contract["allowed_target_fields"])

    def test_candidate_without_matching_contract_is_rejected(self) -> None:
        issues = candidate_contract_issues(
            {
                "action_type": "theme_h1_rewrite",
                "execution_lane": "admin_confirmed_assisted_resolution_only",
                "runtime_gate": "recommend_only",
                "active_seo_owner": "seo-by-rank-math/rank-math.php",
                "bound_domain": "electri-c-ity-studios-24-7.com",
                "target_domain": "electri-c-ity-studios-24-7.com",
                "target_field": "post_content",
                "approval_state": "admin_confirmation_required",
                "rollback_state": "ready_if_before_state_captured",
            },
            get_automation_contract(self.registry, "theme_h1_rewrite"),
        )
        self.assertIn("automation candidate has no matching contract", issues)

    def test_attach_contract_marks_candidate_contract_verified(self) -> None:
        contract = get_automation_contract(self.registry, "rank_math_meta_description_update")
        assert contract is not None
        candidate = {
            "action_type": "rank_math_meta_description_update",
            "execution_lane": "admin_confirmed_assisted_resolution_only",
            "runtime_gate": "recommend_only",
            "active_seo_owner": "seo-by-rank-math/rank-math.php",
            "bound_domain": "electri-c-ity-studios-24-7.com",
            "target_domain": "electri-c-ity-studios-24-7.com",
            "target_field": "rank_math_description",
            "approval_state": "admin_confirmation_required",
            "rollback_state": "ready_if_before_state_captured",
        }
        self.assertEqual(candidate_contract_issues(candidate, contract), [])
        enriched = attach_contract(candidate, contract)
        self.assertEqual(enriched["automation_contract_state"], "contract_verified")
        self.assertEqual(enriched["automation_contract_id"], "ac-rank-math-meta-description-update-v1")
        self.assertEqual(enriched["automation_contract_version"], "1.0")

    def test_contract_rejects_wrong_runtime_owner_or_domain(self) -> None:
        contract = get_automation_contract(self.registry, "rank_math_meta_description_update")
        assert contract is not None
        candidate = {
            "action_type": "rank_math_meta_description_update",
            "execution_lane": "admin_confirmed_assisted_resolution_only",
            "runtime_gate": "blocked",
            "active_seo_owner": "unknown/owner.php",
            "bound_domain": "electri-c-ity-studios-24-7.com",
            "target_domain": "other.example",
            "target_field": "rank_math_description",
            "approval_state": "admin_confirmation_required",
            "rollback_state": "ready_if_before_state_captured",
        }
        issues = candidate_contract_issues(candidate, contract)
        self.assertIn("automation candidate runtime_gate is not allowed by contract", issues)
        self.assertIn("automation candidate active_seo_owner is not allowed by contract", issues)
        self.assertIn("automation candidate target_domain must match bound_domain", issues)


if __name__ == "__main__":
    unittest.main()
