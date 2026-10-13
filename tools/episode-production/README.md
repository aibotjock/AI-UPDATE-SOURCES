# AI UPDATE episode production

This folder provides a predeclared comparison runner and a narration-led video assembly foundation. It does not create verified sources, authentic model outputs, natural narration, an editable deck, or a completed episode by itself.

The regular five segments are the main takeaway, what changed, the benchmark scoreboard, the same-prompt comparison, and your choice and what is next. Episode 01 puts more time into interpreting benchmarks. A practical lesson remains an optional special segment for a verified best or new item.

## Sequence

1. Read the repository source/asset indexes, dated benchmark records, evergreen notes, prior runs and corrections. Keep actively maintained sources in the news workflow. Static papers and old data remain supporting material with their dates.
2. Verify mutable facts on the actual America/New_York script date. Keep publication, measurement and retrieval dates separate. Refresh after midnight or a source correction.
3. Complete the predeclared real comparison. The Episode 01 registration is under `library/reproducibility/episodes/01-2026-10-13/test-registration/`. Its expected JSON is a grading key, never a model output. See [comparison instructions](COMPARISON.md).
4. Review the script and storyboard together from the completed evidence. Split observation-level source notes into sentence-level claims. Do not narrate results of an unperformed comparison. Accurate recurring narration may be reused with original dates and appropriate unchanged labels.
5. Obtain authorized narration in scene segments, review voice/pronunciation, measure the audio and settle the timeline. Create editable PowerPoint scenes and the full animated explainer against actual audio. Give scenes distinct compositions and readable citations.
6. Assemble checked images/narration/SFX and verified caption cues with [the renderer](RENDERER.md), or use a richer compatible editor for progressive graphics, recordings and other planned motion. The supplied renderer implements still frames and fades only.
7. Watch and listen to the whole export, check evidence/readability/permissions/captions, then package the deck, Word/plain-text spoken script, 1080p video, audio stems, captions, manifest, references, actual test artifacts and prepared description. Extract the 120-second excerpt from settled episode content. YouTube publication needs separate authorization.

## Commands from repository root

```bash
python3 tools/episode-production/compare.py dry-run --plan library/reproducibility/episodes/01-2026-10-13/test-registration/plan.json
python3 tools/episode_gate.py library/reproducibility/episodes/01-2026-10-13/scene-manifest.json --stage research
python3 tools/episode-production/render_episode.py validate library/reproducibility/episodes/01-2026-10-13/scene-manifest.json --output /tmp/ai-update-review
python3 -m unittest discover -s tools/episode-production -v
python3 -m unittest discover -s tests -v
```

Execution requires exact provider configuration, verified token/caching semantics, available credentials and an explicit authorized spending cap. No budget is authorized by the example configuration. Missing usage, uncertain billing or failed attempts remain visible. Machine readiness checks require human authenticity and editorial review.

## Current status

Read [Episode 01 preparation and blockers](../../library/reproducibility/episodes/01-2026-10-13/README.md). No final episode, channel-run test, final captions or publication is claimed. Planned runtime is provisional until real audio and evidence exist.
