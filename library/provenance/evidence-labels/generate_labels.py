#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
from html import escape
BASE=Path(__file__).parent
ITEMS=[
('company-reported','Company-reported','The provider reports this result; it is not independent validation.','source','report'),
('independent-evaluation','Independent evaluation','An identifiable evaluator published its own methods and results.','source','check'),
('show-tested','Tested by this show','Use only when the episode has preserved actual test outputs and settings.','source','flask'),
('published-test','Published test output','The output comes from a cited external test, not our own execution.','source','document'),
('objective-check','Objective check passed','Apply only after a verifiable criterion or executable check passes.','source','target'),
('same-prompt','Identical prompt','Inputs are shared; also disclose material settings and tool differences.','method','equal'),
('same-harness','Shared evaluation setup','Use only when relevant benchmark versions and evaluation conditions match.','method','grid'),
('methods-differ','Methods differ','Displayed results are not directly comparable under the available methods.','method','split'),
('single-demonstration','Single demonstration','This example does not establish broad reliability or superiority.','uncertainty','one'),
('small-sample','Limited sample','More representative tests are needed before making a broad recommendation.','uncertainty','dots'),
('confidence-interval','Published uncertainty','Keep the source interval and its meaning; do not invent error bars.','uncertainty','interval'),
('no-clear-winner','No clear winner','The available evidence does not justify a decisive ranking.','uncertainty','balance'),
('coverage-gap','Model coverage gap','Newer or untested models are absent; absence is not a failing score.','uncertainty','gap'),
('preliminary-result','Preliminary result','The source labels this result preliminary; preserve that qualifier.','uncertainty','clock'),
('historical-snapshot','Historical snapshot','This is dated evidence, not a claim about the current leader.','freshness','history'),
('current-price-checked','Price checked','Apply only after checking the relevant provider price and conditions.','cost','coin'),
('estimated-task-cost','Estimated cost','Display assumptions; do not present this as measured billed usage.','cost','calculator'),
('cost-per-success','Cost per successful task','Use total included costs divided by successfully completed tasks.','cost','fraction'),
('cloud-access-check','Cloud access needs checking','A published benchmark alone does not prove current cloud availability.','availability','cloud'),
('correction-issued','Correction recorded','Link the original claim, corrected finding, reason and affected assets.','corrections','revision'),
]
def glyph(name):
    variants={
    'report':'<rect x="68" y="45" width="90" height="118" rx="12"/><path d="M88 80h50M88 105h35M88 130h45"/>',
    'check':'<circle cx="115" cy="105" r="62"/><path d="M82 105l23 23 44-51"/>',
    'flask':'<path d="M92 47h46M104 47v53l-36 58q-8 14 14 14h70q20 0 12-17l-36-55V47M91 136h54"/>',
    'document':'<path d="M72 40h72l30 30v105H72zM140 40v34h34M94 110h50M94 135h60"/>',
    'target':'<circle cx="116" cy="107" r="62"/><circle cx="116" cy="107" r="34"/><circle cx="116" cy="107" r="8"/>',
    'equal':'<path d="M65 80h100M65 130h100"/>',
    'grid':'<rect x="53" y="44" width="124" height="124" rx="8"/><path d="M115 44v124M53 106h124"/>',
    'split':'<path d="M52 155l59-105 62 105M111 50v120M64 115h40M130 90h36"/>',
    'one':'<path d="M82 72l31-25v120M82 167h65"/>',
    'dots':'<circle cx="72" cy="84" r="10"/><circle cx="115" cy="84" r="10"/><circle cx="158" cy="84" r="10"/><path d="M65 125h100M87 157h56"/>',
    'interval':'<path d="M47 108h137M47 80v56M184 80v56"/><circle cx="115" cy="108" r="13"/>',
    'balance':'<path d="M115 43v127M59 72h112M59 72l-28 64h57zM170 72l-28 64h57zM81 171h68"/>',
    'gap':'<rect x="49" y="52" width="124" height="103" rx="9"/><path d="M68 80h45M68 110h27M128 118v-17q0-17 14-17t15 15q0 13-13 16M143 139h1"/>',
    'clock':'<circle cx="115" cy="105" r="63"/><path d="M115 65v42l30 21M67 176h100"/>',
    'history':'<path d="M53 85a65 65 0 1 1 2 55M53 85V44M53 85h41M116 71v38l30 15"/>',
    'coin':'<circle cx="109" cy="103" r="58"/><path d="M111 66v75M132 77q-42-17-42 8 0 16 31 19t1 26q-15 6-34-5M157 165l13 13 24-31"/>',
    'calculator':'<rect x="58" y="38" width="113" height="136" rx="14"/><path d="M77 65h75M77 90h75M80 115h8M112 115h8M145 115h8M80 147h8M112 147h8M145 147h8"/>',
    'fraction':'<path d="M45 108h146M71 58h31M133 43v31M59 147h48M143 135l18 18-18 18"/>',
    'cloud':'<path d="M55 145q-30 0-30-31t35-33q5-45 47-45 36 0 46 38 41-2 41 36t-38 35h-34M109 154v-22q0-17 16-17t17 13q0 11-14 16M128 176h1"/>',
    'revision':'<path d="M44 81a73 73 0 0 1 131-10M175 71V33M175 71h-39M184 133a73 73 0 0 1-129 6M55 139v37M55 139h41"/>',
    }
    return '<g transform="translate(15,35)" fill="none" stroke="#63dcec" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">'+variants[name]+'</g>'
