#!/usr/bin/env python3
"""Retrieve pinned, unmodified brand SVGs with honest provenance records."""
import concurrent.futures
import hashlib
import io
import json
import pathlib
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent
SHA = "bcdb7c82792a854c2967f7328e11a30205ea584d"
REPO = "https://github.com/lobehub/lobe-icons"
RAW = f"https://raw.githubusercontent.com/lobehub/lobe-icons/{SHA}/"
ENTRIES = [
    ("openai", "OpenAI / ChatGPT", "https://openai.com/brand/", "openai chatgpt cloud-api assistant"),
    ("anthropic", "Anthropic", "https://www.anthropic.com/", "anthropic cloud-api company"),
    ("claude", "Claude", "https://claude.ai/", "anthropic claude cloud assistant"),
    ("google", "Google", "https://about.google/brand-resource-center/", "google company cloud"),
    ("gemini", "Google Gemini", "https://gemini.google.com/", "google gemini cloud assistant"),
    ("microsoft", "Microsoft", "https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks", "microsoft company cloud"),
    ("copilot", "Microsoft Copilot", "https://copilot.microsoft.com/", "microsoft copilot cloud assistant"),
    ("meta", "Meta / Meta AI", "https://about.meta.com/brand/resources/meta/company-brand/", "meta meta-ai cloud assistant"),
    ("nvidia", "NVIDIA", "https://www.nvidia.com/en-us/about-nvidia/legal-info/", "nvidia cloud-api company"),
    ("xai", "xAI", "https://x.ai/", "xai company cloud-api"),
    ("grok", "Grok", "https://grok.com/", "xai grok cloud assistant"),
    ("deepseek", "DeepSeek", "https://www.deepseek.com/", "deepseek china cloud-api assistant"),
    ("zai", "Z.ai / GLM", "https://z.ai/", "zai glm china cloud-api assistant"),
    ("qwen", "Qwen", "https://qwen.ai/", "alibaba qwen china cloud assistant"),
    ("alibaba", "Alibaba", "https://www.alibabagroup.com/", "alibaba china company"),
    ("alibabacloud", "Alibaba Cloud", "https://www.alibabacloud.com/", "alibaba qwen cloud-api provider"),
    ("aws", "Amazon Web Services", "https://aws.amazon.com/trademark-guidelines/", "amazon aws cloud provider"),
    ("bedrock", "Amazon Bedrock", "https://aws.amazon.com/bedrock/", "amazon bedrock cloud-api model-provider"),
    ("mistral", "Mistral AI", "https://mistral.ai/", "mistral cloud-api assistant"),
    ("cohere", "Cohere", "https://cohere.com/", "cohere enterprise cloud-api"),
    ("perplexity", "Perplexity", "https://www.perplexity.ai/", "perplexity research cloud assistant"),
    ("moonshot", "Moonshot AI", "https://www.moonshot.ai/", "moonshot kimi china cloud-api"),
    ("kimi", "Kimi", "https://www.kimi.com/", "moonshot kimi china cloud assistant"),
    ("minimax", "MiniMax", "https://www.minimax.io/", "minimax china cloud-api"),
    ("doubao", "Doubao", "https://www.doubao.com/", "bytedance doubao china cloud assistant"),
    ("baidu", "Baidu", "https://www.baidu.com/", "baidu ernie china cloud"),
    ("tencent", "Tencent", "https://www.tencent.com/", "tencent hunyuan china cloud"),
    ("hunyuan", "Tencent Hunyuan", "https://hunyuan.tencent.com/", "tencent hunyuan china cloud-api"),
    ("bytedance", "ByteDance", "https://www.bytedance.com/", "bytedance doubao china cloud"),
    ("huggingface", "Hugging Face", "https://huggingface.co/brand", "huggingface inference cloud-api provider"),
    ("together", "Together AI", "https://www.together.ai/", "together inference cloud-api provider"),
    ("groq", "Groq", "https://groq.com/", "groq inference cloud-api provider"),
    ("fireworks", "Fireworks AI", "https://fireworks.ai/", "fireworks inference cloud-api provider"),
    ("replicate", "Replicate", "https://replicate.com/", "replicate inference cloud-api provider"),
    ("ai21", "AI21 Labs", "https://www.ai21.com/", "ai21 jamba cloud-api"),
    ("deepinfra", "DeepInfra", "https://deepinfra.com/", "deepinfra inference cloud-api provider"),
    ("azure", "Microsoft Azure", "https://azure.microsoft.com/", "microsoft azure cloud model-provider"),
    ("cerebras", "Cerebras", "https://www.cerebras.ai/", "cerebras inference cloud-api provider"),
    ("openrouter", "OpenRouter", "https://openrouter.ai/", "openrouter model-routing cloud-api provider"),
    ("cloudflare", "Cloudflare / Workers AI", "https://www.cloudflare.com/", "cloudflare workers-ai cloud-api provider"),
]

