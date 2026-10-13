"""Regenerate benchmark graphics from saved primary-source numerical records.
Requires Python 3, matplotlib, numpy. Does not fetch mutable live pages.
"""
from pathlib import Path
import json,csv,hashlib,textwrap,re,math,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

P=Path(__file__).parent
D=P/'data';CH=P/'charts';CH.mkdir(exist_ok=True)
AA=json.loads((D/'artificial-analysis.json').read_text())
ARENA=json.loads((D/'arena.json').read_text())
LB=list(csv.DictReader((D/'livebench-2026-06-25.csv').open()))
SOURCES=json.loads((D/'sources.json').read_text())
APPEND_ONLY='--append-only' in sys.argv
PREVIOUS={r['id']:r for r in json.loads((P/'manifest.json').read_text()).get('assets',[])} if APPEND_ONLY and (P/'manifest.json').exists() else {}
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','figure.facecolor':'#081422','axes.facecolor':'#081422','text.color':'#eaf2fa','axes.labelcolor':'#ccd8e6','xtick.color':'#ccd8e6','ytick.color':'#eaf2fa','font.size':12,'axes.edgecolor':'#53677d'})
COLORS={'Anthropic':'#e7ac8a','OpenAI':'#62dfca','Google':'#85a9ff','Meta':'#98c7ff','Alibaba':'#dfa2ff','Z AI':'#f4d274','Z.ai':'#f4d274','DeepSeek':'#71b7ff','SpaceXAI':'#e2e7ed','NVIDIA':'#b2de70','Nvidia':'#b2de70','Microsoft':'#84c8ea','Kimi':'#efa1cd','Moonshot':'#efa1cd'}
ASSETS=[];LEADERS=[]

