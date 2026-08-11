"""Validate deterministic parts of an AI Visual Director delivery.

This module intentionally does not judge visual quality, historical accuracy,
composition quality, or semantic diversity. Those belong to forward evals.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


TARGETS = ("none", "mj", "gpt2")
MODES = (
    "first-round",
    "second-round",
    "r1",
    "r2",
    "single",
    "refine",
    "diagnose",
)

DEFAULT_COUNTS = {
    "first-round": 0,
    "second-round": 0,
    "r1": 12,
    "r2": 6,
    "single": 1,
    "refine": 4,
    "diagnose": 1,
}

CODE_BLOCK_PATTERN = re.compile(
    r"```(?:text)?[ \t]*\r?\n(?P<body>.*?)\r?\n```",
    re.DOTALL | re.IGNORECASE,
)
NUMBERED_HEADING_PATTERN = re.compile(r"^###\s+(\d+)\.\s+.+$", re.MULTILINE)
MJ_PARAMETER_PATTERN = re.compile(r"(?:^|\s)--[a-z][a-z0-9-]*\b", re.IGNORECASE)
GPT_LABEL_PATTERN = re.compile(
    r"^(?:Goal|Scene|Subjects|Composition|Visual treatment|Image inputs|Text|"
    r"Must preserve|Constraints|Change only|Keep unchanged):",
    re.MULTILINE | re.IGNORECASE,
)
OPEN_PLACEHOLDER_PATTERN = re.compile(
    r"\b(?:left open|unspecified|unconstrained)\b|保持开放|开放字段",
    re.IGNORECASE,
)
TEMPLATE_PLACEHOLDER_PATTERN = re.compile(
    r"\b(?:TBD|TODO)\b|Complete model-adapted prompt|\[(?:medium|subject|scene|prompt)[^\]]*\]",
    re.IGNORECASE,
)
MJ_EDIT_PROTOCOL_PATTERN = re.compile(
    r"\b(?:same|original|source image|preserve|unchanged|identical)\b",
    re.IGNORECASE,
)
FINAL_CONFIRMATION_PATTERNS = (
    re.compile(r"最终确认"),
    re.compile(r"请确认.{0,20}(?:生成|交付)"),
    re.compile(r"确认后.{0,20}(?:生成|交付)"),
)


@dataclass(frozen=True)
class ValidationResult:
    """Stable result returned by the delivery validator."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.errors


def _extract_prompt_blocks(delivery: str) -> tuple[str, ...]:
    return tuple(match.group("body").strip() for match in CODE_BLOCK_PATTERN.finditer(delivery))


def _expected_count(mode: str, override: int | None) -> int:
    if override is not None:
        if override < 0:
            raise ValueError("expected count must be zero or greater")
        return override
    return DEFAULT_COUNTS[mode]


def _validate_mode_scaffold(delivery: str, mode: str, errors: list[str]) -> None:
    required_headings = {
        "first-round": ("## 当前锁定", "## 第一轮：场景与任务"),
        "second-round": ("## 已锁定场景", "## 第二轮：媒介专属表现"),
        "r1": ("## 统一锁定",),
        "r2": ("## 固定内容",),
        "single": ("## 单条定稿",),
        "refine": ("## 保留与改变",),
        "diagnose": ("## 诊断",),
    }
    for heading in required_headings[mode]:
        if heading not in delivery:
            errors.append(f"Required heading `{heading}` is missing for mode `{mode}`.")

    if mode == "first-round" and "## 第二轮：媒介专属表现" in delivery:
        errors.append("First-round delivery must not include the second-round card.")
    if mode == "second-round" and "## 第一轮：场景与任务" in delivery:
        errors.append("Second-round delivery must not repeat the first-round card.")


def _validate_numbered_headings(
    delivery: str, mode: str, expected_count: int, errors: list[str]
) -> None:
    if mode not in {"r1", "r2", "refine"}:
        return

    numbers = [int(value) for value in NUMBERED_HEADING_PATTERN.findall(delivery)]
    expected = list(range(1, expected_count + 1))
    if numbers != expected:
        errors.append(
            "Numbered delivery headings must be consecutive and unique; "
            f"expected {expected}, received {numbers}."
        )


def _validate_prompt_block(
    block: str, target: str, mode: str, index: int, errors: list[str]
) -> None:
    label = f"Prompt block {index}"
    if not block:
        errors.append(f"{label} is empty.")
        return

    if OPEN_PLACEHOLDER_PATTERN.search(block):
        errors.append(f"{label} contains an open-field meta placeholder.")
    if TEMPLATE_PLACEHOLDER_PATTERN.search(block):
        errors.append(f"{label} contains an unreplaced template placeholder.")

    if target == "mj":
        if MJ_PARAMETER_PATTERN.search(block):
            errors.append(f"{label} contains a Midjourney parameter; settings must stay outside.")
        if GPT_LABEL_PATTERN.search(block):
            errors.append(f"{label} contains GPT Image 2 production labels.")
        if mode == "refine" and MJ_EDIT_PROTOCOL_PATTERN.search(block):
            errors.append(
                f"{label} uses referential edit protocol instead of a complete positive restatement."
            )
    elif target == "gpt2" and MJ_PARAMETER_PATTERN.search(block):
        errors.append(f"{label} contains Midjourney parameter syntax.")


def validate_delivery(
    delivery: str,
    *,
    target: str,
    mode: str,
    expected_count: int | None = None,
) -> ValidationResult:
    """Validate a complete Markdown delivery without performing I/O."""

    if target not in TARGETS:
        raise ValueError(f"unsupported target: {target}")
    if mode not in MODES:
        raise ValueError(f"unsupported mode: {mode}")
    if target == "none" and mode not in {"first-round", "second-round"}:
        raise ValueError("target `none` is only valid for selection-card modes")
    if target != "none" and mode in {"first-round", "second-round"}:
        raise ValueError("selection-card modes must use target `none`")

    errors: list[str] = []
    warnings: list[str] = []
    count = _expected_count(mode, expected_count)
    blocks = _extract_prompt_blocks(delivery)

    _validate_mode_scaffold(delivery, mode, errors)

    if len(blocks) != count:
        errors.append(
            f"Mode `{mode}` requires {count} prompt block(s); received {len(blocks)}."
        )

    _validate_numbered_headings(delivery, mode, count, errors)
    for index, block in enumerate(blocks, start=1):
        _validate_prompt_block(block, target, mode, index, errors)

    for pattern in FINAL_CONFIRMATION_PATTERNS:
        if pattern.search(delivery):
            errors.append("Delivery contains a forbidden third/final confirmation request.")
            break

    return ValidationResult(errors=tuple(errors), warnings=tuple(warnings))


def format_result(result: ValidationResult) -> str:
    lines = [
        "PASS" if result.passed else "FAIL",
        f"Errors: {len(result.errors)}",
        f"Warnings: {len(result.warnings)}",
    ]
    if result.errors or result.warnings:
        lines.append("")
        lines.extend(f"ERROR: {message}" for message in result.errors)
        lines.extend(f"WARNING: {message}" for message in result.warnings)
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate deterministic protocol rules in an AI Visual Director delivery."
    )
    parser.add_argument("file", help="UTF-8 Markdown delivery to validate")
    parser.add_argument("--target", choices=TARGETS, required=True)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--expected-count", type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        delivery = Path(args.file).read_text(encoding="utf-8")
        result = validate_delivery(
            delivery,
            target=args.target,
            mode=args.mode,
            expected_count=args.expected_count,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"INPUT ERROR: {exc}", file=sys.stderr)
        return 2

    print(format_result(result))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

