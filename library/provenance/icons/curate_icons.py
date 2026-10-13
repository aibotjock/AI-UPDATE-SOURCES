import json, pathlib, tarfile, hashlib, re, xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).parent
SHA='70562c1ee1c4fdcf736fe97bc893fb8511927934'
GROUPS={
 'cloud-infrastructure': ('Cloud hosting, storage, deployment and network service explanations', '''cloud cloud-cog cloud-download cloud-upload cloud-check cloud-alert cloud-off cloud-backup server server-cog server-crash server-off database database-backup database-zap database-search hard-drive hard-drive-download hard-drive-upload network ethernet router wifi cable computer monitor monitor-cloud laptop smartphone tablet globe globe-lock earth satellite radio-tower'''),
 'ai-compute': ('AI agents, reasoning, compute capacity and workflow orchestration', '''brain brain-circuit brain-cog bot bot-message-square bot-off circuit-board cpu gpu microchip memory-stick binary variable function-square workflow waypoints blocks box boxes component puzzle sparkles wand-sparkles lightbulb lightbulb-off zap gauge power atom infinity layers layers-2 layers-3'''),
 'code-engineering': ('Coding model demonstrations, software tools and development workflows', '''code code-xml code-square code-2 terminal square-terminal braces brackets bug bug-off bug-play git-branch git-commit-horizontal git-compare git-fork git-merge git-pull-request git-pull-request-arrow git-pull-request-closed git-pull-request-create git-pull-request-draft file-code file-code-2 folder-code regex test-tube test-tubes flask-conical flask-round wrench hammer screwdriver construction container package package-check package-search'''),
 'data-benchmarks': ('Benchmark results, analytical evidence, rankings and model performance comparisons', '''chart-bar chart-bar-big chart-bar-increasing chart-bar-stacked chart-column chart-column-big chart-column-increasing chart-column-stacked chart-line chart-no-axes-combined chart-no-axes-column chart-no-axes-column-increasing chart-no-axes-gantt chart-pie chart-scatter area-chart chart-area chart-network chart-spline chart-candlestick table table-2 table-properties table-cells-merge table-cells-split table-columns-split table-rows-split sheet list-ordered list-filter list-checks ranking medal trophy award target crosshair sigma calculator percent percentage-circle trending-up trending-down trending-up-down equal equal-not'''),
 'documents-reference': ('Document analysis, citations, reference sources and reusable episode archives', '''file file-text file-search file-search-2 file-check file-check-2 file-clock file-diff file-spreadsheet file-json file-json-2 file-type file-type-2 file-input file-output files folder folder-open folder-search folder-check folder-clock folder-sync archive archive-restore archive-x book book-open book-open-text book-marked book-check book-copy book-text notebook notebook-pen notebook-tabs library library-big bookmark bookmarks sticky-note clipboard clipboard-check clipboard-list clipboard-copy clipboard-paste clipboard-pen clipboard-type'''),
 'media-presentation': ('Images, audio, video, screenshots, slide composition and episode production', '''image image-plus image-minus image-off image-up image-down images image-play image-upscale camera camera-off aperture scan scan-line scan-text scan-search scan-eye scan-face film clapperboard video video-off videocamera audio-lines audio-waveform mic mic-off headphones volume volume-1 volume-2 volume-x music music-2 music-3 music-4 play pause square square-stop circle-play circle-pause circle-stop skip-back skip-forward rewind fast-forward picture-in-picture picture-in-picture-2 presentation projector screen-share screen-share-off captions closed-caption subtitles crop frame gallery-horizontal gallery-vertical gallery-thumbnails panels-top-left palette paintbrush swatch-book contrast blend'''),
 'communication': ('Prompts, model responses, collaboration and assistant conversation features', '''message-circle message-circle-code message-circle-more message-circle-question-mark message-circle-warning message-square message-square-code message-square-diff message-square-more message-square-quote message-square-text messages-square send send-horizontal mail mail-check mail-open mail-search mail-warning inbox at-sign speech text-quote quote languages translate user users user-round user-round-check user-round-cog user-round-search contact contact-round handshake share share-2 rss bell bell-ring bell-off'''),
 'security-privacy': ('Cloud account security, privacy controls, permissions and service trust', '''shield shield-check shield-alert shield-off shield-question-mark shield-ellipsis shield-user shield-ban shield-x shield-half shield-plus lock lock-keyhole lock-open lock-keyhole-open key key-round key-square fingerprint id-card badge-check badge-alert badge-help badge-info badge-x badge-minus badge-plus file-key file-lock folder-key folder-lock eye eye-off scan-lock vault circle-user circle-user-round user-lock cookie'''),
 'time-performance': ('Release timelines, latency, response speed, scheduling and status monitoring', '''clock clock-1 clock-2 clock-3 clock-4 clock-5 clock-6 clock-7 clock-8 clock-9 clock-10 clock-11 clock-12 timer timer-off timer-reset stopwatch hourglass calendar calendar-days calendar-clock calendar-check calendar-check-2 calendar-cog calendar-search calendar-sync history alarm-clock alarm-clock-check watch refresh-cw refresh-ccw rotate-cw rotate-ccw loader loader-circle loader-pin-circle circle-gauge activity signal signal-high signal-low signal-medium signal-zero'''),
 'cost-value': ('Pricing, subscriptions, billing, savings and usage-limit explanations', '''dollar-sign banknote banknote-arrow-down banknote-arrow-up banknote-x coins wallet wallet-cards wallet-minimal credit-card receipt receipt-text receipt-cent receipt-dollar receipt-euro receipt-pound-sterling receipt-indian-rupee receipt-japanese-yen receipt-russian-ruble receipt-swiss-franc badge-dollar-sign badge-percent badge-cent badge-euro badge-pound-sterling badge-indian-rupee badge-japanese-yen badge-russian-ruble badge-swiss-franc circle-dollar-sign piggy-bank landmark scale scale-3d ticket ticket-percent tags tag shopping-cart shopping-bag store gift badge'''),
 'navigation-actions': ('Progressive reveals, comparisons, next steps and movement within cloud interfaces', '''arrow-up arrow-down arrow-left arrow-right arrow-up-right arrow-down-right arrow-down-left arrow-up-left arrows-up-from-line arrows-down-to-line arrow-right-left arrow-up-down arrow-down-up move move-horizontal move-vertical move-diagonal move-diagonal-2 move-right move-left move-up move-down chevron-right chevron-left chevron-up chevron-down chevrons-left-right chevrons-up-down corner-down-right corner-up-right corner-left-down corner-left-up corner-right-down corner-right-up corner-up-left corner-down-left navigation navigation-2 compass route signpost signpost-big external-link link link-2 unlink unlink-2 download upload import export log-in log-out'''),
 'interface-features': ('Cloud platform controls, accessibility, advanced settings and feature tutorials', '''settings settings-2 sliders-horizontal sliders-vertical toggle-left toggle-right panel-left panel-right panel-top panel-bottom panels-left-bottom panel-left-open panel-left-close panel-right-open panel-right-close layout-dashboard layout-grid layout-list layout-panel-left layout-panel-top layout-template columns-2 columns-3 columns-4 rows-2 rows-3 rows-4 fullscreen maximize maximize-2 minimize minimize-2 zoom-in zoom-out mouse-pointer mouse-pointer-2 mouse-pointer-click touchpad touchpad-off keyboard keyboard-music keyboard-off accessibility type text text-cursor text-cursor-input text-select text-selection bold italic underline strikethrough heading heading-1 heading-2 heading-3 highlighter baseline case-sensitive a-large-small a-arrow-down a-arrow-up'''),
 'evidence-quality': ('Verification, uncertainty, warnings, test outcomes and actionable recommendation summaries', '''check check-check circle-check circle-check-big square-check square-check-big circle-x square-x x circle-alert triangle-alert octagon-alert info circle-help circle-question-mark circle-ellipsis ellipsis ellipsis-vertical octagon-x ban circle-minus circle-plus plus minus square-plus square-minus thumbs-up thumbs-down star star-half star-off flag flag-triangle-left flag-triangle-right badge-question-mark circle-dot circle-dashed circle-fading-plus circle-fading-arrow-up circle-slash circle-slash-2 list list-todo list-collapse list-restart list-start list-end list-tree list-video list-music list-plus list-minus list-x'''),
 'search-discovery': ('Source discovery, web research, traceable references and platform search features', '''search search-check search-code search-slash search-x search-alert search-cog telescope binoculars radar focus map map-pinned map-pin map-pin-check map-pin-off map-pins map-plus earth-lock globe-2 globe-pointer globe-search globe-x globe-check globe-cog globe-off newspaper radio podcast megaphone megaphone-off locate locate-fixed locate-off'''),
 'workflow-productivity': ('Practical tasks, feature access, plans, saved projects and organizational workflows', '''briefcase briefcase-business briefcase-conveyor-belt briefcase-medical building building-2 door-open door-closed home house house-plug list-filter-plus filter funnel funnel-plus funnel-x copy copy-check copy-plus copy-minus copy-x copy-slash scissors scissors-line split merge combine replace replace-all repeat repeat-1 repeat-2 recycle undo undo-2 redo redo-2 save save-all save-off trash trash-2 eraser pencil pen pen-tool ruler drafting-compass stamp pin pin-off paperclip hand hand-helping hand-pointer grab grip grip-horizontal grip-vertical pointer pointer-off select lasso lasso-select square-dashed-mouse-pointer square-mouse-pointer mouse-pointer-ban bookmark-check bookmark-plus bookmark-minus bookmark-x bookmark-pen heart-handshake badge-help'''),
}

