"""Tests for deterministic delivery-protocol validation."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = TESTS_DIR.parent
SCRIPTS_DIR = SKILL_ROOT / "scripts"
VALIDATOR_PATH = SCRIPTS_DIR / "validate_delivery.py"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_delivery import validate_delivery  # noqa: E402


def numbered_delivery(title: str, count: int, prompt: str = "A complete visual prompt") -> str:
    parts = [title]
    for index in range(1, count + 1):
        parts.extend(
            (
                f"### {index}. 方案 {index}",
                "",
                "```text",
                f"{prompt} {index}",
                "```",
            )
        )
    return "\n".join(parts)


class DeliveryValidatorTests(unittest.TestCase):
    def test_valid_midjourney_single_with_external_settings(self) -> None:
        delivery = """## 单条定稿

```text
Live-action cinematic still in a rainy station hall.
```

官网设置：Version 8.2，Aspect Ratio 16:9
"""
        result = validate_delivery(delivery, target="mj", mode="single")
        self.assertTrue(result.passed, result.errors)

    def test_midjourney_rejects_parameters_and_gpt_labels(self) -> None:
        delivery = """## 单条定稿

```text
Goal: create a rainy station --ar 16:9 --v 8.2
```
"""
        result = validate_delivery(delivery, target="mj", mode="single")
        self.assertFalse(result.passed)
        self.assertTrue(any("parameter" in error for error in result.errors))
        self.assertTrue(any("production labels" in error for error in result.errors))

    def test_gpt2_accepts_labels_but_rejects_midjourney_parameters(self) -> None:
        valid = """## 单条定稿

```text
Goal: Create a historical street scene.
Scene: Beijing in 2002.
```
"""
        invalid = valid.replace("Beijing in 2002.", "Beijing in 2002. --ar 3:2")
        self.assertTrue(validate_delivery(valid, target="gpt2", mode="single").passed)
        self.assertFalse(validate_delivery(invalid, target="gpt2", mode="single").passed)

    def test_r1_requires_twelve_consecutive_directions(self) -> None:
        valid = numbered_delivery("## 统一锁定", 12)
        missing = numbered_delivery("## 统一锁定", 11)
        self.assertTrue(validate_delivery(valid, target="mj", mode="r1").passed)
        result = validate_delivery(missing, target="mj", mode="r1")
        self.assertFalse(result.passed)
        self.assertTrue(any("requires 12" in error for error in result.errors))

    def test_r2_supports_user_selected_count_and_rejects_duplicate_numbers(self) -> None:
        valid = numbered_delivery("## 固定内容", 3)
        duplicate = valid.replace("### 3. 方案 3", "### 2. 方案 3")
        self.assertTrue(
            validate_delivery(
                valid, target="mj", mode="r2", expected_count=3
            ).passed
        )
        result = validate_delivery(
            duplicate, target="mj", mode="r2", expected_count=3
        )
        self.assertFalse(result.passed)
        self.assertTrue(any("consecutive" in error for error in result.errors))

    def test_selection_cards_cannot_contain_final_prompt_blocks(self) -> None:
        first_round = """## 当前锁定

## 第一轮：场景与任务

```text
Premature prompt
```
"""
        result = validate_delivery(first_round, target="none", mode="first-round")
        self.assertFalse(result.passed)
        self.assertTrue(any("requires 0" in error for error in result.errors))

    def test_open_and_template_placeholders_are_rejected(self) -> None:
        for phrase in ("style left open", "unconstrained equipment", "TBD"):
            with self.subTest(phrase=phrase):
                delivery = f"""## 单条定稿

```text
A complete scene with {phrase}.
```
"""
                result = validate_delivery(delivery, target="mj", mode="single")
                self.assertFalse(result.passed)

    def test_midjourney_refine_requires_positive_restatement(self) -> None:
        valid = numbered_delivery("## 保留与改变", 4, "A complete revised rainy scene")
        invalid = valid.replace(
            "A complete revised rainy scene 1",
            "Keep the same original scene and preserve the source image",
        )
        self.assertTrue(validate_delivery(valid, target="mj", mode="refine").passed)
        result = validate_delivery(invalid, target="mj", mode="refine")
        self.assertFalse(result.passed)
        self.assertTrue(any("positive restatement" in error for error in result.errors))

    def test_third_confirmation_request_is_rejected(self) -> None:
        delivery = """## 单条定稿

```text
A complete visual prompt.
```

