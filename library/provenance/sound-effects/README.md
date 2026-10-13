# Original sound effects for AI UPDATE

60 original, procedural sound effects for cloud AI news, evidence screenshots,
side-by-side prompt/output comparisons, platform feature demonstrations, and
benchmark/cost animations. No speech, music, third-party samples, or downloaded
recordings are included. The audio and generator are released under CC0-1.0.

## Audio format

- Uncompressed PCM WAV, mono, 48 kHz, 16 bit.
- 48 cues are 0.5 seconds or less; all 60 are under one second.
- Peaks are at most -12 dBFS; compact UI cues target -15 dBFS.
- Every event has a short fade; every complete file has a 10 ms fade-in and a
  22 ms fade-out, with exact zero samples at both boundaries.
- Total audio is 29.37 seconds, approximately 2.82 MB for all WAV files.

## Families

| Folder | Count | Examples |
| --- | ---: | --- |
| `transitions/` | 10 | Source zoom, comparison flip, cloud handoff, timeline movement |
| `reveals/` | 10 | Headline, model name, price tag, prompt/output panel |
| `interface/` | 10 | Click, toggle, tab change, copy, filter, expand/collapse |
| `confirmations/` | 10 | Source checked, test completed, criterion met, artifact saved |
| `attention/` | 10 | Methodology, uncertainty, access limit, date, correction |
| `data-motion/` | 10 | Bar growth, line trace, scatter point, interval, cost stack |

These are 60 hand-authored cue profiles, with differing layer arrangements,
rhythms, envelopes, noise/tone combinations, and synthesis parameters. They are
not duplicates made by changing only pitch, file name, silence, or encoding.

## Recommended starting mix with narration included in production

1. Start the SFX track at -6 dB gain relative to the supplied files. Use -10 dB
   for qualification/attention notes if they overlap detailed narration.
2. Duck effects a further 4-8 dB when speech overlaps. Let the brief effect
   remain strongest during a pause or just before the spoken explanation.
3. Align the cue's attack to the actual visual event: slide transition,
   highlight, chart reveal, or click. Do not add a sound for every animation.
4. Use neutral benchmark/cost cues. Reserve confirmation cues for actual
   verified actions or criteria; avoid suggesting an unsupported model winner.
5. Listen to the final mix on headphones and phone speakers. Adjust individual
   cues rather than normalizing every short file to the same integrated LUFS.
   Metadata includes RMS dBFS, which is not a standardized LUFS measurement.
6. Check the completed video for intelligible speech and output clipping.
   The final narration mix and PowerPoint playback have not been tested here.

## Good first auditions

- `transitions/evidence-zoom-in.wav`
- `reveals/price-tag-reveal.wav`
- `interface/copy-prompt.wav`
- `attention/comparability-caveat.wav`
- `data-motion/cost-stack-build.wav`

## Metadata, validation, and reproducibility

`library/asset-index.json`, filtered by `collection: sound-effects`, is the committed catalog with one record per WAV. The original standalone `metadata.json` was not copied. It includes identity, intended
use, tags, relative path, license, exact bytes, SHA-256, duration, format, peak,
RMS, and mix guidance. Canonical catalog paths are relative to the repository root. Committed WAVs are in `library/sound-effects/`.

`qa-report.json` records the actual decoded PCM checks for all 60 files. Those
checks verify readable PCM, expected frame counts, correct sample rate/bit
depth/channels, non-silence, unique hashes, headroom, and zero boundaries. They
do not certify subjective quality or similarity, or a finished narration mix.

Rebuild with Python 3 and NumPy:

```bash
python generate_sound_effects.py
```

Generation uses a deterministic per-cue seed and no network or paid service.
This preserved standalone generator writes a separate local WAV bundle and reports under this provenance directory. It does not update `library/sound-effects/` or the assembled catalog automatically. Deliberately import reviewed changes and update hashes before reuse.

CC0 dedication: <https://creativecommons.org/publicdomain/zero/1.0/>
