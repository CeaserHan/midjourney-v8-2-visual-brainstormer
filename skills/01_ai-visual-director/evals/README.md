# Forward evaluation

These cases test behavior that deterministic checks cannot judge reliably, such
as visual diversity, spatial continuity, subject separation, and whether two
model-specific prompts preserve the same content ledger.

## Procedure

1. Give an independent evaluator only `SKILL.md` and one raw prompt from
   `cases.json`. Do not reveal assertion names or prior outputs.
2. Save the complete response before judging it.
3. Run `scripts/validate_delivery.py` when the response has a deterministic
   delivery mode and target.
4. Judge every assertion independently as pass or fail and cite short evidence.
5. The case passes only if every assertion passes. Do not average away a protocol
   failure because the visual writing is strong.
6. Record model/runtime identity, date, result, and any variance worth retesting.

## Retest policy

- Retest a failure once with the exact same prompt in a fresh context to measure
  variance; do not rewrite the prompt during that retest.
- A skill change is regression-safe only when deterministic tests pass and no
  previously passing forward case becomes a repeatable failure.
- Keep failed runs. They are evidence, not clutter.