def main():
    assets=BASE/'assets';assets.mkdir(parents=True,exist_ok=True);records=[]
    for slug,title,note,tag,icon in ITEMS:
        name='evidence-'+slug+'.svg';p=assets/name
        svg='<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="320" viewBox="0 0 1300 320"><title>'+escape(title)+'</title><desc>'+escape(note)+'</desc><rect x="8" y="8" width="1284" height="304" rx="36" fill="#10273a" stroke="#294e65" stroke-width="3"/>'+glyph(icon)+'<text x="260" y="118" fill="#f3f8fc" font-family="DejaVu Sans,sans-serif" font-size="43" font-weight="700">'+escape(title)+'</text><text x="260" y="179" fill="#efc26d" font-family="DejaVu Sans,sans-serif" font-size="19">EDITORIAL LABEL — APPLY ONLY WHEN ITS CONDITION IS VERIFIED</text><foreignObject/></svg>'
        # Use ordinary SVG text, never active HTML or external content.
        svg=svg.replace('<foreignObject/>','')
        words=note.split();lines=[];line=''
        for word in words:
            if len(line+' '+word)>77:lines.append(line);line=word
            else:line=(line+' '+word).strip()
        if line:lines.append(line)
        text=''.join(f'<text x="260" y="{229+i*31}" fill="#c0d5e3" font-family="DejaVu Sans,sans-serif" font-size="21">{escape(t)}</text>' for i,t in enumerate(lines))
        p.write_text(svg.replace('</svg>',text+'</svg>'))
        records.append({'id':'evidence-'+slug,'title':title,'path':'assets/'+name,'category':'evidence-label','tags':['evidence','benchmark','editorial',tag],'intended_use':note,'dimensions':{'width':1300,'height':320},'kind':'evidence-label','origin':'original','license':'CC0-1.0','attribution':'AI Update Sources','source_url':None,'rights_status':'original','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'requires_verification':True})
    (BASE/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
    (BASE/'README.md').write_text('# Evidence labels\n\n20 original reusable labels with distinct editorial meanings and symbols. Apply only when their documented condition holds. They do not establish that a claim is verified.\n\nOriginal label graphics: CC0 1.0. https://creativecommons.org/publicdomain/zero/1.0/\n')
    print(len(records))
if __name__=='__main__':main()
