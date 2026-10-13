# Original backgrounds and motion overlays

200 original assets for the cloud-model AI update show: **100 static SVG backgrounds** and **100 SVG SMIL motion overlays**. All use a 1920 × 1080 viewBox. Backgrounds have quiet central space; overlays have transparent canvases. Each family has five distinct geometric compositions rather than simple color replacements.

## Reuse

- Static backgrounds can sit below benchmark charts, screenshots, model outputs, and narration cards.
- Overlays can emphasize, introduce or transition genuine source content. Keep motion away from text while it is being read.
- Artwork is illustrative only. Pulse/waveform/landscape graphics do not encode measurements. The completion animation does not establish that an evaluation passed.
- No logo, benchmark result, model output, or screenshot in this collection purports to come from a provider.
- Licensing: CC BY 4.0, attribution **AI Update Sources**. License link: https://creativecommons.org/licenses/by/4.0/

## Formats and animation

`backgrounds/*.svg`: static editable vectors. `motion-overlays/*.svg`: self-contained browser-playable SVG SMIL animations. Exact loop durations and purposes appear in `manifest.json` and each SVG description. The motion examples are intentionally cyclic and can be trimmed to a single loop; transitions should be used once, not continuously.

PowerPoint importing an SVG may show only a static frame: **native PowerPoint animation is not claimed**. Import the static graphic and apply PowerPoint-native motion, or render browser animation to a video clip. For faithful export, play the SVG at 1920 × 1080 in a compatible browser and record/capture frames at a fixed rate (e.g. 30 fps); encode the intended loop with FFmpeg. Use WebM with alpha or ProRes 4444 for transparency, or composite onto the actual slide before creating an H.264 MP4. A screen recorder may flatten alpha. Browser automation and recording tools may be unavailable in a restricted environment.

## Manifest

`manifest.json` contains IDs, titles, relative paths, dimensions, duration, category, origin, license, intended uses, reuse limits, byte sizes, and SHA-256 hashes. It is the machine-readable catalog. `generate_assets.py` reproduces all 200 SVGs deterministically. The generator and QA contact sheet are supporting files, not counted as assets.

## Verification

The collection is checked for valid XML, 200 unique file hashes, 1920 × 1080 dimensions, and animation presence in all 100 motion files. The contact sheet samples every static family and every motion family at its initial SVG frame. Initial-frame raster verification does not verify browser animation or PowerPoint export playback.
