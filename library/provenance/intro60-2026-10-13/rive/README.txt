AI UPDATE — ORIGINAL RIVE GRAPHICS
Created October 13, 2026 for the authorized AI UPDATE opening.

These illustrations are original commissioned artwork authored in Rive Markup
Language and compiled/rendered by the official Rive CLI 1.5.1. They are actual
Rive-produced assets. No third-party marketplace/community artwork, company
logos, stock imagery, fonts, templates, or paid assets were reused in them.
The user may reuse and modify this original artwork for AI UPDATE, including
commercial episodes. Rive software itself remains subject to Rive's terms.

ASSETS
neural_core.png: original network globe with central processor, cyan/gold palette.
evaluation_lens.png: original evaluation instrument with code and verification motif.
value_balance.png: original quality/cost balance; no factual scores or prices.
neural_core_3s.png: later render of the Neural Core artboard for motion verification.
neural_core_6s.gif: actual animated image encoded from 120 Rive-rendered frames,
sampled at 20 fps. A seamless six-second orbit, 720 x 720, infinite loop.

Each PNG is 1200 x 1200, rendered directly by Rive. Background: #07111C.
The PNGs are opaque. They are frame captures, not video and not an animation file.
PowerPoint animation of these frames is separate from native Rive animation.
The GIF preserves actual Rive motion as an animated image supported by PowerPoint.
It was encoded directly from PNG captures using ffmpeg; there is no video intermediate.

EDITABLE SOURCE
neural_core/scene.rml: full editable scene source with three artboards, vector
primitives, original geometry, timeline keyframes and default state machines.
neural_core/rive.yaml: project configuration.
generate_rml.py: deterministic source generator; uses only Python standard library.
neural_core/build/neural_core.riv: actual compiled Rive runtime artifact.
gif_scene/scene.rml: editable source for the six-second loop variant.
gif_scene/build/ai_update_neural_loop.riv: actual compiled loop-variant runtime file.
capture_gif.py: traceable Rive headless capture and ffmpeg image encoding workflow.

MOTION
Neural Core: orbit carrier rotates through 0.72 radians every 10 seconds.
Evaluation Lens: scanning arc completes one revolution every 10 seconds.
Value Balance: value beam tilts gently in a repeating 10-second cycle.
These are conceptual illustrations and do not establish measured AI performance.

VERIFICATION
Official CLI installed from https://releases.rive.app/cli/install.sh.
Linux binary version 1.5.1, verified against official SHA-256 manifest.
Local build succeeded. Final CLI verify: 0 errors, 0 warnings.
CLI inspect: problems array empty; three correctly named artboards present.
All three PNG captures viewed at native dimensions.
1-second and 3-second Neural Core frames differ, establishing live timeline motion.
See provenance.json and inspect-summary.json for exact evidence.
See gif_capture_evidence.json for every GIF source capture command and frame hash.
See gif_validation.json for encoded duration, frame count, distinct frames and loop.

REBUILD
Install the official Rive CLI. Then from the asset folder:
  python3 generate_rml.py
  rive neural_core --verify
  rive inspect neural_core --summary
  rive neural_core --screenshot=neural_core.png --artboard="Neural Core" --advance=1s
  rive neural_core --screenshot=evaluation_lens.png --artboard="Evaluation Lens" --advance=1s
  rive neural_core --screenshot=value_balance.png --artboard="Value Balance" --advance=1s

LIMITS
No sign-in or purchase was used. Native .rev export requires Rive sign-in under
current CLI documentation; therefore .rev was not generated. The editable source
is RML. The .riv contains no scripts and works locally without publishing.
The official CLI installation needed an extracted Ubuntu libGLES2 runtime library
in this container. Those software binaries are excluded from the artwork bundle.

OFFICIAL DOCUMENTATION
https://rive.app/docs/cli/overview
https://rive.app/docs/cli/getting-started
https://rive.app/docs/cli/examples
https://rive.app/docs/cli/reference/commands