def safe(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def name(r):return r.get('name') or r.get('modelDisplayName') or r.get('model')
def creator(r):
    if 'creator'in r:return r['creator']['name']
    if 'modelOrganization'in r:return r['modelOrganization']
    s=name(r).lower()
    for prefix,c in [('claude','Anthropic'),('gpt','OpenAI'),('o3','OpenAI'),('o4','OpenAI'),('gemini','Google'),('deepseek','DeepSeek'),('qwen','Alibaba'),('glm','Z.ai'),('grok','SpaceXAI'),('llama','Meta'),('mistral','Mistral'),('kimi','Moonshot'),('nemotron','NVIDIA')]:
        if s.startswith(prefix):return c
    return 'Other / verify developer'
def val(r,k):
    try:v=float(r.get(k));return v if math.isfinite(v) else None
    except (TypeError,ValueError):return None

def chosen(records,key,n=None):
    x=[r for r in records if val(r,key)is not None and not r.get('deprecated',False)]
    if key=='intelligenceIndex':x=[r for r in x if not r.get('intelligenceIndexIsEstimated',False)]
    x.sort(key=lambda r:(-val(r,key),name(r)))
    return x if n is None else x[:n]

def footer(fig,source,note,subsource=None):
    s=SOURCES[source];url=subsource or s['url']
    fig.text(.025,.077,'Source: '+url,fontsize=9.9,color='#a9c9e5')
    fig.text(.025,.054,s['version']+' | '+s['snapshot'],fontsize=9.7,color='#a9c9e5')
    fig.text(.025,.031,note,fontsize=9.4,color='#d8e3ed')
    fig.text(.025,.010,'Benchmark-listed configurations; cloud availability needs verification. Scores alone do not establish the best model for a task.',fontsize=9.1,color='#b7c3d2')

def save(fig,id,title,source,records,key,kind='benchmark-chart',note='',subsource=None):
    file=CH/(id+'.svg')
    if id not in PREVIOUS:fig.savefig(file,format='svg',facecolor=fig.get_facecolor())
    plt.close(fig)
    s=SOURCES[source]
    rec={'id':id,'title':title,'path':'charts/'+file.name,'kind':kind,'origin':'original-data-visualization','tags':['benchmark','source-cited',source,key,'cloud-availability-unverified'],'intended_use':'Accurate source-cited model comparison; pair with prompt/output evidence before making viewer recommendations.','source_url':subsource or s['url'],'data_source_url':s['url'],'capture_date_utc':s['capture_date_utc'],'source_version':s['version'],'source_snapshot':s['snapshot'],'license':'Original visualization; third-party benchmark facts attributed to their publisher. Upstream benchmark code/data licenses are separate.','attribution':'Visualization: AI Update Sources. Factual benchmark measurements: '+s['publisher']+'.','reuse_status':'original-visualization-with-third-party-factual-data-attribution','contains_actual_benchmark_results':True,'metric':key,'notes':note,'dimensions':{'width':round(fig.get_figwidth()*100),'height':round(fig.get_figheight()*100)},'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
    if id in PREVIOUS:
        assert hashlib.sha256(file.read_bytes()).hexdigest()==PREVIOUS[id]['sha256'], 'Existing asset hash changed unexpectedly.'
        rec=PREVIOUS[id]
    else:
        rec['displayed_model_count']=len(records) if records is not None else None
        rec['cohort_scope']='all named source-listed provider configurations, including historical variants' if id.endswith('-full-cohort') and source=='arena' else 'displayed source-listed configurations'
    ASSETS.append(rec)
    if records:
        LEADERS.append({'chart':id,'source':s['publisher'],'metric':key,'leader_configuration':name(records[0]),'creator':creator(records[0]),'value':val(records[0],key),'source_version':s['version'],'source_snapshot':s['snapshot'],'interpretation':'Highest point estimate in this displayed cohort; not proof of a universal or statistically significant winner.'})

def bar(id,title,records,key,source,n=20,mult=1,unit='Score',note='',ci=None,subsource=None,poster=False):
    rows=chosen(records,key,n)
    if len(rows)<2:raise ValueError(f'{id}: too few records')
    height=max(10.8,2.8+len(rows)*.35) if poster else 10.8
    width=24 if poster else 19.2
    fig,ax=plt.subplots(figsize=(width,height),dpi=100)
    fig.subplots_adjust(left=.42,right=.955,top=.835,bottom=.15 if not poster else .10)
    scores=np.array([val(r,key)*mult for r in rows]);y=np.arange(len(rows))
    labels=[]
    for i,r in enumerate(rows):
        label=name(r)
        if source=='arena' and r.get('releaseType')=='pre_release':label+=' [preliminary]'
        labels.append('\n'.join(textwrap.wrap(label,56 if poster else 47)))
    if key in ['rating','gdpval','briefcaseElo']:
        # Interval plots avoid implying that truncated Elo axes are bar lengths.
        ax.scatter(scores,y,c=[COLORS.get(creator(r),'#8eb6c9') for r in rows],s=76,zorder=3)
    else:
        ax.barh(y,scores,color=[COLORS.get(creator(r),'#8eb6c9') for r in rows],height=.64)
    if ci:
        bounds=[]
        for r in rows:
            if source=='arena':lo,hi=r['ratingLower'],r['ratingUpper']
            else:
                b=r.get(ci) or {};lo,hi=b.get('lower95ci'),b.get('upper95ci')
            bounds.append((lo,hi))
        valid=[i for i,(lo,hi) in enumerate(bounds) if lo is not None and hi is not None]
        if valid:ax.errorbar(scores[valid],y[valid],xerr=np.array([[scores[i]-bounds[i][0]*mult for i in valid],[bounds[i][1]*mult-scores[i] for i in valid]]),fmt='none',ecolor='#f5f9ff',capsize=3,elinewidth=1.15)
    ax.set_yticks(y);ax.set_yticklabels(labels,fontsize=10.7 if not poster else 11)
    ax.invert_yaxis();ax.set_xlabel(unit,fontsize=13,labelpad=12)
    left=min(0,float(scores.min())*1.15);right=max(float(scores.max())*1.16,1)
    if key in ['rating','gdpval','briefcaseElo']:
        spread=max(float(scores.max()-scores.min()),35)
        left=max(0,float(scores.min())-spread*.16-12)
        right=float(scores.max())+spread*.22+24
    ax.set_xlim(left,right);ax.axvline(0,color='#899bad',linewidth=.8)
    ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
    for spine in ['top','right','left']:ax.spines[spine].set_visible(False)
    for i,score in enumerate(scores):
        label=f'{score:.1f}' if key!='rating' else f'{score:.0f}'
        if unit.endswith('(%)'):label+='%'
        offset=(right-left)*.013
        label_x=score+offset
        if ci and bounds[i][1]is not None:label_x=bounds[i][1]*mult+offset
        ax.text(label_x,i,label,va='center',ha='left',fontsize=11.1,color='#edf5fd')
    fig.text(.025,.945,title,fontsize=25 if not poster else 28,weight='bold')
    fig.text(.025,.907,f'{len(rows)} displayed source-listed configurations • Exact names and reasoning settings retained',fontsize=13.4,color='#bdd4e9')
    fig.text(.025,.875,((('95% confidence intervals shown' if source=='aa' else 'Published bootstrap score intervals shown')+'; overlapping intervals caution against strict rankings.') if ci else 'Point estimates only; captured data does not supply uncertainty for this displayed metric.'),fontsize=11.5,color='#cad9e7')
    footer(fig,source,note,subsource)
    save(fig,id,title,source,rows,key,note=note,subsource=subsource)

def best_per_creator(records,key):
    seen=set();out=[]
    for r in chosen(records,key):
        c=creator(r)
        if c not in seen:seen.add(c);out.append(r)
    return out

COMPONENTS=[
 ('briefcaseElo','AA-Briefcase v1.1','Agentic knowledge-work Elo; supporting agent/tools apply.',1,'Elo score','briefcaseBreakdown','aa-briefcase'),
 ('gdpval','GDPval-AA v2.1','Agentic occupational-work Elo; supporting agent/tools apply.',1,'Elo score','gdpvalBreakdown','gdpval-aa'),
 ('automationBenchPartialScore','AutomationBench-AA','Mean objective completion score with guardrail penalties; supporting agent/tools apply.',100,'Score (%)',None,'automationbench-aa'),
 ('terminalBench40','Terminal-Bench 4.0','Terminal-agent task success; supporting agent/tools apply.',100,'Task success (%)',None,'terminalbench-4-0'),
 ('scicode','SciCode','Scientific coding score reported by Artificial Analysis.',100,'Score (%)',None,'scicode'),
 ('hle',"Humanity’s Last Exam",'AA implementation; source-listed configuration settings apply. Do not equate with differently configured HLE runs.',100,'Score (%)',None,'humanitys-last-exam'),
 ('gdpPdfAllPass','GDP.pdf','All-criteria task pass rate, not average criterion score.',100,'All-pass rate (%)',None,'gdp-pdf'),
 ('critpt','CritPt','Research-level physics evaluation score reported by Artificial Analysis.',100,'Score (%)',None,'critpt'),
 ('omniscience','AA-Omniscience','Signed knowledge/hallucination score; negative values are possible. This is not accuracy percentage.',1,'Signed score',None,'omniscience'),
 ('lcr','AA Long Context Reasoning','Long-document reasoning score reported by Artificial Analysis.',100,'Score (%)',None,'artificial-analysis-long-context-reasoning'),
]

bar('aa-index-top20','Artificial Analysis Intelligence Index | top 20',AA,'intelligenceIndex','aa',note='Composite Index v4.3.2; estimated scores excluded. Configurations may include documented fallback behavior.')
bar('aa-index-full-cohort','Artificial Analysis Intelligence Index | complete captured cohort',AA,'intelligenceIndex','aa',n=None,poster=True,note='Complete 32-row captured initialModels cohort, not every model Artificial Analysis has ever evaluated; estimates excluded.')
bar('aa-index-best-listed-per-provider','AA Index | strongest evaluated setting per developer',best_per_creator(AA,'intelligenceIndex'),'intelligenceIndex','aa',n=None,note='One highest point estimate per developer in the captured cohort. Different reasoning/fallback settings are preserved.')
for key,title,note,mult,unit,ci,slug in COMPONENTS:
    bar('aa-'+safe(key)+'-top15',title+' | top 15',AA,key,'aa',n=15,mult=mult,unit=unit,note=note,ci=ci,subsource='https://artificialanalysis.ai/evaluations/'+slug)

for c in ['OpenAI','Anthropic','Google','Alibaba','Meta','Z AI']:
    bar('aa-index-'+safe(c),'AA Index | '+c+' source-listed variants',[r for r in AA if creator(r)==c],'intelligenceIndex','aa',n=None,note='Within-developer captured cohort; exact reasoning/fallback settings retained; no assertion that every available model is included.')

def matrix(company):
    keys=['automationBenchPartialScore','terminalBench40','scicode','hle','gdpPdfAllPass','critpt','lcr']
    titles=['Automation\nBench-AA','Terminal\nBench 4.0','SciCode','HLE','GDP.pdf\nall-pass','CritPt','Long-context\nreasoning']
    rows=chosen([r for r in AA if creator(r)==company],'intelligenceIndex')
    values=np.array([[val(r,k)*100 if val(r,k)is not None else np.nan for k in keys] for r in rows])
    fig,ax=plt.subplots(figsize=(19.2,10.8),dpi=100);fig.subplots_adjust(left=.34,right=.97,top=.77,bottom=.20)
    cmap=plt.get_cmap('YlGnBu').copy();cmap.set_bad('#27384a')
    ax.imshow(values,vmin=0,vmax=100,cmap=cmap,aspect='auto');ax.set_xticks(np.arange(len(keys)));ax.set_xticklabels(titles,fontsize=11);ax.set_yticks(np.arange(len(rows)));ax.set_yticklabels(['\n'.join(textwrap.wrap(name(r),44)) for r in rows],fontsize=11)
    for i in range(len(rows)):
        for j in range(len(keys)):
            v=values[i,j];ax.text(j,i,'N/A'if np.isnan(v)else f'{v:.1f}%',ha='center',va='center',fontsize=12,color='#edf6ff'if np.isnan(v)or v>60 else '#071b2b')
    title=company+' | capability profile across AA evaluations'
    fig.text(.025,.945,title,fontsize=25,weight='bold');fig.text(.025,.904,'Different evaluations share percentage units; they are separate tasks, not interchangeable measures.',fontsize=13,color='#c9daeb')
    footer(fig,'aa','Each cell is its own published metric. No average or synthetic combined score is calculated; N/A means missing source data.')
    save(fig,'aa-capability-profile-'+safe(company),title,'aa',None,'separate-component-metrics',note='Independent percentage metrics displayed separately, never aggregated.')
matrix('OpenAI');matrix('Anthropic')

EXTRA=[('frontierCode','FrontierCode 1.1','Agentic repository coding score; supporting agent/tools apply.','frontiercode'),('terminalBenchScience','Terminal-Bench-Science 0.1','Research-workflow task score; supporting agent/tools apply.','terminal-bench-science'),('gpqa','GPQA Diamond','AA scientific reasoning evaluation; listed configurations with data only.','gpqa-diamond'),('mmmuPro','MMMU-Pro','AA multimodal reasoning evaluation; listed configurations with data only.','mmmu-pro'),('mlcrOverall','Medical Long Context Reasoning (MLCR-AA)','Medical-document reasoning score; source-listed configurations only. This benchmark is not clinical-use validation.','mlcr-aa')]
for key,title,note,slug in EXTRA:
    bar('aa-'+safe(key)+'-top15',title+' | top 15',AA,key,'aa',n=15,mult=100,unit='Score (%)',note=note,subsource='https://artificialanalysis.ai/evaluations/'+slug)

# Unknown-organization entries are not guessed or assigned to providers.
named=[r for r in ARENA if r.get('modelOrganization') and r.get('modelDisplayName')]
bar('arena-text-top20','Arena Text | overall preference top 20',named,'rating','arena',ci='arena',note='Style control enabled. Whiskers are source bootstrap score intervals; preliminary entries labeled. Preference is not factual accuracy.')
bar('arena-text-named-provider-poster','Arena Text | complete named-provider cohort',named,'rating','arena',n=None,ci='arena',poster=True,note='Unknown-organization entries excluded, not private/local deployment recommendations. Many source-listed entries are older configurations.')
bar('arena-text-best-listed-per-provider','Arena Text | strongest listed setting per provider',best_per_creator(named,'rating'),'rating','arena',n=None,ci='arena',note='One highest point estimate per named provider; includes older and preliminary configurations. Overlapping intervals are not strict winners.')
for c in ['OpenAI','Anthropic','Google','Meta','DeepSeek','Alibaba','Z.ai','SpaceXAI','Microsoft','Nvidia']:
    shown='xAI / SpaceXAI' if c=='SpaceXAI' else c
    bar('arena-text-'+safe(c),shown+' | Arena Text source-listed variants',[r for r in named if creator(r)==c],'rating','arena',n=15,ci='arena',note='Top 15 or all available source-listed provider rows. Exact configuration names retained; older variants are historical comparisons.')

for c in ['OpenAI','Anthropic','Google','Meta','DeepSeek','Alibaba','Z.ai','SpaceXAI','Microsoft','Nvidia']:
    rows=[r for r in named if creator(r)==c]
    if len(rows)<2:continue
    shown='xAI / SpaceXAI' if c=='SpaceXAI' else c
    bar('arena-text-'+safe(c)+'-full-cohort',shown+' | all source-listed configurations (including historical)',rows,'rating','arena',n=None,ci='arena',poster=True,note='Full captured provider cohort, including historical variants. No claim that every model is currently cloud-available; exact settings retained.')

for key,title in [('python','Python coding'),('summarize','Summarization'),('code_generation','Code generation')]:
    bar('livebench-2026-06-25-'+safe(key),'LiveBench | '+title+' | June 25 release',LB,key,'livebench',n=15,unit='Task score (0–100)',note='Historical June 25, 2026 subtask scores. Not overall/category averages and not current October leaders. Names/settings retained.')

(P/'manifest.json').write_text(json.dumps({'assets':ASSETS},indent=2)+'\n')
(P/'leader_summary.json').write_text(json.dumps({'note':'Point-estimate leaders within displayed cohorts only. Distinct benchmark scales are never merged. Cloud availability requires verification.','leaders':LEADERS},indent=2)+'\n')
counts={'charts':len(ASSETS),'aa_captured_model_variants':len(AA),'arena_source_rows':len(ARENA),'arena_named_provider_rows':len(named),'livebench_source_rows':len(LB),'distinct_chart_file_hashes':len({a['sha256']for a in ASSETS})}
(P/'verification.json').write_text(json.dumps(counts,indent=2)+'\n')
print(json.dumps(counts,indent=2))