def download(url):
    req = urllib.request.Request(url, headers={"User-Agent": "AI-Update-Sources asset provenance collector"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()

def one(entry):
    slug, title, official_ref, tags = entry
    name = "kimi.svg" if slug == "kimi" else (slug + "-color.svg" if slug + "-color.svg" in names else slug + ".svg")
    if name not in names:
        raise ValueError(f"No upstream mark for {slug}")
    url = RAW + "packages/static-svg/icons/" + name
    dest = ROOT / "assets" / name
    data = dest.read_bytes() if dest.exists() else download(url)
    xml = ET.fromstring(data)
    if not xml.tag.endswith("svg"):
        raise ValueError(f"Not SVG: {name}")
    for element in xml.iter():
        if element.tag.split("}")[-1] in {"script", "foreignObject"}:
            raise ValueError(f"Active content found: {name}")
        for key, value in element.attrib.items():
            if key.split("}")[-1] in {"href", "src"} and not value.startswith(("#", "data:")):
                raise ValueError(f"External SVG reference: {name}")
    dest.write_bytes(data)
    png = ROOT / "previews" / (slug + ".png")
    # Inkscape does not resolve upstream CSS em page dimensions. Normalize only
    # the temporary rendering viewport; all source paths, colors and marks stay
    # intact, and the distributed upstream SVG is preserved byte-for-byte.
    render_xml = ET.fromstring(data)
    view = render_xml.get("viewBox", "0 0 24 24").split()
    render_xml.set("width", view[2])
    render_xml.set("height", view[3])
    render_xml.set("color", "#000000")
    helper = ROOT / "previews" / (slug + "-render-helper.svg")
    ET.ElementTree(render_xml).write(helper)
    try:
        subprocess.run(["inkscape", str(helper), "--export-type=png", "--export-width=600", "--export-background=#ffffff", "--export-background-opacity=1", "--export-filename=" + str(png)], check=True, capture_output=True)
    finally:
        helper.unlink(missing_ok=True)
    im = Image.open(png).convert("RGB")
    white = Image.new("RGB", im.size, "white")
    from PIL import ImageChops
    if ImageChops.difference(im, white).getbbox() is None:
        raise ValueError(f"Blank mark: {name}")
    return {
        "id": "brand-" + slug,
        "title": title,
        "category": "brand-logo",
        "path": "brands/assets/" + name,
        "relative_path": "assets/" + name,
        "tags": tags.split(),
        "use": "Unaltered identifying brand mark beside cloud model/service comparisons, announcements, or platform feature demonstrations; never imply endorsement.",
        "source_url": url,
        "source_repository": REPO,
        "source_commit": SHA,
        "source_path": "packages/static-svg/icons/" + name,
        "origin": "community-maintainer-sourced; not an official brand download",
        "official_origin": False,
        "official_brand_reference_url": official_ref,
        "official_brand_reference_status": "Reference supplied for review; no independent brand approval is asserted.",
        "license": "MIT (upstream repository license; trademark rights are separate)",
        "license_url": RAW + "LICENSE",
        "license_path": "brands/licenses/lobehub-MIT.txt",
        "attribution": "LobeHub lobe-icons contributors, MIT; Copyright (c) 2023 LobeHub. Referenced brand names and marks belong to their respective owners.",
        "rights_status": "trademark-editorial-use-review",
        "rights_note": "MIT notice preserved for the repository-distributed asset. It does not grant trademark rights or independently clear brand use. Review current owner guidelines before publication; use only for accurate editorial identification, without endorsement or logo alteration.",
        "approval_status": "not-independently-brand-cleared",
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "modified": False,
        "preview_path": "brands/previews/" + slug + ".png",
    }

if __name__ == "__main__":
    for folder in ["assets", "previews", "licenses"]:
        (ROOT / folder).mkdir(exist_ok=True)
    listing = json.loads((ROOT / "upstream_listing.json").read_text())
    names = {item["name"] for item in listing}
    for relative, upstream in [("licenses/lobehub-MIT.txt", "LICENSE"), ("licenses/upstream-README.md", "README.md")]:
        if not (ROOT / relative).exists():
            (ROOT / relative).write_bytes(download(RAW + upstream))
    rows = []
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        tasks = {pool.submit(one, entry): entry[0] for entry in ENTRIES}
        for future in concurrent.futures.as_completed(tasks):
            try:
                row = future.result()
                rows.append(row)
                print("OK", row["id"], flush=True)
            except Exception as exc:
                errors.append({"brand": tasks[future], "error": str(exc)})
                print("ERROR", tasks[future], str(exc), flush=True)
    rows.sort(key=lambda row: next(i for i,e in enumerate(ENTRIES) if row["id"] == "brand-" + e[0]))
    if len({row["sha256"] for row in rows}) != len(rows):
        raise RuntimeError("Duplicate logo bytes")
    (ROOT / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    (ROOT / "download-errors.json").write_text(json.dumps(errors, indent=2) + "\n")
    W, H, COLS = 2200, 2640, 5
    sheet = Image.new("RGB", (W,H), "#111b2d")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    draw.text((35,22), "CLOUD AI BRAND MARKS | 40 DISTINCT COMPANY / PRODUCT IDENTITIES", font=font, fill="white")
    draw.text((35,58), "Community-maintained LobeHub SVGs, pinned commit; original marks unaltered. Trademark review required.", font=small, fill="#b6c5df")
    for i,row in enumerate(rows):
        x = 25 + (i % COLS) * 435
        y = 100 + (i // COLS) * 310
        draw.rounded_rectangle((x,y,x+410,y+286), radius=16, fill="white")
        mark = Image.open(ROOT / row["preview_path"].replace("brands/", "", 1)).convert("RGB")
        mark.thumbnail((280,185), Image.Resampling.LANCZOS)
        sheet.paste(mark, (x+(410-mark.width)//2, y+20+(190-mark.height)//2))
        label = row["title"]
        bounds = draw.textbbox((0,0), label, font=font)
        if bounds[2] > 392:
            chosen = small
        else:
            chosen = font
        width = draw.textbbox((0,0), label, font=chosen)[2]
        draw.text((x+(410-width)//2,y+223),label,font=chosen,fill="#17243c")
        draw.text((x+14,y+258),row["id"],font=small,fill="#536a88")
    sheet.save(ROOT / "contact-sheet.jpg", quality=92)
    print(json.dumps({"downloaded":len(rows), "errors":errors,"unique_sha256":len({row['sha256'] for row in rows})}), flush=True)
