#!/usr/bin/env python3
"""Generate 60 original AI-update animation cues; no samples or model services.

Audio: mono, 48 kHz, signed 16-bit PCM. NumPy is the only non-stdlib dependency.
The sound designs and generated WAV files are released under CC0-1.0.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import wave

import numpy as np

ROOT = Path(__file__).resolve().parent
SR = 48000
VERSION = "1.0.0"


def L(kind, start, duration, gain=1.0, **parameters):
    return dict(kind=kind, start=start, duration=duration, gain=gain, **parameters)


def cue(slug, title, duration, use, layers, *, tags=(), peak=-12.0):
    return dict(slug=slug, title=title, duration=duration, use=use, layers=layers,
                tags=list(tags), peak=peak)


# Each cue has a hand-authored temporal and spectral structure. These are not
# pitch-shifted duplicates or imported/copyrighted sound samples.
FAMILIES = {
    "transitions": [
        cue("airy-page-turn", "Airy page turn", .56, "Move between news slides with a soft forward sweep.",
            [L("air",0,.53,.9, center=950, width=24, envelope="swell"), L("chirp",.12,.31,.10,f0=330,f1=840,envelope="swell")],tags=["whoosh","slide","soft"]),
        cue("evidence-zoom-in", "Evidence zoom in", .48, "Zoom from a source page into the exact evidence region.",
            [L("air",0,.45,.8,center=1700,width=15,envelope="rise"),L("chirp",.09,.35,.18,f0=260,f1=780,envelope="rise"),L("pluck",.37,.09,.16,f0=880)],tags=["zoom","source","rising"]),
        cue("context-zoom-out", "Context zoom out", .67, "Pull back from a detail to the comparison overview.",
            [L("air",0,.60,.9,center=850,width=35,envelope="fall"),L("chirp",.03,.45,.15,f0=650,f1=210,envelope="fall")],tags=["zoom","context","falling"]),
        cue("split-screen-open", "Split screen open", .61, "Open a two-model comparison panel.",
            [L("air",0,.25,.6,center=1250,width=20,envelope="swell"),L("air",.24,.34,.8,center=2200,width=14,envelope="swell"),L("tone",.26,.18,.13,f0=440,f1=440,partials=[1,.18])],tags=["comparison","two-stage","whoosh"]),
        cue("timeline-slide", "Timeline slide", .72, "Travel along a release timeline.",
            [L("air",0,.68,.85,center=1200,width=28,envelope="swell",tremolo=8),L("chirp",.07,.55,.11,f0=300,f1=450,envelope="swell")],tags=["timeline","ripple","slide"]),
        cue("soft-crossfade", "Soft crossfade", .82, "Bridge two calm explanatory sections.",
            [L("air",0,.80,.48,center=600,width=56,envelope="swell"),L("tone",.04,.69,.23,f0=220,f1=220,partials=[1,.12],envelope="swell"),L("tone",.13,.61,.12,f0=330,f1=330,envelope="swell")],tags=["crossfade","calm","warm"]),
        cue("chapter-marker", "Chapter marker", .92, "Introduce a new chapter with a brief restrained sonic signature.",
            [L("air",0,.31,.60,center=900,width=30,envelope="rise"),L("bell",.26,.61,.30,f0=392),L("bell",.43,.43,.15,f0=587.33)],tags=["chapter","signature","chime"]),
        cue("comparison-flip", "Comparison flip", .44, "Flip between a model output and its evaluation.",
            [L("chirp",0,.18,.21,f0=400,f1=1000,envelope="swell"),L("air",.13,.29,.82,center=1700,width=18,envelope="fall"),L("click",.24,.035,.19,f0=520)],tags=["flip","comparison","crisp"]),
        cue("cloud-handoff", "Cloud handoff", .78, "Move from one cloud provider to another.",
            [L("air",0,.72,.76,center=1550,width=23,envelope="swell"),L("tone",.05,.29,.17,f0=294,f1=294,envelope="swell"),L("tone",.36,.31,.18,f0=440,f1=440,envelope="swell")],tags=["cloud","handoff","two-tone"]),
        cue("next-section-lift", "Next section lift", .88, "Lift the presentation into the next development.",
            [L("chirp",0,.70,.23,f0=196,f1=784,envelope="rise",curve="exp"),L("air",.25,.58,.66,center=1100,width=28,envelope="swell"),L("bell",.66,.19,.20,f0=988)],tags=["section","lift","rising"]),
    ],
    "reveals": [
        cue("headline-reveal", "Headline reveal", .48, "Reveal a short news headline.",
            [L("kick",.02,.21,.55,f0=170,f1=74),L("air",.01,.22,.25,center=1050,width=30,envelope="fall"),L("bell",.07,.37,.18,f0=660)],tags=["headline","impact","soft"]),
        cue("model-name-arrival", "Model name arrival", .58, "Place an exact model version on screen.",
            [L("pluck",.03,.28,.47,f0=330,partials=[1,.18,.08]),L("bell",.15,.39,.24,f0=660),L("air",.03,.11,.20,center=1550,width=20,envelope="fall")],tags=["model","label","reveal"]),
        cue("price-tag-reveal", "Price tag reveal", .43, "Reveal a verified task cost or API price.",
            [L("click",.01,.035,.27,f0=620),L("bell",.04,.33,.38,f0=784),L("bell",.12,.24,.16,f0=1046.5)],tags=["price","cost","light"]),
        cue("benchmark-score-reveal", "Benchmark score reveal", .69, "Reveal a benchmark score without implying victory.",
            [L("kick",.01,.20,.34,f0=145,f1=82),L("tone",.12,.23,.29,f0=440,f1=440,partials=[1,.1],envelope="swell"),L("bell",.28,.36,.26,f0=880)],tags=["benchmark","score","neutral"]),
        cue("source-card-arrival", "Source card arrival", .35, "Bring in a dated source citation.",
            [L("air",0,.19,.47,center=800,width=44,envelope="rise"),L("pluck",.15,.16,.37,f0=520)],tags=["citation","source","compact"]),
        cue("prompt-panel-unfold", "Prompt panel unfold", .75, "Unfold the identical prompt supplied to each model.",
            [L("air",0,.37,.65,center=1050,width=35,envelope="swell"),L("pluck",.15,.15,.15,f0=392),L("air",.34,.37,.52,center=1450,width=22,envelope="fall"),L("pluck",.45,.22,.20,f0=523.25)],tags=["prompt","unfold","two-stage"]),
        cue("output-panel-arrival", "Output panel arrival", .64, "Bring an actual model output beside its benchmark evidence.",
            [L("kick",.01,.17,.33,f0=120,f1=62),L("air",.03,.30,.33,center=1100,width=33,envelope="fall"),L("pluck",.19,.25,.27,f0=349.23),L("bell",.30,.29,.12,f0=698.46)],tags=["output","panel","warm"]),
        cue("feature-spotlight", "Feature spotlight", .91, "Introduce a practical platform feature demonstration.",
            [L("air",0,.40,.42,center=1150,width=26,envelope="rise"),L("tone",.18,.32,.27,f0=262,f1=262,envelope="swell"),L("bell",.40,.47,.29,f0=524),L("bell",.52,.30,.09,f0=786)],tags=["feature","spotlight","lift"]),
        cue("takeaway-stamp", "Takeaway stamp", .32, "Place the qualified viewer recommendation on screen.",
            [L("kick",.01,.24,.64,f0=135,f1=82),L("click",.015,.045,.28,f0=430),L("pluck",.04,.23,.17,f0=294)],tags=["takeaway","stamp","restrained"]),
        cue("announced-release-reveal", "Announced release reveal", .98, "Reveal a verified announced release date.",
            [L("air",0,.30,.42,center=1500,width=21,envelope="rise"),L("bell",.21,.45,.26,f0=330),L("bell",.38,.46,.26,f0=440),L("bell",.58,.36,.24,f0=660)],tags=["announcement","release","sequence"]),
    ],
    "interface": [
        cue("soft-single-click", "Soft single click", .18, "Acknowledge a single UI selection.",
            [L("click",.02,.026,.58,f0=620),L("pluck",.025,.11,.23,f0=310)],tags=["click","ui","single"],peak=-15),
        cue("double-selection", "Double selection", .29, "Select two comparison inputs.",
            [L("click",.02,.025,.5,f0=520),L("click",.13,.036,.45,f0=710),L("pluck",.14,.12,.15,f0=355)],tags=["click","ui","double"],peak=-15),
        cue("toggle-on", "Toggle on", .27, "Enable a demonstrated platform option.",
            [L("chirp",.02,.11,.55,f0=300,f1=560,envelope="swell"),L("pluck",.09,.15,.22,f0=560)],tags=["toggle","on","rising"],peak=-15),
        cue("toggle-off", "Toggle off", .25, "Disable an option while explaining its tradeoff.",
            [L("click",.015,.026,.2,f0=540),L("chirp",.035,.17,.52,f0=470,f1=250,envelope="fall")],tags=["toggle","off","falling"],peak=-15),
        cue("tab-change", "Tab change", .30, "Change between evidence, output, and cost tabs.",
            [L("air",.01,.13,.30,center=1400,width=19,envelope="swell"),L("pluck",.11,.15,.5,f0=494,partials=[1,.1,.04])],tags=["tab","ui","soft"],peak=-15),
        cue("copy-prompt", "Copy prompt", .40, "Demonstrate copying a reusable prompt.",
            [L("click",.02,.025,.34,f0=660),L("click",.085,.025,.26,f0=660),L("bell",.14,.21,.42,f0=880)],tags=["copy","prompt","compact"],peak=-15),
        cue("filter-applied", "Filter applied", .38, "Apply a task, provider, or cost filter.",
            [L("pluck",.02,.09,.32,f0=740),L("pluck",.11,.09,.31,f0=554),L("pluck",.20,.14,.37,f0=440)],tags=["filter","ui","descending"],peak=-15),
        cue("expand-details", "Expand details", .45, "Expand methodology or the cost breakdown.",
            [L("pluck",.02,.15,.26,f0=330),L("air",.05,.32,.50,center=1000,width=33,envelope="rise"),L("pluck",.27,.14,.31,f0=660)],tags=["expand","details","ui"],peak=-15),
        cue("collapse-details", "Collapse details", .33, "Collapse an expanded detail panel.",
            [L("air",.01,.23,.45,center=1250,width=26,envelope="fall"),L("click",.16,.04,.32,f0=430),L("pluck",.17,.12,.18,f0=215)],tags=["collapse","details","ui"],peak=-15),
        cue("selection-triple", "Selection triple", .50, "Mark three selected features in a UI walkthrough.",
            [L("click",.02,.03,.44,f0=510),L("click",.17,.025,.33,f0=660),L("click",.31,.04,.30,f0=810),L("pluck",.32,.13,.16,f0=405)],tags=["selection","ui","three-step"],peak=-15),
    ],
    "confirmations": [
        cue("source-verified", "Source verified", .56, "Mark a claim whose source has been checked.",
            [L("bell",.02,.37,.48,f0=523.25),L("bell",.16,.35,.39,f0=783.99)],tags=["verified","source","confirmation"]),
        cue("test-complete", "Test complete", .66, "Indicate a completed practical model test.",
            [L("pluck",.02,.19,.31,f0=392),L("pluck",.19,.23,.31,f0=523.25),L("bell",.36,.25,.34,f0=659.25)],tags=["test","complete","three-note"]),
        cue("requirement-met", "Requirement met", .44, "Show that an output passes a defined task requirement.",
            [L("tone",.02,.34,.44,f0=440,f1=440,partials=[1,.08],envelope="swell"),L("tone",.05,.30,.24,f0=660,f1=660,envelope="swell")],tags=["pass","criterion","chord"]),
        cue("saved-to-library", "Saved to library", .71, "Show a reusable artifact being saved.",
            [L("click",.02,.03,.19,f0=600),L("pluck",.13,.28,.31,f0=330),L("bell",.33,.33,.39,f0=494)],tags=["save","library","confirmation"]),
        cue("comparison-ready", "Comparison ready", .59, "Indicate comparable test conditions are ready.",
            [L("pluck",.02,.21,.36,f0=440),L("pluck",.18,.21,.36,f0=440),L("bell",.32,.21,.39,f0=660)],tags=["comparison","ready","balanced"]),
        cue("caption-ready", "Caption ready", .36, "Acknowledge prepared captions or transcript.",
            [L("click",.02,.027,.17,f0=720),L("bell",.07,.25,.43,f0=698.46)],tags=["caption","ready","light"]),
        cue("cost-calculated", "Cost calculated", .79, "Show a calculation resolving to measured task cost.",
            [L("click",.02,.025,.17,f0=520),L("click",.12,.025,.17,f0=580),L("pluck",.24,.16,.25,f0=392),L("bell",.38,.35,.34,f0=587.33)],tags=["calculation","cost","resolution"]),
        cue("evidence-matched", "Evidence matched", .48, "Link a shown output to its run record and source evidence.",
            [L("pluck",.02,.17,.33,f0=349.23),L("pluck",.05,.17,.23,f0=523.25),L("bell",.20,.23,.34,f0=698.46)],tags=["evidence","matched","link"]),
        cue("step-complete", "Step complete", .28, "Mark an individual feature-demonstration step.",
            [L("pluck",.02,.20,.50,f0=587.33,partials=[1,.1]),L("click",.025,.023,.15,f0=900)],tags=["step","complete","compact"],peak=-15),
        cue("ready-for-post", "Ready for post", 1.08, "Finish an animation sequence and hand off to postproduction.",
            [L("bell",.03,.45,.29,f0=261.63),L("bell",.23,.51,.29,f0=392),L("bell",.44,.58,.32,f0=523.25),L("air",.50,.47,.12,center=1500,width=28,envelope="fall")],tags=["handoff","post","closing"]),
    ],
    "attention": [
        cue("methodology-note", "Methodology note", .51, "Draw gentle attention to an evaluation setup detail.",
            [L("tone",.02,.19,.46,f0=392,f1=392,envelope="swell"),L("tone",.28,.17,.31,f0=392,f1=392,envelope="swell")],tags=["methodology","note","neutral"]),
        cue("comparability-caveat", "Comparability caveat", .68, "Highlight that two published scores may not be directly comparable.",
            [L("tone",.02,.24,.37,f0=349.23,f1=349.23,envelope="swell"),L("tone",.32,.28,.33,f0=329.63,f1=329.63,envelope="swell"),L("air",.22,.24,.12,center=650,width=49,envelope="swell")],tags=["caveat","benchmark","gentle"]),
        cue("uncertain-result", "Uncertain result", .73, "Mark a result whose difference is inconclusive.",
            [L("tone",.03,.63,.37,f0=293.66,f1=293.66,envelope="swell"),L("tone",.11,.54,.20,f0=440,f1=440,envelope="swell",tremolo=2)],tags=["uncertainty","tie","soft"]),
        cue("price-basis-note", "Price basis note", .42, "Highlight input/output pricing or a subscription/API distinction.",
            [L("pluck",.02,.16,.40,f0=440),L("pluck",.20,.16,.32,f0=329.63)],tags=["pricing","basis","note"]),
        cue("dated-evidence", "Dated evidence", .61, "Call attention to the evidence capture date.",
            [L("click",.02,.026,.17,f0=480),L("tone",.09,.39,.42,f0=261.63,f1=261.63,envelope="swell"),L("pluck",.42,.13,.16,f0=523.25)],tags=["date","evidence","attention"]),
        cue("feature-limit", "Feature limit", .55, "Highlight a plan, region, or access limitation.",
            [L("tone",.02,.19,.37,f0=330,f1=330,envelope="swell"),L("tone",.25,.24,.34,f0=262,f1=262,envelope="swell")],tags=["feature","limit","gentle"]),
        cue("correction-marker", "Correction marker", .80, "Introduce a transparent correction to an earlier episode.",
            [L("air",0,.25,.28,center=900,width=39,envelope="rise"),L("tone",.18,.23,.30,f0=294,f1=294,envelope="swell"),L("bell",.40,.34,.26,f0=440)],tags=["correction","transparent","neutral"]),
        cue("check-the-source", "Check the source", .64, "Direct viewers to the linked source or run record.",
            [L("click",.02,.023,.16,f0=690),L("bell",.09,.30,.33,f0=587.33),L("pluck",.37,.21,.29,f0=440)],tags=["source","check","attention"]),
        cue("no-clear-winner", "No clear winner", .89, "Present an inconclusive result without a winner sound.",
            [L("tone",.05,.64,.30,f0=330,f1=330,envelope="swell"),L("tone",.12,.66,.29,f0=440,f1=440,envelope="swell"),L("air",.30,.49,.15,center=650,width=62,envelope="fall")],tags=["tie","inconclusive","balanced"]),
        cue("important-footnote", "Important footnote", .31, "Briefly point to a necessary qualification.",
            [L("pluck",.02,.15,.42,f0=349.23),L("air",.045,.22,.23,center=950,width=37,envelope="fall")],tags=["footnote","qualification","compact"],peak=-15),
    ],
    "data-motion": [
        cue("bar-chart-grow", "Bar chart grow", .83, "Animate a benchmark bar from zero to its verified value.",
            [L("chirp",.02,.65,.38,f0=220,f1=660,envelope="swell"),L("air",.16,.61,.35,center=1100,width=32,envelope="rise"),L("pluck",.68,.11,.18,f0=660)],tags=["chart","bar","growth"]),
        cue("line-trace", "Line trace", .94, "Trace a time series whose values come from canonical records.",
            [L("chirp",.02,.87,.33,f0=300,f1=620,envelope="swell",vibrato=3,vibrato_depth=.025),L("air",.07,.82,.22,center=1300,width=30,envelope="swell")],tags=["chart","line","trace"]),
        cue("scatter-point-place", "Scatter point place", .23, "Place a model on a quality-versus-cost scatterplot.",
            [L("pluck",.02,.15,.48,f0=660,partials=[1,.1]),L("air",.025,.05,.15,center=1900,width=15,envelope="fall")],tags=["chart","scatter","point"],peak=-15),
        cue("rank-reorder", "Rank reorder", .74, "Move comparison rows into a justified order.",
            [L("pluck",.03,.11,.18,f0=523.25),L("air",.06,.26,.47,center=1500,width=23,envelope="swell"),L("pluck",.32,.11,.19,f0=392),L("air",.35,.33,.47,center=950,width=34,envelope="swell"),L("pluck",.59,.10,.19,f0=659.25)],tags=["ranking","reorder","data"]),
        cue("table-row-highlight", "Table row highlight", .34, "Highlight a table row while retaining its source labels.",
            [L("air",.01,.21,.34,center=1150,width=29,envelope="rise"),L("tone",.10,.17,.44,f0=440,f1=440,envelope="swell")],tags=["table","row","highlight"],peak=-15),
        cue("numbers-resolve", "Numbers resolve", .62, "Resolve a brief number animation into the actual value.",
            [L("click",.02,.022,.20,f0=650),L("click",.105,.022,.19,f0=540),L("click",.19,.022,.17,f0=740),L("click",.275,.023,.15,f0=610),L("bell",.36,.20,.37,f0=784)],tags=["number","resolve","data"]),
        cue("interval-unfold", "Interval unfold", .82, "Expand a published confidence interval around a result.",
            [L("tone",.03,.55,.30,f0=392,f1=392,envelope="swell"),L("chirp",.12,.60,.17,f0=392,f1=330,envelope="swell"),L("chirp",.12,.60,.17,f0=392,f1=466.16,envelope="swell"),L("air",.09,.65,.24,center=1200,width=40,envelope="swell")],tags=["uncertainty","interval","unfold"]),
        cue("cost-stack-build", "Cost stack build", .88, "Build input, output, tools, and retries into total task cost.",
            [L("pluck",.02,.14,.32,f0=261.63),L("pluck",.18,.14,.29,f0=329.63),L("pluck",.34,.14,.29,f0=392),L("pluck",.50,.14,.29,f0=523.25),L("bell",.64,.20,.22,f0=659.25)],tags=["cost","stack","calculation"]),
        cue("savings-link", "Savings link", .57, "Connect the named baseline to a lower-cost qualifying alternative.",
            [L("chirp",.02,.30,.33,f0=660,f1=392,envelope="swell"),L("air",.10,.35,.33,center=1000,width=33,envelope="swell"),L("bell",.33,.19,.26,f0=523.25)],tags=["savings","baseline","link"]),
        cue("release-nodes-connect", "Release nodes connect", 1.14, "Connect four verified developments on a release timeline.",
            [L("pluck",.02,.17,.25,f0=294),L("air",.05,.24,.18,center=1000,width=32,envelope="swell"),L("pluck",.29,.17,.25,f0=370),L("air",.32,.24,.18,center=1300,width=28,envelope="swell"),L("pluck",.56,.17,.25,f0=440),L("air",.59,.24,.18,center=1600,width=23,envelope="swell"),L("bell",.83,.26,.29,f0=588)],tags=["release","timeline","nodes"]),
    ],
}

# Compact UI/data cues for economical storage and brief editorial punctuation.
# Time scales preserve tone pitches and semantic layer order. We keep a handful
# of longer composed cues where a timeline or closing animation benefits.
LONG_CUES = {"ready-for-post": .70, "release-nodes-connect": .76,
             "line-trace": .64, "no-clear-winner": .60}
for family, profiles in FAMILIES.items():
    if family == "transitions":
        continue
    for profile in profiles:
        target = LONG_CUES.get(profile["slug"], min(profile["duration"], .50))
        factor = target / profile["duration"]
        profile["duration"] = target
        for layer in profile["layers"]:
            layer["start"] *= factor
            layer["duration"] *= factor


def envelope(t, duration, name):
    q = np.clip(t / duration, 0, 1)
    if name == "swell":
        e = np.sin(np.pi * q) ** 1.4
    elif name == "rise":
        e = q ** 1.1 * (1 - q) ** .30
    elif name == "fall":
        e = (1 - q) ** 2.3
    elif name == "pluck":
        e = np.exp(-8.5 * q)
    elif name == "bell":
        e = np.exp(-4.7 * q)
    else:
        e = np.exp(-6 * q)
    # Minimum 4 ms attack and 12 ms release on every event; global fade follows.
    attack = min(.004, duration / 8)
    release = min(.012, duration / 6)
    e *= np.sin(np.pi/2 * np.minimum(t/attack,1)) ** 2
    e *= np.sin(np.pi/2 * np.minimum((duration-t)/release,1)) ** 2
    return e


def moving_average(x, size):
    return np.convolve(x, np.ones(size)/size, mode="same")


def render_layer(spec, rng):
    duration = spec["duration"]
    n = round(SR * duration)
    t = np.arange(n) / SR
    kind = spec["kind"]
    f0 = spec.get("f0", 440.)
    f1 = spec.get("f1", f0)
    if spec.get("curve") == "exp" and f0 != f1:
        a = math.log(f1/f0) / duration
        phase = 2*np.pi*f0*(np.exp(a*t)-1)/a
    else:
        phase = 2*np.pi*(f0*t + (f1-f0)*t*t/(2*duration))
    if spec.get("vibrato"):
        phase += (f0 * spec.get("vibrato_depth", .015) / spec["vibrato"]) * np.sin(2*np.pi*spec["vibrato"]*t)
    if kind == "air":
        noise = rng.normal(0,1,n)
        low = moving_average(noise,spec.get("width",32))
        # A soft noise carrier produces a narrow, less fatiguing airy spectrum.
        signal = low * np.sin(2*np.pi*spec.get("center",1200)*t)
        signal += .18*moving_average(noise,8)
        signal /= max(np.sqrt(np.mean(signal**2)),1e-9)*3
        env_name = spec.get("envelope","swell")
    elif kind == "click":
        noise = moving_average(rng.normal(0,1,n),5)
        signal = .40*noise + .60*np.sin(phase)
        env_name = "pluck"
    elif kind == "kick":
        freq = f1 + (f0-f1)*np.exp(-t/max(.015,duration/6))
        phase = 2*np.pi*np.cumsum(freq)/SR
        signal = np.sin(phase) + .06*np.sin(phase*2)
        env_name = "pluck"
    elif kind == "bell":
        signal = np.sin(phase) + .22*np.sin(2.01*phase)*np.exp(-t*12) + .085*np.sin(3.03*phase)*np.exp(-t*20)
        env_name = "bell"
    else:
        partials = spec.get("partials",[1,.055] if kind=="pluck" else [1])
        signal = sum(a*np.sin((i+1)*phase) for i,a in enumerate(partials))
        env_name = spec.get("envelope", "pluck" if kind=="pluck" else "swell")
    signal *= envelope(t,duration,env_name)
    if spec.get("tremolo"):
        signal *= .75 + .25*np.sin(2*np.pi*spec["tremolo"]*t)
    return signal * spec.get("gain",1)


def dbfs(value):
    return round(20*math.log10(max(value,1e-12)),3)


def generate():
    total = sum(len(v) for v in FAMILIES.values())
    assert total == 60
    records=[]
    checks=[]
    for family,profiles in FAMILIES.items():
        folder = ROOT/family
        folder.mkdir(exist_ok=True)
        for profile in profiles:
            asset_id = "sfx-"+profile["slug"]
            seed = int(hashlib.sha256(asset_id.encode()).hexdigest()[:16],16)
            rng = np.random.default_rng(seed)
            n = round(SR*profile["duration"])
            samples = np.zeros(n)
            for layer in profile["layers"]:
                event=render_layer(layer,rng)
                start=round(layer["start"]*SR)
                end=min(n,start+len(event))
                samples[start:end] += event[:end-start]
            # Gentle global boundaries; exact first/last zero samples.
            fi=min(round(.010*SR),n//8)
            fo=min(round(.022*SR),n//6)
            samples[:fi] *= np.sin(np.linspace(0,np.pi/2,fi))**2
            samples[-fo:] *= np.cos(np.linspace(0,np.pi/2,fo))**2
            samples[0]=samples[-1]=0
            samples *= 10**(profile["peak"]/20) / max(np.max(np.abs(samples)),1e-12)
            pcm=np.rint(samples*32767).astype("<i2")
            file=folder/(profile["slug"]+".wav")
            with wave.open(str(file),"wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(SR)
                w.writeframes(pcm.tobytes())
            normalized=pcm.astype(float)/32768
            peak=dbfs(np.max(np.abs(normalized)))
            rms=dbfs(np.sqrt(np.mean(normalized**2)))
            relative=file.relative_to(ROOT).as_posix()
            record=dict(id=asset_id,title=profile["title"],path=relative,
                tags=[family,*profile["tags"],"cloud-ai-show","original","narration-safe"],
                intended_use=profile["use"],kind="sound-effect",origin="original",
                license="CC0-1.0",creator="AI-Update-Sources production workflow",
                source_url=None,created_at="2026-10-13",duration_seconds=n/SR,
                sample_rate=SR,channels=1,bit_depth=16,format="PCM WAV",
                peak_dbfs=peak,rms_dbfs=rms,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
                bytes=file.stat().st_size,
                profile_layer_count=len(profile["layers"]),generator_version=VERSION,
                sound_design_note="Procedural original synthesis; no downloaded samples, speech, songs, or model services.",
                loudness_guidelines="Do not peak-normalize to 0 dBFS. Start the cue track at -6 dB gain under narration; -10 dB for caution notes. Duck a further 4-8 dB while speech overlaps. Adjust by listening after voiceover is added; these RMS values are not LUFS.")
            records.append(record)
            with wave.open(str(file),"rb") as w:
                decoded=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2")
                passed=(w.getnchannels()==1 and w.getsampwidth()==2 and w.getframerate()==SR
                    and w.getcomptype()=="NONE" and len(decoded)==n and peak<=-11.99
                    and np.max(np.abs(decoded.astype(np.int32)))<32767
                    and decoded[0]==0 and decoded[-1]==0 and np.any(decoded!=0))
            checks.append(dict(id=asset_id,path=relative,passed=bool(passed),
                duration_seconds=n/SR,peak_dbfs=peak,rms_dbfs=rms,first_sample=int(decoded[0]),
                last_sample=int(decoded[-1]),clipped_samples=int(np.count_nonzero(np.abs(decoded.astype(np.int32))>=32767)),
                fade_in_seconds=fi/SR,fade_out_seconds=fo/SR))
    assert len({r["sha256"] for r in records})==60
    assert all(x["passed"] for x in checks)
    (ROOT/"metadata.json").write_text(json.dumps(records,indent=2)+"\n")
    report=dict(generator_version=VERSION,wav_count=60,unique_audio_hashes=60,
        passed_count=sum(x["passed"] for x in checks),failed_count=sum(not x["passed"] for x in checks),
        sample_rate=SR,channels=1,bit_depth=16,format="uncompressed signed 16-bit PCM WAV",
        subsecond_cues=sum(r["duration_seconds"]<1 for r in records),
        cues_at_most_half_second=sum(r["duration_seconds"]<=.50 for r in records),
        duration_range_seconds=[min(r["duration_seconds"] for r in records),max(r["duration_seconds"] for r in records)],
        max_peak_dbfs=max(r["peak_dbfs"] for r in records),
        total_duration_seconds=round(sum(r["duration_seconds"] for r in records),3),
        total_wav_bytes=sum((ROOT/r["path"]).stat().st_size for r in records),
        verification_limits="PCM structure, unique file hashes, peaks, non-silence, and zero-boundary fades are verified. No real narration mix or PowerPoint playback has been tested. Equal hashes are excluded; subjective similarity is not mechanically certified.",
        checks=checks)
    (ROOT/"qa-report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="checks"},indent=2))


if __name__=="__main__":
    generate()
