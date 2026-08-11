"""Schema and coverage tests for forward-evaluation cases."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = TESTS_DIR.parent
EVAL_CASES_PATH = SKILL_ROOT / "evals" / "cases.json"

REQUIRED_CATEGORIES = {
    "open_state",
    "ai_design_authorization",
    "direct_r3",
    "r1_diversity",
    "r2_continuity",
    "model_separation",
    "multi_subject",
    "refinement",
    "diagnosis",
}

ALLOWED_ASSERTIONS = {
    "first_round_only",
    "no_selection_card",
    "open_fields_omitted",
    "x_decisions_disclosed",
    "r1_count_12",
    "r1_content_diversity",
    "prompt_count_matches_requested",
    "r2_fixed_content",
    "r2_camera_signatures",
    "spatial_topology_preserved",
    "mj_no_parameters",
    "mj_no_gpt_protocol",
    "gpt_no_mj_syntax",
    "same_content_ledger",
    "lead_identities_separated",
    "crowd_remains_secondary",
    "no_two_round_restart",
    "single_variable_variants",
    "root_cause_identified",
    "minimal_repair",
}


class ForwardEvalCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads(EVAL_CASES_PATH.read_text(encoding="utf-8"))["cases"]

    def test_case_ids_are_unique(self) -> None:
        ids = [case["id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))

    def test_required_categories_are_covered(self) -> None:
        categories = {case["category"] for case in self.cases}
        self.assertTrue(REQUIRED_CATEGORIES.issubset(categories))

    def test_case_schema_and_assertions(self) -> None:
        for case in self.cases:
            with self.subTest(case=case.get("id")):
                self.assertEqual(
                    set(case), {"id", "category", "prompt", "assertions"}
                )
                self.assertTrue(case["id"])
                self.assertTrue(case["prompt"].strip())
                self.assertGreaterEqual(len(case["assertions"]), 1)
                self.assertTrue(set(case["assertions"]).issubset(ALLOWED_ASSERTIONS))

    def test_prompts_do_not_leak_expected_answers(self) -> None:
        forbidden = ("测试这个skill", "评审这个skill", "预期答案", "故意失败")
        for case in self.cases:
            normalized = case["prompt"].casefold()
            with self.subTest(case=case["id"]):
                self.assertFalse(any(phrase in normalized for phrase in forbidden))


if __name__ == "__main__":
    unittest.main()
