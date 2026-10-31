# AI UPDATE — Motion Graphics Resources (Ranked, Cited)

*Research & planning document only — no code. Compiled 2026-10-31.*

## Bottom line

For AI UPDATE, which needs repeatable benchmark scoreboards, narration-synced explainers, consistent branding (charcoal, electric blue and gold), and transparent overlays that keep clear of the floating webcam bubble, the top resource is **Remotion** for data-driven templates. Second are **gsap-video-export / svg-to-video**, which can turn the existing library of 100 animated SVG overlays and 992 SVGs into video clips without new art. Third is **Revideo**, an MIT-licensed tool for narration-synced explainers. Free stock and template libraries (Mixkit, LottieFiles, Pexels/Pixabay) fill gaps in intros, lower thirds and B-roll. AI video generators are useful only for stylized B-roll, never for exact numbers or text.

## Methodology & honesty note

- **The webcrawl tool (aibotjock/webcrawl)** was read and assessed. It is a public, MIT-licensed, self-hosted Firecrawl alternative with five tools: `search` (keyless web search), `scrape` (URL → Markdown/HTML/links/screenshot via headless Chromium), `crawl` (same-origin recursive), `map` (all URLs on a domain) and `extract` (page → typed JSON via LLM, with heuristic fallback). It exposes an HTTP API on port 8787, a stdio MCP server and a WebUI.
- **Important:** webcrawl runs locally on your Linux machine. I could read its code on GitHub but **could not execute it**, because my environment has no network path to your local server. Instead, I applied the same search → scrape → extract methodology with my own web search and scraping tools. **The results below did not come from running webcrawl itself.**
- Most facts come from search-result summaries and vendor or project pages. Star counts, exact license texts and asset counts were **not** independently opened for every item; anything marked **(verify)** needs checking before use. Some sources are vendor blogs and may be biased; these are flagged.

### Suggested webcrawl workflow to re-verify or extend this list (run on your machine)
1. **search**: queries such as "Remotion license", "gsap-video-export", "free lower thirds commercial license", "transparent WebM motion graphics".
2. **map**: map each vendor or project docs domain (e.g. remotion.dev, mixkit.co, lottiefiles.com, svgator.com) to find license, pricing and export pages.
3. **scrape**: scrape those license, pricing and export pages to Markdown and keep them in the repo as evidence snapshots.
4. **extract**: run a schema over each page to build a comparable table. Suggested fields: name, license, cost, export formats, alpha/transparency support, last updated, maintenance status.

## Ranked summary

| Rank | Resource | Type | Cost / License | Best use in AI UPDATE |
|---:|---|---|---|---|
| 1 | Remotion | Code framework (React) | Free for individuals and companies of ≤3 people; paid above that | Data-driven benchmark scoreboard templates |
| 2 | gsap-video-export / svg-to-video | SVG → video converters | Open source (verify licenses) | Turn existing 100 animated SVGs into clips |
| 3 | Revideo (+ Motion Canvas lineage) | Code framework (TS) | MIT | Narration-synced explainers |
| 4 | YouTube-AI-Motion-Graphics + Futurepedia Style Atlas | HTML/GSAP explainer packs | Verify | Ready-made explainer boards |
| 5 | LottieFiles | Animation library + tools | Free + premium; per-asset licenses | Icons, loaders, AI-themed animations |
| 6 | Mixkit | Free templates & stock | Mixkit License (commercial, no attribution) | Lower thirds, openers, transitions |
| 7 | SVGator | No-code SVG animator | Animated export requires paid plan | Transparent brand stings (WebM/MOV) |
| 8 | Vizzu / D3.js / Anime.js | Chart & animation libraries | Apache-2.0 / open source | Animated chart morphs (needs capture) |
| 9 | AECharts / Alien Art / AnimCharts | No-code animated charts | Free tier to paid | Quick animated charts from CSV |
| 10 | Pexels / Pixabay | Free stock video | Own free licenses | Tech backgrounds, B-roll |
| 11 | Runway / Kling / Veo / Pika | AI video generators | Paid / credits | Stylized B-roll only |
| 12 | Motion Array / Envato Elements | Paid template subscriptions | ~$16–25/mo | Broad template catalog |
| 13 | Rive | Interactive animation | Free + paid | Poor fit for linear video |
| 14 | Emerging packs (motion-skills, video-shotcraft, CodeCinematic, HTML-Video, Celesta, Friction) | Agent skills / niche tools | Varies — verify | Experimentation only |

