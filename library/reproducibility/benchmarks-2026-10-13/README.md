# Source-cited benchmark graphics

52 original SVG charts derived from three primary benchmark publishers' captured numerical records. They supplement the media library and are not substitutes for actual same-prompt model outputs or verified current cloud availability.

## Sources and snapshots

- Artificial Analysis Intelligence Index **v4.3.2**: captured October 13, 2026 UTC / October 12 Eastern. The captured page embeds 32 source-selected model configurations and their component/evaluation scores. This is not a complete history of every model Artificial Analysis has evaluated. Individual evaluation dates were not provided by the captured records. Exact reasoning effort, fallback qualifiers, and model names are retained.
- Arena Text: **overall, style control enabled**, vote cutoff **October 8, 2026 at 14:00 UTC**. Captured October 13 UTC. The source has 414 model rows; 364 have named organizations and are eligible for these charts. No developer identity is guessed for missing organizations. Source bootstrap score intervals are shown. Preliminary source entries are labeled. These are human preference measurements, not direct factual-accuracy measurements.
- LiveBench **June 25, 2026** CSV release: 70 model/configuration rows. Three charts display individual Python, summarization and code-generation task scores. These are deliberately labeled historical June coverage, not October leaders and not computed overall/category scores.

Sources, capture dates, raw capture hashes and benchmark versions are saved in `data/sources.json`. Full source HTML captures remain outside this distributable directory. Only necessary factual numerical records are included in `data/`.

`data/arena-selection-provenance.json` records the exact parsed adjustment, category, cutoff and interval field paths. The selected leaderboard metadata explicitly has `params.styleControl: true`, `params.category: overall` and an ID containing `text-overall-style_control`; its 414 entries were matched in order against the 414 visible table rows. The source UI listing several possible adjustments is not used to infer the selected adjustment.

## Chart inventory

- 26 Artificial Analysis graphics: full captured cohort and top 20 index comparisons, strongest evaluated setting per developer, ten component leaderboards, six within-provider comparisons, two separate-metric capability profiles and five additional evaluation leaderboards.
- 23 Arena graphics: top 20, named-provider full reference poster, strongest listed setting per named provider, ten readable within-provider comparisons, and ten complete within-provider reference posters. Full posters retain lower-scoring/low-cost configurations as well as the strongest configurations; published score order is not a claim about cost or cloud availability.
- 3 LiveBench historical task comparisons.

The full Arena poster is a tall reference asset rather than a single slide. Use crops or subsets in episodes. Same-provider cohorts show source-listed configurations and may include older configurations; they do not assert that every model is presently available for cloud use. Developer names are reproduced from the source, including `SpaceXAI` and `Z AI`; they are not independently asserted branding changes.

## Interpretation rules

1. Cloud service availability, host/provider, account plan, region, and present-day prices require separate primary-source verification before making a user recommendation.
2. Scores from different benchmarks are never summed, averaged or treated as interchangeable. The capability matrices retain seven distinct percentage metrics.
3. Elo/rating metrics use point-and-interval plots rather than truncated bars. AA index and task scores use bars; signed Omniscience scores can legitimately be negative.
4. AA GDPval and Briefcase intervals are source-provided 95% confidence bounds. Arena intervals are labeled source bootstrap intervals; no confidence level is guessed. Other charts display point estimates and visibly state that uncertainty is not supplied for the displayed metric.
5. Point-estimate leaders are not proof of statistically significant or universal superiority. Agentic evaluations also measure supporting agent/tool environments. Exact configuration names remain visible.
6. Missing values remain missing. Estimated AA index scores and deprecated AA entries are excluded. No model outputs, benchmark scores, weights or model-setting details are invented.

## Rebuild

Install/use Python 3 with `matplotlib` and `numpy`, then from the repository root run:

```sh
python library/reproducibility/benchmarks-2026-10-13/generate_charts.py
```

The generator reads the factual datasets in `data/` and writes a standalone `charts/` subdirectory and `manifest.json` next to the script, plus leader summaries and verification counts. The committed charts live in `library/graphics/benchmarks/`, indexed by `library/asset-index.json` (filter `collection: verified-benchmarks`). Regeneration does not automatically update those assembled files or their catalog hashes. Import deliberately reviewed changes and refresh the catalog before episode use. It does not refetch mutable webpages. The initial parser is kept as `extract_primary_data.py` for future captures; it expects raw captures in the parent directory and should be run deliberately when updating evidence.

The canonical asset index identifies the 52 committed chart assets; the original standalone `manifest.json` was not copied. A new `manifest.json` is produced by the rebuild command. Metadata files, scripts, numerical datasets and preview renders are not counted as media assets. Numeric rounding in visible labels does not alter the raw saved values. Full-provider poster records include exact displayed cohort counts.

## Rights and attribution

The chart compositions and generator are original work for AI Update Sources. Numerical benchmark facts are attributed to their publishers using visible source URLs and dates. This collection does not grant rights to third-party logos, benchmark questions, source website design or unrelated copyrighted material. No full publisher webpages or benchmark questions are distributed here. Keep source attribution and caveats with reused or cropped graphics.
