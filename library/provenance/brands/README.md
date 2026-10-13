# Cloud AI brand marks

40 distinct company/product identifiers for model comparisons, cloud platform walkthroughs, and announcements. One mark per identity; previews and the contact sheet are derivatives, not extra counted assets.

## Provenance and use

These are community-maintained LobeHub `lobe-icons` assets, **not official brand-kit downloads**. The exact, byte-preserved SVGs are pinned to commit `bcdb7c82792a854c2967f7328e11a30205ea584d`. The manifest records the raw source URL, source path, hash, attribution, and an official brand/service reference for later review. Those reference links are not assertions of official permission or independent review.

The upstream repository is MIT licensed. Its actual full license, including `Copyright (c) 2023 LobeHub`, is retained in `licenses/lobehub-MIT.txt`, together with the upstream README. Retain the notice when redistributing the assets.

**MIT licensing does not grant trademark rights or independently clear the companies' brand-use conditions.** Each manifest record is marked `trademark-editorial-use-review` and `not-independently-brand-cleared`. Use marks for accurate editorial identification, review the owner's current rules before publication, avoid endorsement implications, and preserve the brand artwork. No broad commercial brand authorization is claimed.

## Files

- `assets/`: 40 original SVGs, unchanged from the pinned upstream source.
- `previews/`: one 600-pixel-wide PNG preview per identity, rendered on white for legibility.
- `manifest.json`: the 40 counted asset records.
- `contact-sheet.jpg`: all 40 identities in one visual index.
- `build_brands.py`: pinned collection and rendering script.

OpenAI's mark also identifies ChatGPT context here. Z.ai's mark also identifies the GLM product-family context; this does not fabricate separate ChatGPT or GLM marks. Company marks such as Meta, Baidu, and Tencent are for company-level context, not a claim that all of their products use that logo.

## Render verification

All 40 SVGs parsed successfully; no embedded scripts, `foreignObject` content, or external image references were found. All 40 source SHA-256 values differ. Each preview was checked for nonblank pixels, and the entire contact sheet was visually inspected. Kimi uses the upstream monochrome mark for legibility rather than its white-on-dark version.

Some upstream SVGs use CSS `1em` viewport dimensions and `currentColor`. When rendering for a presentation, the script temporarily supplies numeric viewport dimensions and black current color without changing any paths or source SVG. This fixes an Inkscape compatibility issue. Preview images are derivatives of the source artwork and are not additional original assets. For a different background, render from the SVG while preserving its aspect ratio and approved artwork colors.