---

## 1. Remotion
**What it is:** A React framework for making videos in code.
**How it works:** Each frame is rendered as a function of time (`useCurrentFrame`). Videos can be rendered headlessly from a CLI or in the cloud (Lambda / Cloud Run). Data such as JSON props can be passed in, so one template can produce many videos.
**Fit for AI UPDATE:** This is the strongest match for the "Benchmark scoreboard" segment: one branded scoreboard template, fed new benchmark numbers each episode. Community templates exist (reactvideoeditor/remotion-templates).
**Caveats:** Source-available, not open source. It is free for individuals and companies of up to 3 people; larger companies need a paid license, so confirm your status.
**Sources:** github.com/remotion-dev/remotion; remotion.dev; pkgpulse.com/guides/remotion-vs-motion-canvas-vs-revideo-programmatic-video-2026; rendercomp.com/blog/remotion-vs-motion-canvas-comparison/; ai-solutions.wiki/tools/remotion/; github.com/reactvideoeditor/remotion-templates

## 2. gsap-video-export and svg-to-video
**What they are:** Tools that capture browser-based SVG/GSAP animations and turn them into video files.
**How they work:**
- **gsap-video-export** is an npm CLI. It uses Puppeteer (headless Chrome) to step through a GSAP or SVG animation frame by frame, then encodes the frames with FFmpeg. Options include an SVG selector (`-S`), a scale factor (`-z`), "Timeweb" frame advancement for non-GSAP animations, and page/frame preparation hooks.
- **svg-to-video** (GehDoc) is a browser "Web Studio" that uses WebCodecs for frame-accurate rendering and includes an MCP server. **svg2vid** is a similar browser tool.

**Fit:** Your library already has 100 animated SVG overlays and 992 SVGs in total, but no video clips, and the current renderer only does stills and fades. These tools fill that gap directly without creating new art.
**Caveats:** Licenses and maintenance status are not individually verified **(verify)**. Transparent-video output support should be tested.
**Sources:** github.com/workeffortwaste/gsap-video-export; npmjs.com/package/gsap-video-export; github.com/GehDoc/svg-to-video; gehdoc.github.io/svg-to-video/; lowweilin.github.io/svg2vid/; background reading: umesh-malik.com/blog/svg-to-mp4-in-the-browser; captio.work/blog/client-side-video-rendering-2026

## 3. Revideo (and the Motion Canvas lineage)
**What it is:** An MIT-licensed TypeScript framework for programmatic video, forked from Motion Canvas.
**How it works:** Scenes are written as generator functions. It supports headless and CLI rendering, cloud rendering (Cloud Run / Lambda), a React player, and audio/video sync. v0.11.0 was released on 2026-07-10, and the fork is maintained at midrender/revideo.
**Motion Canvas** (MIT) has an editor with an audio waveform for syncing to voiceover. Its core is described as effectively dormant as of Oct 2026. **Canvas Commons** is an active community fork.
**Fit:** Well suited to explainers timed to narration, such as the "What changed" segment.
**Caveats:** Upstream Revideo development has reportedly slowed as the team focuses on its commercial editor (Midrender).
**Sources:** github.com/midrender/revideo; midrender.com/revideo/docs; genmotion.dev/blog/hyperframes-alternatives; metavert.io/motion-canvas

