# AI UPDATE channel continuity and episode generation

This branch is the project's versioned reference and episode-generation base. It retains the repository's populated media collection and reviewed resource repairs and adds the approved channel decisions from this thread.

## Start here

Read these canonical references before generating any episode:

| File | Purpose |
| --- | --- |
| continuity.json | Current approved machine-readable decisions and series version |
| series-master-prompt.txt | Production, evidence, narration and completion rules |
| episode-formula.txt | Five regular segments and flexible timing |
| channel-description.txt | Exact approved channel description |
| source-review-policy.md | Reputable sources, claim verification and source changes |
| history/CHANGELOG.md | Changes and retained previous versions |

The standard 12-minute formula is: main takeaway 0:30, what changed 2:45, benchmark scoreboard 2:30, same-prompt comparison 4:00, and your choice/what is next 2:15. Keep these roles recognizable and move minutes according to meaningful verified changes. A practical lesson is optional for special occasions featuring best and/or new items. Episode 01 may allocate more time to its benchmark primer and 35–45-second introduction.

## Mandatory repository use

Read references/source-registry.json, library/asset-index.json and library/INDEX.md first. Then select relevant benchmark data, media, source/provenance records, evergreen definitions, prior outputs/costs and corrections. Do not rebuild the collection or assume a listed source or saved chart is current. Record selected source IDs, asset IDs, versions, dates, attribution and conditions in the episode records. Use only suitable permitted assets.

The source registry is adaptable rather than a permanently trusted list. Only reputable, reliable and regularly updated sources qualify. Access-checked candidates require verified maintenance history and claim-level content verification before their facts enter narration. See source-review-policy.md for additions, replacements, disputes and retirement. Capture original evidence where permitted, keep numeric data, and preserve history.

## Generate today's production prompt

From the repository root, run:

```bash
python3 channel/generate_episode.py generate --episode 01
```

The generator resolves the actual America/New_York date. It writes a dated prompt and pending evidence/comparison/status records, snapshots the canonical references, source/evolution policies and source/media indexes, and retains their hashes. The prompt references the large indexes instead of embedding their entire content. It never claims to have researched, tested models, written a finished script, generated narration or rendered video. A completed or already generated episode folder is not silently overwritten. Use the next appropriate episode ID; keep old episodes. To request an exceptional best/new-item lesson, add --include-practical-lesson; that selects an optional plan and does not verify its evidence.

Read the generated prompt and perform its evidence-first production steps through authorized tools. Complete same-day verification before script creation. If production moves to a new local calendar day, update the date and reverify material changeable claims rather than backdating. Keep original benchmark measurement/publication dates separate from fresh retrieval/verification. The comparison records separate today's review from each original run date. Reused results need retained evidence references and a review of whether the model, settings and task still support their use; do not relabel an old test as a new run.

```bash
python3 channel/generate_episode.py validate episodes/ACTUAL-DATE/EPISODE-ID
```

Use the actual path printed by the generator. Validation checks date/stage records, source-maintenance fields, matching reference/script/video hashes and required files; it cannot independently establish truthful claims or actual media playback. Do not mark gates completed without doing and documenting the work.

## Evolve without losing continuity

After each episode, record changed/unchanged/superseded findings, corrections, useful new assets and production issues in its dated records. Use evolution-policy.md to assess new models, benchmarks, technology and source quality. Update mutable evidence with dates and provenance while preserving the approved series roles. Preserve approved prior templates under history when the series specification changes.

There is no scheduled research, paid API integration, narration service, video assembly engine, YouTube publishing or analytics connection created by this branch. Those capabilities must be supplied and verified during production. The branch supports honest prompt generation and reproducible continuity; it does not represent a finished episode.