# Favor concept diversity in the first 21–22 choices per theme. Status variants
# remain available only when they convey a different operational meaning.
PRIORITIES={
 'code-engineering': 'code code-xml terminal square-terminal braces brackets regex bug bug-play git-branch git-commit-horizontal git-compare git-fork git-merge git-pull-request file-code folder-code test-tube flask-conical wrench container package',
 'documents-reference': 'file-text file-search file-check file-clock file-diff file-spreadsheet file-type file-input file-output files folder-open folder-search folder-check folder-sync archive archive-restore book book-open book-open-text notebook library bookmark clipboard clipboard-check',
 'media-presentation': 'image images image-play image-upscale camera aperture scan-text scan-search film clapperboard video audio-lines audio-waveform mic headphones volume-2 music play pause presentation projector screen-share captions crop palette',
 'communication': 'message-circle message-circle-code message-circle-question-mark message-square message-square-code message-square-diff message-square-quote message-square-text messages-square send mail mail-check mail-open mail-search inbox at-sign speech text-quote quote languages user users share rss bell',
 'security-privacy': 'shield shield-check shield-alert shield-user shield-ban shield-x shield-half lock lock-keyhole lock-open key key-round id-card badge-check badge-alert badge-info file-key file-lock folder-key folder-lock eye eye-off vault cookie',
 'time-performance': 'clock timer timer-off timer-reset hourglass calendar calendar-days calendar-clock calendar-check calendar-cog calendar-search calendar-sync alarm-clock alarm-clock-check watch refresh-cw refresh-ccw loader loader-circle circle-gauge activity signal signal-high signal-low',
 'cost-value': 'dollar-sign banknote banknote-arrow-down banknote-arrow-up coins wallet wallet-cards credit-card receipt receipt-text receipt-cent badge-dollar-sign badge-percent circle-dollar-sign piggy-bank landmark scale ticket ticket-percent tags tag shopping-cart gift',
 'navigation-actions': 'arrow-up arrow-down arrow-left arrow-right arrow-right-left arrow-up-down move move-horizontal move-vertical chevron-right chevron-left chevron-up chevron-down compass route signpost external-link link link-2 download upload log-in log-out',
 'interface-features': 'settings settings-2 sliders-horizontal sliders-vertical toggle-left toggle-right panel-left panel-right layout-dashboard layout-grid layout-list layout-template fullscreen maximize zoom-in zoom-out mouse-pointer-click keyboard accessibility type highlighter text-cursor a-large-small',
 'evidence-quality': 'check check-check circle-check square-check circle-x square-x circle-alert triangle-alert info circle-question-mark ban thumbs-up thumbs-down star star-half flag target crosshair list-checks list-todo list-tree circle-dot circle-dashed equal-not',
 'search-discovery': 'search search-check search-code search-x search-alert telescope binoculars radar focus map map-pinned earth-lock globe-lock globe-x globe-check newspaper radio rss megaphone locate locate-fixed scan-search external-link',
 'workflow-productivity': 'briefcase briefcase-business building list-filter-plus funnel funnel-plus copy copy-check scissors split merge combine replace repeat recycle undo redo save save-all trash eraser pencil pen-tool ruler stamp pin paperclip hand-helping grip',
}
for category, prioritized in PRIORITIES.items():
    use, fallback=GROUPS[category]
    GROUPS[category]=(use, ' '.join(dict.fromkeys((prioritized+' '+fallback).split())))

