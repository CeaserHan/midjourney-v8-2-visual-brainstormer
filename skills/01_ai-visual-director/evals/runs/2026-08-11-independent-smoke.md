# Independent forward smoke run — 2026-08-11

Runtime: three isolated Codex subagent contexts. Each evaluator received only the
skill path and a natural user request; tests, assertions, and expected outcomes
were withheld.

## Results

| Run | Coverage | Result | Evidence |
| --- | --- | --- | --- |
| A | Open-state handling from an era-and-place seed | PASS | All requested `0` fields remained explicitly open; the response asked only for the unresolved work mode and did not invent content. |
| B | Fixed-scene R2 spatial continuity | FAIL | Three camera signatures preserved every wall, doorway, light-source, and crowd-layer relationship, but the delivery contained zero copyable prompt blocks instead of the requested three. |
| C | Dual-model separation with one shared ledger | PASS | Both versions kept the same scene facts; the Midjourney block used plain descriptive prose without parameters or GPT labels, while the GPT Image 2 block used labeled production instructions without Midjourney syntax. |

Score: **2/3 cases passed**. The failure is retained as a baseline signal. No
runtime skill text was changed in response; this addition is evaluation evidence
only.

