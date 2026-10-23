# Benchmark snapshot

Research cutoff: October 22, 2026, America/New_York. These are retrieved publisher results, not tests run by AI UPDATE. Live pages can change. Score differences do not prove statistical separation.

| Category | Exact listed model/configuration | Result | Source |
|---|---|---:|---|
| Composite, AA Intelligence Index v4.3.2 | Claude Opus 5.5 (Max, Default Fallback) | 58 | [AA Index](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index) |
| Composite runner-up configurations | Claude Sonnet 5.5 (Max, Default Fallback); Claude Opus 5.5 (Xhigh, Default Fallback) | 56 each | AA Index |
| Agentic terminal work, Terminal-Bench 4.0, AA implementation | Claude Sonnet 5.5 (Max, Default Fallback) | 63.6% | [AA Terminal-Bench](https://artificialanalysis.ai/evaluations/terminalbench-4-0) |
| Agentic terminal work, next listed configurations | Claude Opus 5.5 (Max, Default Fallback); Claude Opus 5.5 (Xhigh, Default Fallback) | 59.6% each | AA Terminal-Bench |
| Academic reasoning, HLE, AA implementation | Claude Opus 5.5 (Max, Default Fallback) | 61.4% | [AA HLE](https://artificialanalysis.ai/evaluations/humanitys-last-exam) |
| Professional PDF reasoning, GDP.pdf all-pass, AA implementation | Muse Wonder Full (Max) | 32.6% | [AA GDP.pdf](https://artificialanalysis.ai/evaluations/gdp-pdf) |
| Professional PDF reasoning, next listed configurations | GPT-6 Astra (Xhigh); GPT-6.1 Sol (High) | 32.2%; 32.0% | AA GDP.pdf |
| Text preference, Arena overall | Gemini 4 Argon (High) | 1517 ±7, preliminary | [Arena](https://arena.ai/leaderboard/chat/text), displayed Oct 22 |

## Interpretation

These categories measure different things. An index point, a preference rating and a pass percentage are not interchangeable. Arena extraction exposes adjustment controls but does not establish their selected state, so do not label this October 22 record as style-controlled. Its next listed entries, Opus 5.5 (High) 1509 ±7 and Muse Wonder (Max) 1509 ±8, have overlapping displayed intervals with the leader.

The AA Terminal-Bench implementation uses mini-swe-agent, pass@1 averaged across three repeats for each of 66 tasks. Vendor figures from another harness cannot silently replace those numbers. GDP.pdf all-pass requires every criterion to pass. It is stricter than mean criterion pass rate and does not measure a general user failure probability.

No independently supported universal winner in writing, voice, conversational usefulness or agent safety is established here. No same-prompt comparison was run for this package. Provider demos remain provider demos. Do not fabricate missing ranks or model outputs.

The repo's October 12/13 charts remain historical assets. This file records the October 22 refresh without overwriting those earlier snapshots.
