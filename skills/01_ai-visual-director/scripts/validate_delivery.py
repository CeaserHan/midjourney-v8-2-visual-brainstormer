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


TARGETS = ("none", "mj", "gpt2", "both")
MODES = (
    "first-round",
    "second-round",
    "r1",
    "r2",
    "single",
    "refine",
    "diagnose",
    "keyframe",
)

DEFAULT_COUNTS = {
    "first-round": 0,
    "second-round": 0,
    "r1": 12,
    "r2": 6,
    "single": 1,
    "refine": 4,
    "diagnose": 1,
    "keyframe": 2,
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
META_PURPOSE_PATTERN = re.compile(
    r"\bfor (?:a|an|the)\s+(?:[\w-]+\s+){0,3}"
    r"(?:magazine|report|pitch|portfolio|campaign|presentation|client|deck)\b",
    re.IGNORECASE,
)
TAIL_WORDS = 10
SHARED_NGRAM = 8
SHARED_NGRAM_MIN_BLOCKS = 3
MJ_SOFT_WORD_LIMIT = 110
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


LABEL_PATTERN = re.compile(r"\*\*(Midjourney|GPT Image)\*\*\s*$", re.IGNORECASE)


def _block_targets(delivery: str, target: str) -> tuple[str, ...]:
    """Per-block target; in `both` mode read the **Midjourney** / **GPT Image** label above each block."""
    targets: list[str] = []
    for match in CODE_BLOCK_PATTERN.finditer(delivery):
        if target != "both":
            targets.append(target)
            continue
        preceding = delivery[: match.start()].rstrip().splitlines()[-3:]
        label = ""
        for line in reversed(preceding):
            found = LABEL_PATTERN.search(line.strip())
            if found:
                label = found.group(1).casefold()
                break
        targets.append("mj" if label == "midjourney" else "gpt2" if label == "gpt image" else "both")
    return tuple(targets)


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
        "keyframe": ("## 连续性卡",),
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

    if META_PURPOSE_PATTERN.search(block):
        errors.append(f"{label} translates purpose or delivery context into the prompt.")
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
    elif target in {"gpt2", "both"} and MJ_PARAMETER_PATTERN.search(block):
        errors.append(f"{label} contains Midjourney parameter syntax.")


def _tail(block: str) -> tuple[str, ...]:
    words = re.findall(r"[a-z0-9'-]+", block.casefold())
    return tuple(words[-TAIL_WORDS:]) if len(words) >= TAIL_WORDS else ()


def _validate_repeated_tails(blocks: Sequence[str], errors: list[str]) -> None:
    seen: dict[tuple[str, ...], int] = {}
    for index, block in enumerate(blocks, start=1):
        tail = _tail(block)
        if not tail:
            continue
        if tail in seen:
            errors.append(
                f"Prompt blocks {seen[tail]} and {index} end with the same {TAIL_WORDS} words; "
                "rewrite shared style choices per image."
            )
        else:
            seen[tail] = index


def _validate_shared_phrases(blocks: Sequence[str], errors: list[str]) -> None:
    """Flag long word sequences pasted into many prompts of one set."""
    if len(blocks) < SHARED_NGRAM_MIN_BLOCKS:
        return
    owners: dict[tuple[str, ...], set[int]] = {}
    for index, block in enumerate(blocks, start=1):
        words = re.findall(r"[a-z0-9'-]+", block.casefold())
        for start in range(len(words) - SHARED_NGRAM + 1):
            owners.setdefault(tuple(words[start : start + SHARED_NGRAM]), set()).add(index)
    pasted = [gram for gram, ids in owners.items() if len(ids) >= SHARED_NGRAM_MIN_BLOCKS]
    if pasted:
        sample = " ".join(pasted[0])
        errors.append(
            f"{len(pasted)} phrase(s) of {SHARED_NGRAM}+ words repeat across "
            f"{SHARED_NGRAM_MIN_BLOCKS}+ prompts (e.g. `{sample}`); rewrite shared style per image."
        )


def _word_count_warnings(blocks: Sequence[str], target: str, warnings: list[str]) -> None:
    if target != "mj":
        return
    for index, block in enumerate(blocks, start=1):
        count = len(re.findall(r"[A-Za-z0-9'-]+", block))
        if count > MJ_SOFT_WORD_LIMIT:
            warnings.append(
                f"Prompt block {index} has {count} words; "
                f"Midjourney prompts usually work best under {MJ_SOFT_WORD_LIMIT}."
            )


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

    block_count = count * 2 if target == "both" else count
    if len(blocks) != block_count:
        errors.append(
            f"Mode `{mode}` requires {block_count} prompt block(s); received {len(blocks)}."
        )

    _validate_numbered_headings(delivery, mode, count, errors)
    block_targets = _block_targets(delivery, target)
    for index, (block, block_target) in enumerate(zip(blocks, block_targets), start=1):
        _validate_prompt_block(block, block_target, mode, index, errors)
    if target == "both" and "both" in block_targets:
        warnings.append("Some prompt blocks lack a **Midjourney** / **GPT Image** label; only shared checks ran on them.")
    # Repetition checks apply only to R1, where every direction has different content.
    # R2, refinement and keyframes must restate the same subject, place and anchors.
    if mode == "r1":
        for group in ("mj", "gpt2"):
            group_blocks = [b for b, bt in zip(blocks, block_targets) if bt == group]
            _validate_repeated_tails(group_blocks, errors)
            _validate_shared_phrases(group_blocks, errors)
    for group in ("mj",):
        group_blocks = [b for b, bt in zip(blocks, block_targets) if bt == group]
        _word_count_warnings(group_blocks, group, warnings)

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