## 4. YouTube-AI-Motion-Graphics and Futurepedia AI Style Atlas
**YouTube-AI-Motion-Graphics (sirioberati):** Described as 74 pre-built HTML/GSAP "explainer boards", plus skills for syncing them to audio using Whisper transcripts, aimed at technical YouTube channels. **(verify — known only from a search summary; repo not opened.)**
**Futurepedia AI Style Atlas:** Assessed earlier in this project. It offers 86 styles, with prompts that produce 1280×720 HTML animations rendered to MP4, plus a storyboard mode, voiceover timing and sound kits. *(The page URL was not recorded in my notes — verify.)*
**Fit:** Both follow the HTML → video pipeline and match the explainer format.
**Source:** github.com/sirioberati/YouTube-AI-Motion-Graphics

## 5. LottieFiles
**What it is:** A library and toolset for Lottie (JSON) and dotLottie animations, with 800,000+ free and premium animations.
**How it works:** It provides an AI Motion Copilot, plugins for After Effects, Figma and Canva, and the ThorVG runtime. Its marketplace has an "AI / machine learning" category.
**Fit:** Animated icons and AI-themed accents. These need conversion to video or an overlay workflow.
**Caveats:** Licenses vary by asset, so check each one (this is my recommendation, not a statement from the source).
**Sources:** lottiefiles.com; lottiefiles.com/ai; lottiefiles.com/marketplace/ai-machine-learning

## 6. Mixkit
**What it is:** Free video templates for After Effects, Premiere, Final Cut Pro and DaVinci Resolve, including lower thirds, news lower thirds, openers and transitions, plus free tech motion-graphics stock.
**License:** The Mixkit License allows commercial use with no attribution and no signup.
**Fit:** Lower thirds, segment transitions and openers. This fills the "no intro/outro stings" gap.
**Similar sources:** Videezy and Uppbeat both have free tiers **(verify licenses)**.
**Sources:** mixkit.co/free-after-effects-templates/lower-thirds/; mixkit.co/free-video-templates/; mixkit.co/free-stock-video/motion-graphics/; videezy.com/free-video/lower-thirds; uppbeat.io/motion-graphics/category/lower-thirds

## 7. SVGator
**What it is:** A browser-based, no-code SVG animator.
**How it works:** It exports SVG, Lottie, MP4, MOV and WebM. MOV and WebM support transparency, and cloud rendering goes up to 4K60.
**Fit:** Animate your existing logo SVGs into transparent brand stings that can sit around the webcam bubble.
**Caveats:** The free plan only exports static files; animated exports need a paid plan.
**Sources:** svgator.com; svgator.com/svg-to-video

## 8. Vizzu, D3.js and Anime.js
- **Vizzu** (Apache-2.0) animates morphs between chart types, rendered on Canvas with a C++ → WASM engine. It has no built-in video export.
- **D3.js** handles transitions, timers and interpolation. It has no native video export; use headless-browser capture plus FFmpeg.
- **Anime.js v4.5.0** offers SVG `morphTo`, motion paths and line-drawing effects. It needs headless capture to produce video.

**Fit:** Animated benchmark charts, used together with the capture approach in #2.
**Sources:** github.com/vizzuhq/vizzu-lib; d3js.org; animejs.com; animejs.com/documentation/svg; github.com/juliangarnier/anime

## 9. No-code animated chart tools
- **AECharts:** MP4 and transparent WebM export, with a brand kit.
- **Alien Art Charts:** CSV → MP4, up to 4K60 on paid plans.
- **AnimCharts:** free 1080p MP4/GIF.
- **Flourish:** video export is Enterprise-only (about $5k+/yr).
- **Datawrapper and RAWGraphs:** no video export.

**Caveat:** The Alien Art and AECharts comparisons are vendor blogs and may be biased.
**Sources:** alienart.io/blog/best-animated-chart-video-software; aecharts.com/best-animated-chart-tools/; animcharts.com

