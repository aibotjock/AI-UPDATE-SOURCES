# Visual and semantic QA

- Exactly 180 original SVG files; 180 unique titles and 180 unique file hashes.
- 18 substantive categories, 10 separately authored concepts per category.
- 14 diagram compositions: flow, split, merge, three-input merge, comparison,
  stack, cycle, hub, matrix, gate, triangle, tree, funnel, and ladder.
- Every SVG parsed successfully and rendered at 480 × 270 for QA using
  Inkscape. The original editable graphics remain 1920 × 1080.
- All nine contact sheets were visually inspected. Labels, title hierarchy,
  contrast, arrow routing, and footer placement were reviewed.
- Decision labels and branch semantics were reviewed; validation diagrams
  preserve rejection outcomes rather than implying invalid output is accepted.
- Three-input aggregation graphics were revised so reference excerpts and
  additional charges appear as contributing inputs rather than produced stages.
- Revised context aggregation and ranking-uncertainty samples were inspected
  individually after regeneration.
- No live prices, model rankings, benchmark scores, company logos, factual
  screenshots, or other empirical results are represented.
- These are original schematic explanations. Current platform behavior and
  episode-specific factual claims still require verification from authoritative
  evidence; that limitation is included in each metadata record.

## Renderer

CairoSVG was unavailable in the execution environment. Inkscape rendered all
180 SVGs, and Pillow produced the contact sheets. All source graphics have
editable SVG text/shapes and no external resources, scripts, or raster content.

The 180 QA PNGs and nine contact sheets are derivatives, not extra unique
assets for the requested library count. Import only `assets/*.svg` when counting
this category toward the media library.
