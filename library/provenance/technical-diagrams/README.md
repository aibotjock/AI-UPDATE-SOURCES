# Original cloud-AI technical diagrams

180 original 1920 × 1080 SVG schematics for recurring AI episodes.

These assets explain stable concepts: cloud inference, prompting, context,
tools, search, files, multimodal tasks, platform features, costs, latency,
evaluation, uncertainty, benchmarks, comparisons, provenance, and reliability.
They contain no invented benchmark results, empirical price data, company
logos, or local hosting advice. Each concept is individually labeled and
cataloged in `library/asset-index.json` (filter `collection: technical-diagrams`) and this directory's `topics.md`. Committed SVGs are in `library/graphics/diagrams/`; the original standalone manifest and QA derivatives were not copied.

## Use

SVGs have no external dependencies or embedded scripts. They use editable
vector shapes and text with common fonts. Prefer importing into a presentation
as SVG; verify font substitution in the target application. A conceptual
schematic should be labeled as an illustration, not used as score evidence.

## Rebuild

The preserved standalone generator `python generate_diagrams.py` creates a separate local `assets/` bundle and its manifest. It does not automatically update the committed SVG locations or canonical catalog.
Run `python generate_diagrams.py --qa` with Pillow and Inkscape available to
render every asset and produce nine contact sheets. `qa/validation.json`
records programmatic checks. The thumbnail renders are QA derivatives of
these 180 assets, not additional unique assets.

## Interpretation

Diagrams simplify real implementations. Verify technical claims and the
current behavior of the exact cloud service before episode use. Node order
does not imply a vendor's documented architecture. No asset asserts a live
model score, current price, current availability, or guaranteed behavior.

## License

Original graphics and generator: CC BY 4.0.
Attribution: **AI Update Sources**.
License: https://creativecommons.org/licenses/by/4.0/