## 10. Pexels and Pixabay
- **Pexels:** 60k+ motion-graphics clips under the Pexels License (free, no attribution required).
- **Pixabay:** 12k+ motion graphics and 18k+ tech backgrounds.

**Fit:** Background plates and B-roll.
**Sources:** pexels.com/search/videos/motion%20graphics/; pixabay.com/videos/search/motion%20backgrounds%20tech/

## 11. AI video generators (Runway, Kling, Veo, Pika)
These include Runway Gen-4/4.5 (Motion Brush and camera controls; you already use Runway for narration), Kling 3.0, Google Veo 3.1 and Pika 2.x (stylized effects). Sora was reportedly shut down as a consumer app in early 2026.
**Fit:** Stylized B-roll only. These models are known to be unreliable at rendering exact numbers or text, so they are unsuitable for scoreboards.
**Sources:** lovart.ai/blog/video-generators-review; explainx.ai guide (2026-10-09)

## 12. Motion Array and Envato Elements
- **Motion Array:** $15.99/mo for templates or $24.99/mo for everything. The license is tied to the subscription, with a $9.99 Continuity plan, and there is no indemnification.
- **Envato Elements:** from $16.50/mo for 29M+ assets, with indemnification.

**Sources:** photutorial.com/envato-vs-motion-array/; elements.envato.com/learn/envato-vs-motion-array-comparison (Envato's own page, so a vendor source)

## 13. Rive
Rive builds interactive, state-machine-driven animations (.riv files). The editor can export MP4, GIF, WebM or PNG sequences, but exported video loses the interactivity.
**Fit:** Weak for a linear YouTube video.
**Sources:** rive.app/docs/editor/exporting/exporting-for-video-and-static-design; hedrick.io/post/rive-animation-guide-2026

## 14. Emerging / niche (all **verify**)
- **iart-ai/motion-skills:** 56 agent skills covering kinetic typography, data viz and 3D WebGL.
- **video-shotcraft:** 100+ shot recipe cards, aimed at product promos.
- **CodeCinematic:** built on Remotion; HUD and IDE simulations.
- **nexu-io HTML-Video:** HTML/CSS → MP4.
- **Celesta:** Rust, code-first video.
- **Friction Graphics:** C++/Skia.

**Sources:** github.com/iart-ai/motion-skills; github.com/topics/motion-graphics; github.com/Mihuil121/CodeCinematic; github.com/topics/programmatic-video

---

## Appendix — Floating webcam bubble on Linux (production setup, not ranked)
- In OBS, use an **Image Mask/Blend** filter with a PNG mask (white circle on black) to crop the webcam to a circle. Layer animated transparent WebM rings above it.
- On Linux, v4l2loopback provides a virtual camera, and Wayland setups use PipeWire. Cubix Capture offers automated bubble masking.
- **Implication for motion assets:** prefer formats with transparency (WebM, MOV) and keep a consistent clear zone where the bubble sits.

**Sources:** neonstreamlab.com/blog/how-to-add-webcam-overlay-obs; cubix.design/resources/how-to-add-webcam-overlay-obs; fosslinux.com/46258/webcam-software-ubuntu-linux.htm

## Gaps / not verified
- webcrawl was not executed; see the methodology note.
- Licenses for gsap-video-export, svg-to-video, sirioberati's pack and the emerging tools were not opened.
- The Futurepedia Style Atlas URL was not recorded.
- Asset counts and prices are as stated by the sources at the time of search and may change.
- Remotion licensing depends on your company size.

## How this maps to known library gaps
| Gap in AI-UPDATE-SOURCES | Resources that address it |
|---|---|
| Motion is SVG loops only, no video clips | #2, #8 |
| No brand intro/outro stings | #6, #7, #5 |
| Renderer does stills and fades only | #1, #3 |
| presentation-components folder empty | #1 (templates), #4, #6 |
