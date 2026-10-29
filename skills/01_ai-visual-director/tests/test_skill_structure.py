"""Static contract and package-structure tests for AI Visual Director."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = TESTS_DIR.parent
PLUGIN_ROOT = SKILL_ROOT.parents[1]
SKILL_PATH = SKILL_ROOT / "SKILL.md"
REFERENCES_DIR = SKILL_ROOT / "references"
AGENT_METADATA_PATH = SKILL_ROOT / "agents" / "openai.yaml"
PLUGIN_MANIFEST_PATH = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"

FRONTMATTER_PATTERN = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*\n", re.DOTALL)
FRONTMATTER_KEY_PATTERN = re.compile(r"^([a-zA-Z0-9_-]+):\s*(.*)$", re.MULTILINE)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)(?:#[^)]+)?\)")


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        raise AssertionError("SKILL.md is missing YAML frontmatter")
    values: dict[str, str] = {}
    for key, value in FRONTMATTER_KEY_PATTERN.findall(match.group("body")):
        values[key] = value.strip().strip('"\'')
    return values


class SkillPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = SKILL_PATH.read_text(encoding="utf-8")
        cls.frontmatter = parse_frontmatter(cls.skill_text)

    def test_frontmatter_contract_and_folder_name(self) -> None:
        self.assertEqual(set(self.frontmatter), {"name", "description"})
        self.assertEqual(self.frontmatter["name"], SKILL_ROOT.name)
        self.assertTrue(self.frontmatter["description"])

    def test_plugin_manifest_points_to_skills_directory(self) -> None:
        if not PLUGIN_MANIFEST_PATH.is_file():
            self.skipTest("standalone skill install without a Codex plugin wrapper")
        manifest = json.loads(PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "midjourney-v8-2-visual-brainstormer")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertIn("interface", manifest)

    def test_openai_ui_metadata_is_present(self) -> None:
        metadata = AGENT_METADATA_PATH.read_text(encoding="utf-8")
        for key in ("display_name:", "short_description:", "default_prompt:"):
            with self.subTest(key=key):
                self.assertIn(key, metadata)

    def test_all_relative_markdown_references_resolve(self) -> None:
        markdown_files = [SKILL_PATH, *sorted(REFERENCES_DIR.rglob("*.md"))]
        unresolved: list[str] = []
        for markdown_file in markdown_files:
            text = markdown_file.read_text(encoding="utf-8")
            for relative_path in MARKDOWN_LINK_PATTERN.findall(text):
                target = (markdown_file.parent / relative_path).resolve()
                if not target.is_file():
                    unresolved.append(f"{markdown_file.name}: {relative_path}")
        self.assertEqual(unresolved, [])

    def test_required_routing_references_exist(self) -> None:
        for filename in (
            "intake-and-routing.md",
            "output-contract.md",
            "model-adapters.md",
            "midjourney.md",
            "gpt-image.md",
            "keyframes.md",
            "styles/README.md",
        ):
            with self.subTest(filename=filename):
                self.assertTrue((REFERENCES_DIR / filename).is_file())

    def test_runtime_skill_does_not_invoke_test_tooling(self) -> None:
        self.assertNotIn("validate_delivery.py", self.skill_text)
        self.assertNotIn("evals/cases.json", self.skill_text)


class CrossFileContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL_PATH.read_text(encoding="utf-8")
        cls.intake = (REFERENCES_DIR / "intake-and-routing.md").read_text(
            encoding="utf-8"
        )
        cls.output = (REFERENCES_DIR / "output-contract.md").read_text(
            encoding="utf-8"
        )
        cls.adapters = (REFERENCES_DIR / "model-adapters.md").read_text(
            encoding="utf-8"
        )
        cls.mj = (REFERENCES_DIR / "midjourney.md").read_text(
            encoding="utf-8"
        )

    def test_open_and_ai_design_semantics_remain_explicit(self) -> None:
        for text in (self.skill, self.intake, self.output):
            with self.subTest(source=text[:30]):
                self.assertIn("0", text)
                self.assertIn("X", text)
                self.assertIn("开放", text)
        self.assertIn("开放字段都不得在适配阶段被补全", self.adapters)

    def test_r1_and_r2_default_counts_are_stable(self) -> None:
        self.assertIn("R1 视觉探索", self.skill)
        self.assertIn("默认十二", self.skill)
        self.assertIn("R2 固定场景执行", self.skill)
        self.assertIn("默认六", self.skill)
        self.assertIn("默认恰好十二条", self.output)
        self.assertIn("用户未指定数量时输出六条", self.output)

    def test_second_round_delivers_without_third_confirmation(self) -> None:
        self.assertIn("不发送第三张确认卡", self.skill)
        self.assertIn("不发送“最终确认卡”", self.output)

    def test_midjourney_prompt_parameter_separation_is_stable(self) -> None:
        self.assertIn("无参数", self.skill)
        self.assertIn("不得包含任何以连续双短横线开头", self.mj)
        self.assertIn("不写 `Goal:`", self.adapters)

    def test_gpt_image_edit_protocol_is_stable(self) -> None:
        self.assertIn("Change only", self.adapters)
        self.assertIn("Keep unchanged", self.adapters)
        self.assertIn("GPT Image 输出不得包含 Midjourney 参数", self.adapters)


class V03ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL_PATH.read_text(encoding="utf-8")
        cls.styles = REFERENCES_DIR / "styles"

    def test_keyframe_mode_is_routed(self) -> None:
        self.assertIn("R4 关键帧", self.skill)
        self.assertIn("keyframes.md", self.skill)

    def test_prompt_hygiene_rules_are_stated(self) -> None:
        self.assertIn("O（用途）永不直译进英文提示词", self.skill)
        self.assertIn("不复制粘贴尾巴", self.skill)
        self.assertIn("M 本身成立所必需的最少识别信号", self.skill)

    def test_style_cards_tag_signals_and_stay_short(self) -> None:
        for card in sorted(self.styles.glob("*.md")):
            if card.name in {"README.md", "_template.md"}:
                continue
            with self.subTest(card=card.name):
                text = card.read_text(encoding="utf-8")
                self.assertIn("[M]", text)
                self.assertLessEqual(len(text.splitlines()), 40)

    def test_skill_md_stays_within_budget(self) -> None:
        self.assertLessEqual(len(self.skill.splitlines()), 200)


class V031FieldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL_PATH.read_text(encoding="utf-8")
        cls.intake = (REFERENCES_DIR / "intake-and-routing.md").read_text(encoding="utf-8")
        cls.media = (REFERENCES_DIR / "media-modules.md").read_text(encoding="utf-8")

    def test_mood_field_exists_and_output_purpose_left_round_one(self) -> None:
        self.assertIn("| B | 情绪／叙事基调 |", self.intake)
        self.assertNotIn("| O | 输出用途 |", self.intake)
        self.assertIn("`Z R U Y G B T L P E W M`", self.skill)

    def test_r1_skips_lpe(self) -> None:
        self.assertIn("R1 视觉探索不列 L/P/E", self.skill)
        self.assertIn("R1 视觉探索：不列 L/P/E", self.intake)

    def test_lighting_moved_from_q_to_c(self) -> None:
        self.assertNotIn("照明过程：可用光、直闪、离机灯等", self.media)
        self.assertIn("照明方式不属于 Q", self.skill)

    def test_conditional_aspect_and_layout_fields(self) -> None:
        self.assertIn("| F | 画幅 |", self.intake)
        self.assertIn("| O | 用途与版面 |", self.intake)


if __name__ == "__main__":
    unittest.main()
