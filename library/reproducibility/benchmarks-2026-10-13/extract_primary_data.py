"""Extract primary benchmark data and build accurate, source-cited SVG assets.

Run acquisition extraction once, then the saved output/generate_charts.py can
regenerate assets using only the factual datasets in output/data/.
"""
from pathlib import Path
import json, hashlib, csv, re, datetime, shutil
from lxml import html
OUT=Path(__file__).parent
P=OUT.parent
(OUT/'data').mkdir(parents=True,exist_ok=True)

def flight(name):
    dom=html.fromstring((P/(name+'.txt')).read_text())
    parts=[]
    for script in dom.xpath('//script'):
        s=script.text or ''
        if s.startswith('self.__next_f.push('):
            try:
                x=json.loads(s[len('self.__next_f.push('):-1])
                if len(x)>1 and isinstance(x[1],str):parts.append(x[1])
            except (ValueError,TypeError):pass
    return ''.join(parts)

def list_after(s,key):
    k=s.index('"'+key+'":')
    return json.JSONDecoder().raw_decode(s[s.index('[',k):])[0]

af=flight('arena');aa=flight('aa')
leaderboard_start=af.index('"leaderboard":{')+len('"leaderboard":')
leaderboard=json.JSONDecoder().raw_decode(af[leaderboard_start:])[0]
assert leaderboard['params']['category']=='overall'
assert leaderboard['params']['styleControl']is True, 'Adjustment changed; update chart labels before proceeding.'
arena=leaderboard['entries']
cutoff=leaderboard['voteCutoffISOString']
dom=html.fromstring((P/'arena.txt').read_text())
table_rows=dom.xpath('//table//tbody/tr')
assert len(table_rows)==len(arena)
for row,record in zip(table_rows,arena):
    assert record['modelDisplayName'] in ' '.join(row.xpath('./td')[2].xpath('.//text()'))
proof={
 'source_url':'https://arena.ai/leaderboard/chat/text',
 'source_file_sha256':hashlib.sha256((P/'arena.txt').read_bytes()).hexdigest(),
 'serialized_source_locator':'React server-flight component 3e[3].leaderboard',
 'adjustment_json_path':'3e[3].leaderboard.params.styleControl',
 'adjustment_exact_value':leaderboard['params']['styleControl'],
 'category_json_path':'3e[3].leaderboard.params.category',
 'category_exact_value':leaderboard['params']['category'],
 'leaderboard_id':leaderboard['id'],
 'vote_cutoff_json_path':'3e[3].leaderboard.voteCutoffISOString',
 'vote_cutoff_exact_value':cutoff,
 'score_json_path':'3e[3].leaderboard.entries[*].rating',
 'interval_lower_json_path':'3e[3].leaderboard.entries[*].ratingLower',
 'interval_upper_json_path':'3e[3].leaderboard.entries[*].ratingUpper',
 'interval_method':'Bootstrap model-strength intervals as labeled in visible source; confidence level not guessed.',
 'visible_table_check':'All 414 visible table rows match leaderboard.entries model names in order.',
 'provider_cohort_policy':'Top15, or all if fewer15, of source-listed provider variants. Includes older historical configurations; no claim to cover all available cloud models.',
}
(OUT/'data'/'arena-selection-provenance.json').write_text(json.dumps(proof,indent=2)+'\n')
models=list_after(aa,'initialModels')
AA_KEYS=['id','slug','name','shortName','suffix','release','releaseDate','deprecated','isReasoning','isOpenWeights','mitigationStatus','creator','intelligenceIndex','intelligenceIndexIsEstimated','analystAgent','analystAgentPassAt1','analystAgentPassAtK','automationBenchPartialScore','briefcaseElo','briefcaseBreakdown','critpt','gdpval','gdpvalBreakdown','gdpPdfAllPass','gpqa','hle','lcr','mmmuPro','omniscience','scicode','terminalBench40','frontierCode','terminalBenchScience','mlcrOverall']
pruned=[]
for r in models:
    x={k:r.get(k) for k in AA_KEYS}
    # Only required factual measurements; omit publisher website text and task content.
    if x['briefcaseBreakdown']:
        x['briefcaseBreakdown']={k:x['briefcaseBreakdown'].get(k) for k in ['elo','lower95ci','upper95ci']}
    x['creator']={k:r['creator'].get(k) for k in ['slug','name']}
    pruned.append(x)
(OUT/'data'/'artificial-analysis.json').write_text(json.dumps(pruned,indent=2)+'\n')
(OUT/'data'/'arena.json').write_text(json.dumps(arena,indent=2)+'\n')
shutil.copyfile(P/'livebench_csv.txt',OUT/'data'/'livebench-2026-06-25.csv')
sources={
 'aa':{'url':'https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index','publisher':'Artificial Analysis','version':'Intelligence Index v4.3.2','capture_date_utc':'2026-10-13','capture_date_et':'2026-10-12','source_file_sha256':hashlib.sha256((P/'aa.txt').read_bytes()).hexdigest(),'snapshot':'Captured Oct 13, 2026 UTC / Oct 12 ET; individual evaluation dates not supplied'},
 'arena':{'url':'https://arena.ai/leaderboard/chat/text','publisher':'Arena','version':'Text / overall / style control enabled','vote_cutoff_utc':cutoff,'capture_date_utc':'2026-10-13','capture_date_et':'2026-10-12','source_file_sha256':hashlib.sha256((P/'arena.txt').read_bytes()).hexdigest(),'snapshot':'Vote cutoff Oct 8, 2026 14:00 UTC; captured Oct 13 UTC'},
 'livebench':{'url':'https://livebench.ai/table_2026_06_25.csv','publisher':'LiveBench','version':'2026-06-25 task-score CSV','capture_date_utc':'2026-10-13','capture_date_et':'2026-10-12','source_file_sha256':hashlib.sha256((P/'livebench_csv.txt').read_bytes()).hexdigest(),'snapshot':'June 25, 2026 release; historical coverage, not October standings'},
}
(OUT/'data'/'sources.json').write_text(json.dumps(sources,indent=2)+'\n')
print('Extracted AA',len(pruned),'Arena',len(arena),'LiveBench',len(list(csv.DictReader((P/'livebench_csv.txt').open()))))
