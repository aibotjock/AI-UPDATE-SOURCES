# Mandatory episode resource workflow

1. Read the source registry, asset index, benchmark chart source/date records, evergreen reference notes, prior reproduction records, and correction log.
2. Complete research and verification for the episode cutoff before writing the spoken script. Use the checked evidence packet to write the episode's narration and current storyline. Reuse accurate narration and visual portions when relevant, preserving original measurement dates and labeling unchanged evidence. Complete the required genuine comparison before narrating its results. Search metadata first, then load only the assets needed for the episode. Preserve asset IDs and provenance in the episode manifest.
3. Check dated evidence and current cloud availability against original sources before using a chart to recommend a model. Do not use a template as a measured result or a historical snapshot as a current ranking.
4. Use logos, images, graphics, icons, motion, SFX, and presentation components where they improve the explanation. All resource categories participate in the workflow; an episode need not display every asset or every category.
5. Give slides distinct compositions within the deck. Logos may repeat; preserve necessary visual continuity.
6. Use raw benchmark data and scripts for refreshed cross-company, category, and within-platform comparisons. Preserve exact model settings, intervals and coverage; do not fabricate universal rankings.
7. Save new reusable assets and metadata to the media-library branch. Record episode use and any limitations. Store prompts, outputs, settings, billed usage and calculations under reproducibility.
8. Add claim-level corrections and flag affected charts/recommendations. Update the dated comparison index and preserve historical evidence.

Generate or obtain authorized narration before finalizing scene timing. Align animation, effects, cuts and captions to its actual durations. Initial timing is provisional. A complete narrated export and full watch-and-listen review are required before an episode is complete.

## Runway narration retrieval recovery

For a multi-cue stock-voice job, persist the returned task ID for each cue immediately. Generation and retrieval are separate operations; never submit a new generation merely because an asset download fails. After tasks succeed, retrieve each result URL, download to a deterministic cue filename, and verify every asset with `ffprobe` plus a checksum. A batch transfer may partly complete and then hit a transient network-policy or transport error. Count the existing verified files, identify only missing cue IDs, and retry those individually with bounded backoff and a timeout. Refresh the task URL with `get_task` if its signed URL expired. Keep signed URLs and workspace identifiers out of the public manifest and repository. Measure decoded PCM sample counts after retrieval; those actual durations govern captions, slide timing, and the video. Preserve the cue-to-task IDs and file hashes for future recovery without incurring generation charges. This procedure recovered seven missing cues from an interrupted 134-cue Episode 01 download on 2026-10-13.

Current reusable tools and their limits: [episode-production](../tools/episode-production/README.md).