def geometry(e):
    return (e.tag.split('}')[-1], tuple(sorted(e.attrib.items())), tuple(geometry(x) for x in e))

def build():
    tar=tarfile.open(ROOT/'lucide-static.tgz')
    tags=json.load(tar.extractfile('package/tags.json'))
    source_tree=json.loads((ROOT/'source-tree.json').read_text())
    source_paths={e['path']:e['sha'] for e in source_tree['tree'] if e['type']=='blob'}
    candidates={}; missing=[]
    for category,(use,names) in GROUPS.items():
        candidates[category]=[]
        for name in names.split():
            if name in tags and 'icons/'+name+'.svg' in source_paths:
                candidates[category].append(name)
            else: missing.append(name)
    selected=[]; taken=set(); fingerprints=set()
    # Round robin keeps broad editorial coverage instead of exhausting the first category.
    while len(selected)<320:
        advanced=False
        for category,names in candidates.items():
            while names:
                name=names.pop(0)
                if name in taken: continue
                raw=tar.extractfile('package/icons/'+name+'.svg').read()
                root=ET.fromstring(raw)
                shape=hashlib.sha256(repr(tuple(geometry(e) for e in root)).encode()).hexdigest()
                if shape in fingerprints: continue
                selected.append((category,name,raw,root,shape));taken.add(name);fingerprints.add(shape);advanced=True
                break
            if len(selected)==320: break
        if not advanced: raise RuntimeError(f'Only {len(selected)} valid candidates')
    out=ROOT/'lucide';out.mkdir(exist_ok=True)
    for previous in out.glob('*.svg'): previous.unlink()
    license_bytes=tar.extractfile('package/LICENSE').read()
    (ROOT/'LICENSE-LUCIDE.txt').write_bytes(license_bytes)
    records=[]
    for category,name,raw,root,shape in selected:
        p=out/(name+'.svg');p.write_bytes(raw)
        records.append({
         'id':'lucide-'+name,
         'title':name.replace('-',' ').title(),
         'path':'lucide/'+name+'.svg',
         'tags':list(dict.fromkeys(['lucide','icon','cloud-ai-show',category]+tags[name])),
         'intended_use':GROUPS[category][0],
         'dimensions':{'width':24,'height':24,'viewBox':root.attrib.get('viewBox')},
         'kind':'icon', 'origin':'third-party',
         'source_url':f'https://github.com/lucide-icons/lucide/blob/{SHA}/icons/{name}.svg',
         'source_commit':SHA,
         'source_blob_sha':source_paths['icons/'+name+'.svg'],
         'distribution_url':'https://registry.npmjs.org/lucide-static/-/lucide-static-1.55.0.tgz',
         'source_version':'lucide-static 1.55.0',
         'license':'ISC; bundled license also includes MIT notice for Feather-derived icons',
         'license_file':'LICENSE-LUCIDE.txt',
         'attribution':'Lucide Icons and Contributors; Feather-derived icons: Cole Bemis. See bundled LICENSE-LUCIDE.txt.',
         'modification':'Unmodified SVG from official lucide-static package; upstream license and version comment retained.',
         'reuse_status':'licensed-commercial-and-editorial; retain bundled copyright and permission notices',
         'sha256':hashlib.sha256(raw).hexdigest(),
         'geometry_sha256':shape,
        })
    (ROOT/'assets.json').write_text(json.dumps(records,indent=2)+'\n')
    (ROOT/'manifest.json').write_text(json.dumps({'assets':records},indent=2)+'\n')
    report={'assets':len(records),'unique_geometry':len(fingerprints),'categories':{k:sum(r['tags'][3]==k for r in records) for k in GROUPS},'source_commit':SHA,'missing_candidate_names':sorted(set(missing)),'package_sha256':hashlib.sha256((ROOT/'lucide-static.tgz').read_bytes()).hexdigest(),'package_integrity':json.loads((ROOT/'package-metadata.json').read_text())['dist']['integrity']}
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'README.md').write_text('''# Cloud AI show workflow icons\n\n320 distinct Lucide SVG icons covering cloud infrastructure, AI compute, programming, benchmark evidence, documents, media, communication, security, performance, pricing, navigation, platform features, source discovery and productivity. These are editorial workflow symbols, not company logos, model results, or benchmark evidence.\n\nThe SVGs are unchanged extracts from the official `lucide-static` npm package, version 1.55.0. Git tag 1.55.0 resolves to commit `'''+SHA+'''`. Each asset record links to its immutable upstream SVG and includes its upstream Git blob SHA.\n\nRetain `LICENSE-LUCIDE.txt` with copies of this collection. That upstream license includes ISC terms and the MIT terms and attribution for Feather-derived assets. Never present these icons as official brand logos.\n\nEach file is 24 × 24 SVG with transparent background, `currentColor` stroke, no external resources and no scripts. It can be recolored or scaled for an episode as a derived asset; keep the source copy and metadata.\n\n`assets.json` contains individual provenance and intended use. `verification.json` records distinct geometry checks and package integrity. Full-screen contact sheets are preview aids and not counted as individual assets.\n''')
    print(json.dumps(report,indent=2))

if __name__=='__main__': build()
