# Original backgrounds and motion overlays

200 original assets: 100 static SVG backgrounds and 100 SVG SMIL motion overlays, all 1920 × 1080. Their committed locations are `library/images/backgrounds/` and `library/motion/overlays/`. Filter `library/asset-index.json` for `collection: background-motion` to find exact IDs, paths, hashes, durations and use guidance. Catalog paths are relative to the repository root. The original standalone `manifest.json` and contact-sheet derivatives are not committed.

Use these illustrative assets behind or around genuine source content. They do not encode measured results. Keep motion away from evidence while it is being read. CC BY 4.0; retain attribution **AI Update Sources**.

Motion SVGs play through browser SMIL. Native PowerPoint animated-SVG playback is not asserted. Render actual timed browser frames to video, or recreate the motion natively. Preserve alpha through a compatible format, or composite onto the scene before H.264 export. A static thumbnail does not verify animation.

From the repository root, render committed assets using:

```sh
node library/provenance/background-motion/verify_render.mjs --output-dir /tmp/ai-update-background-qa
```

This checks hashes, static rasterization and all 40 family samples. Its report explicitly excludes animation/audio/PowerPoint playback. It reads the assembled catalog and writes QA derivatives only to the selected output directory. `generate_assets.py` is the preserved standalone generator; it produces a local source bundle, not an automatic update to the assembled collection.