请确认后我再生成最终版本。
"""
        result = validate_delivery(delivery, target="mj", mode="single")
        self.assertFalse(result.passed)
        self.assertTrue(any("confirmation" in error for error in result.errors))


class DeliveryValidatorCliTests(unittest.TestCase):
    def test_cli_exit_codes(self) -> None:
        valid = "## 单条定稿\n\n```text\nA complete visual prompt.\n```\n"
        invalid = valid.replace("A complete visual prompt.", "A scene --v 8.2")
        with tempfile.TemporaryDirectory() as temporary_directory:
            valid_path = Path(temporary_directory) / "valid.md"
            invalid_path = Path(temporary_directory) / "invalid.md"
            valid_path.write_text(valid, encoding="utf-8")
            invalid_path.write_text(invalid, encoding="utf-8")
            valid_run = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR_PATH),
                    str(valid_path),
                    "--target",
                    "mj",
                    "--mode",
                    "single",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            invalid_run = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR_PATH),
                    str(invalid_path),
                    "--target",
                    "mj",
                    "--mode",
                    "single",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
        self.assertEqual(valid_run.returncode, 0)
        self.assertIn("PASS", valid_run.stdout)
        self.assertEqual(invalid_run.returncode, 1)
        self.assertIn("FAIL", invalid_run.stdout)

    def test_cli_missing_file_returns_input_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR_PATH),
                "missing-delivery.md",
                "--target",
                "mj",
                "--mode",
                "single",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("INPUT ERROR", completed.stderr)


class V03ValidatorTests(unittest.TestCase):
    def test_rejects_purpose_meta_in_prompt(self) -> None:
        delivery = """## 单条定稿

```text
Live-action film still for a city-image magazine report, commuters on a pier.
```
"""
        result = validate_delivery(delivery, target="mj", mode="single")
        self.assertFalse(result.passed)
        self.assertTrue(any("purpose" in error for error in result.errors))

    def test_rejects_copied_style_tail(self) -> None:
        tail = "hong kong new wave realism photographed on 35mm color negative with natural grain"
        delivery = numbered_delivery("## 统一锁定", 2, prompt="Commuters cross the pier, " + tail)
        delivery = delivery.replace(tail + " 1", tail).replace(tail + " 2", tail)
        result = validate_delivery(delivery, target="mj", mode="r1", expected_count=2)
        self.assertFalse(result.passed)
        self.assertTrue(any("same 10 words" in error for error in result.errors))

    def test_keyframe_requires_continuity_card_and_two_frames(self) -> None:
        valid = """## 连续性卡

- 角色：…

### KF1 首帧

```text
A man in a grey raincoat pushes the door open, lit by one hallway bulb.
```

### KF2 尾帧

```text
A man in a grey raincoat steps into the dark room, lit by one hallway bulb behind him.
```
"""
        self.assertTrue(validate_delivery(valid, target="mj", mode="keyframe").passed)
        missing = valid.replace("## 连续性卡", "## 卡")
        self.assertFalse(validate_delivery(missing, target="mj", mode="keyframe").passed)

    def test_both_target_doubles_block_count(self) -> None:
        delivery = """## 单条定稿

```text
Watercolor of a late-night Chinatown noodle shop.
```

```text
Scene: A late-night noodle shop in Chinatown.
```
"""
        self.assertTrue(validate_delivery(delivery, target="both", mode="single").passed)

    def test_long_midjourney_prompt_warns(self) -> None:
        delivery = "## 单条定稿\n\n```text\n" + " ".join(["word"] * 130) + "\n```\n"
        result = validate_delivery(delivery, target="mj", mode="single")
        self.assertTrue(result.passed)
        self.assertTrue(result.warnings)


class V032ValidatorTests(unittest.TestCase):
    def test_r2_may_restate_fixed_subject_and_place(self) -> None:
        fixed = "a woman in a grey trench coat waits at the corner payphone of the 1930s pharmacy"
        parts = ["## 固定内容"]
        for index, view in enumerate(("low angle from the doorway", "high angle from the stair", "long lens from across the street"), 1):
            parts += [f"### {index}. 机位 {index}", "", "```text", f"Film still, {view}: {fixed}, rain light at the door {index}.", "```"]
        result = validate_delivery("\n".join(parts), target="mj", mode="r2", expected_count=3)
        self.assertTrue(result.passed, result.errors)

    def test_both_mode_catches_gpt_labels_inside_midjourney_block(self) -> None:
        delivery = """## 单条定稿

**Midjourney**
```text
Scene: a noodle shop in Chinatown at night.
```

**GPT Image**
```text
Scene: a noodle shop in Chinatown at night.
```
"""
        result = validate_delivery(delivery, target="both", mode="single")
        self.assertFalse(result.passed)
        self.assertTrue(any("Prompt block 1" in e and "production labels" in e for e in result.errors))


if __name__ == "__main__":
    unittest.main()

