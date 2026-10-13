#!/usr/bin/env python3
"""Generate original, editable evidence-first AI-show SVG production templates.
No live data or third-party marks are embedded. CC BY 4.0; AI Update Sources.
"""
from pathlib import Path
import json, re, textwrap, hashlib, xml.etree.ElementTree as ET
from html import escape
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'assets'
NAVY='#081421'; CARD='#112637'; CYAN='#63dcec'; GOLD='#efc26d'; WHITE='#f4f8fc'; MUTED='#abc0cf'; LINE='#294456'; RED='#ff9d9d'
records=[]
from custom_scenes import distinct_benchmark, distinct_verdict, distinct_change, distinct_feature

def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
class SVG:
 def __init__(self,title,cat,subtitle='Replace all placeholders with verified episode evidence.'):
  self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080" role="img" aria-labelledby="asset-title asset-description">',f'<title id="asset-title">{escape(title)}</title>',f'<desc id="asset-description">Original editable template for {escape(cat)}. All displayed results, models, costs, and evidence fields are placeholders requiring verification. Not a factual comparison.</desc>', '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#63dcec"/></marker></defs>']
  self.rect(0,0,1920,1080,NAVY,r=0)
  self.line(70,70,1850,70,LINE,2)
  self.txt(70,57,'AI UPDATE / '+cat.upper(),20,CYAN,weight='700')
  self.txt(70,147,title,54,WHITE,weight='700')
  self.txt(73,194,subtitle,24,MUTED)
  self.chip(1555,23,295,'TEMPLATE • VERIFY DATA',GOLD,18)
  self.line(70,1018,1850,1018,LINE,2)
  self.txt(70,1051,'TEMPLATE / no measured results embedded',20,GOLD)
  self.txt(1270,1051,'CC BY 4.0 • AI Update Sources',20,MUTED)
 def rect(self,x,y,w,h,fill=CARD,stroke=None,sw=1,r=16,opacity=None):
  self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+(f' opacity="{opacity}"' if opacity is not None else '')+'/>')
 def line(self,x1,y1,x2,y2,color=LINE,sw=2,dash=None,arrow=False):
  self.s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
 def path(self,d,fill='none',stroke=CYAN,sw=3): self.s.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
 def circle(self,x,y,r,fill=CARD,stroke=None,sw=2): self.s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')
 def txt(self,x,y,t,size=27,color=WHITE,weight='400',anchor=None):
  self.s.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="DejaVu Sans, Arial, sans-serif" font-size="{size}" font-weight="{weight}"'+(f' text-anchor="{anchor}"' if anchor else '')+'>'+escape(str(t))+'</text>')
 def para(self,x,y,t,width,size=27,color=MUTED,lh=None,weight='400'):
  # Character budget conservative for proportional sans; explicit paragraphs retained.
  lh=lh or size*1.40; budget=max(8,int(width/(size*.60))); offset=0
  for p in t.split('\n'):
   lines=textwrap.wrap(p,budget,break_long_words=False,break_on_hyphens=False) or ['']
   for l in lines: self.txt(x,y+offset,l,size,color,weight); offset+=lh
  return offset
 def chip(self,x,y,w,t,color=CYAN,size=20):
  self.rect(x,y,w,42,NAVY,color,1,9);self.txt(x+14,y+28,t,size,color,weight='700')
 def panel(self,x,y,w,h,label,body='',accent=CYAN,size=27):
  self.rect(x,y,w,h,CARD,LINE,1,16);self.rect(x,y,6,h,accent,r=2)
  self.para(x+26,y+42,label,w-50,23,accent,lh=30,weight='700')
  if body:self.para(x+26,y+88,body,w-52,size,WHITE)
 def bullets(self,x,y,w,items,size=26,gap=76,color=WHITE):
  for i,t in enumerate(items):
   self.circle(x+7,y+i*gap-8,4,CYAN);self.para(x+26,y+i*gap,t,w-30,size,color)
 def arrow(self,x1,y1,x2,y2,label=None):
  self.line(x1,y1,x2,y2,CYAN,3,arrow=True)
  if label:self.txt((x1+x2)/2,(y1+y2)/2-16,label,20,MUTED,anchor='middle')
 def image_slot(self,x,y,w,h,label='REAL SOURCE SCREENSHOT'):
  self.rect(x,y,w,h,NAVY,LINE,2,12);self.line(x+15,y+15,x+w-15,y+h-15,LINE,1,dash='8 9');self.line(x+w-15,y+15,x+15,y+h-15,LINE,1,dash='8 9')
  self.rect(x+20,y+h/2-35,w-40,76,CARD,r=10);self.para(x+36,y+h/2-5,label,w-72,24,WHITE,weight='700')
 def note(self,x,y,w,t):self.rect(x,y,w,58,NAVY,GOLD,1,10);self.para(x+18,y+36,t,w-35,21,GOLD,lh=27)
 def table(self,x,y,w,cols,rows,widths=None,row_h=78):
  widths=widths or [w/len(cols)]*len(cols)
  self.rect(x,y,w,row_h,CARD,LINE,r=8)
  for j,c in enumerate(cols):self.para(x+sum(widths[:j])+18,y+33,c,widths[j]-36,21,CYAN,lh=27,weight='700')
  for i,row in enumerate(rows):
   yy=y+(i+1)*row_h;self.rect(x,yy,w,row_h-2,NAVY,LINE,r=3)
   for j,c in enumerate(row):self.para(x+sum(widths[:j])+18,yy+32,c,widths[j]-36,23,WHITE,lh=29)
  for boundary in range(1,len(cols)):
   divider_x=x+sum(widths[:boundary]);self.line(divider_x,y+7,divider_x,y+row_h*(len(rows)+1)-7,LINE,1)
 def end(self):return '\n'.join(self.s+['</svg>'])

def prompt(s,y=235,h=112,text='Paste the identical prompt, attached inputs, and task constraints here.'):
 s.panel(70,y,1780,h,'IDENTICAL PROMPT / EXACT INPUTS',text,GOLD,25)

def model(s,x,y,w,h,name='MODEL A',output=True):
 s.panel(x,y,w,h,name+' / EXACT VERSION','',CYAN)
 if output:
  s.txt(x+26,y+92,'ACTUAL OUTPUT EXCERPT',24,WHITE,weight='700')
  s.para(x+26,y+132,'Paste the unedited response. Preserve errors and omissions; link the full output.',w-52,25,MUTED)
 s.line(x+25,y+h-115,x+w-25,y+h-115,LINE)
 s.txt(x+26,y+h-76,'TASK COST / verified billed usage',22,GOLD)
 s.txt(x+26,y+h-35,'BENCHMARK / version • score • source',21,CYAN)

def compact_model(s,x,y,w,h,name,fields):
 s.panel(x,y,w,h,name+' / EXACT VERSION','',CYAN)
 s.bullets(x+27,y+91,w-54,fields,24,gap=max(60,(h-98)/len(fields)))

def save(s,cat,title,usage,tags):
 i=len(records)+1;id=f'cmp-{i:03d}-{slug(title)}';p=OUT/(id+'.svg');p.write_text(s.end(),encoding='utf-8')
 ET.fromstring(p.read_text())
 records.append({'id':id,'title':title,'path':'assets/'+p.name,'category':cat,'tags':['cloud-ai','evidence-first','editable-svg',cat]+tags,'dimensions':{'width':1920,'height':1080},'intended_use':usage,'kind':'template','origin':'original','license':'CC-BY-4.0','recommended_attribution':'AI Update Sources','creator':'AI Update Sources','source_url':None,'placeholder_notice':'Template only. Replace fields with verified evidence; no benchmark values or model outputs included.','sha256':hashlib.sha256(p.read_bytes()).hexdigest()})

# 30 practical comparison layouts. Each includes the central five-part evidence relation.
comparisons=[
('Evidence duel','A direct two-model comparison with one shared prompt and vertically aligned output, cost, and benchmark fields.'),
('Three-service comparison','Compare three cloud services on one task without collapsing subscription and API costs.'),
('Prompt beside paired outputs','Keep a long exact prompt readable beside two output excerpts and shared evidence notes.'),
('Output difference microscope','Zoom into a consequential difference while retaining both models, prices, and benchmark context.'),
('Five-field comparison ledger','A compact audit table aligning prompt, product, exact model, task cost, and benchmarks.'),
('Expected result and actual products','Compare actual output with a predeclared expected result and success criteria.'),
('Source image and model response','Place a real benchmark screenshot beside an actual response and model billing metadata.'),
('Document analysis duel','Compare two models against a shared cloud document task and marked evidence passages.'),
('Code repair duel','Compare actual patches, executed checks, cost, and relevant software benchmark context.'),
('Research citation duel','Compare cited answers with source verification and benchmark relevance.'),
('Chart interpretation duel','Compare chart interpretations using the same uploaded chart and explicitly verified findings.'),
('Long-context task comparison','Show exact document inputs, retrieval requirements, actual responses, and context-evaluation limits.'),
('Structured-output comparison','Compare response schemas, actual JSON, validation outcomes, costs, and instruction-following evidence.'),
('Tool-use trace comparison','Compare observable tool traces and final products; distinguish model from the full system.'),
('Writing constraint comparison','Compare writing outputs against identical tone, length, and factual constraints.'),
('First pass and retry comparison','Expose failed attempts and accumulated costs rather than selecting only the successful response.'),
('Cloud app and API comparison','Compare app and API environments with shared input and clearly different pricing bases.'),
('Reasoning setting comparison','Show how explicitly recorded reasoning settings affect observed products and billed task cost.'),
('Search disabled and enabled','Separate base-model response from search-augmented output on one cloud platform.'),
('Multimodal input comparison','Compare products from identical text and visual inputs, preserving image preprocessing details.'),
('Translation comparison','Compare translation outputs against meaning, terminology, and preservation requirements.'),
('Instruction compliance comparison','Make each prompt requirement visible next to observable compliance and actual model responses.'),
('Latency and product comparison','Show actual response time with quality, benchmark context, and the same cost basis.'),
('Cloud availability comparison','Make region, access tier, and provider restrictions explicit beside products and costs.'),
('Accessible product comparison','Compare task output accessibility and formatting with underlying capability evidence.'),
('Safe response comparison','Compare refusals and useful safe alternatives without making an overall safety claim.'),
('Context handling comparison','Compare how services handle the same document near their supported input limits.'),
('Batch product comparison','Compare a batch task with per-item outcomes, total billing, and relevance-limited benchmark evidence.'),
('Claim and evidence comparison','Connect every output claim to source verification while retaining model/cost/benchmark identity.'),
('Readable comparison summary','A spacious short-output comparison suitable for small-screen viewing and screenshot recall.')]
for k,(title,usage) in enumerate(comparisons):
 s=SVG(title,'comparison')
 if k==0:
  prompt(s);model(s,70,375,875,560);model(s,975,375,875,560,'MODEL B');s.note(70,952,1780,'Explain the practical difference; a benchmark score does not establish the quality of this single output.')
 elif k==1:
  prompt(s)
  for j in range(3):compact_model(s,70+j*600,375,580,560,f'MODEL {chr(65+j)}',['Actual product excerpt','Task cost / billing basis','Benchmark / version / source','Task success / rubric evidence'])
  s.note(70,952,1780,'Use equivalent task conditions. Label differences in tools, platform defaults, and access tiers.')
 elif k==2:
  s.panel(70,235,480,615,'IDENTICAL PROMPT','Exact prompt and shared inputs\n\nTask constraints\n\nPredeclared success criteria',GOLD)
  model(s,580,235,620,615);model(s,1230,235,620,615,'MODEL B');s.panel(70,875,1780,123,'EVALUATION NOTES','Observed differences, sample size, caveats, and links to full products.',GOLD,25)
 elif k==3:
  prompt(s)
  s.image_slot(70,375,1030,365,'ACTUAL OUTPUT / MARKED EXCERPT');s.panel(1130,375,720,365,'CONSEQUENTIAL DIFFERENCE','Verified error or benefit\nWhy the viewer should care\nPredeclared rubric result',GOLD)
  model(s,70,770,875,230,output=False);model(s,975,770,875,230,'MODEL B',output=False)
 elif k==4:
  s.table(70,235,1780,['EVIDENCE FIELD','MODEL A / exact version','MODEL B / exact version'],[['Identical prompt','Exact shared input','Exact shared input'],['Actual product','Unedited excerpt + full output','Unedited excerpt + full output'],['Task cost','Billed usage + rate date','Billed usage + rate date'],['Benchmark','Metric / version / source','Metric / version / source'],['Task verdict','Observed rubric outcome','Observed rubric outcome']],widths=[360,710,710],row_h=108)
  s.note(70,921,1780,'This table connects five evidence fields; it does not turn an illustrative task into a universal model ranking.')
 elif k==5:
  prompt(s,235,112)
  s.panel(70,375,1780,125,'EXPECTED RESULT / DECLARED BEFORE TESTING','List objective checks and the minimum acceptable result.',GOLD)
  model(s,70,530,875,465);model(s,975,530,875,465,'MODEL B')
 elif k==6:
  s.image_slot(70,235,800,475,'REAL BENCHMARK IMAGE / SOURCE');s.panel(70,737,800,258,'BENCHMARK INTERPRETATION','What it measures\nWhat it does not establish\nEvaluation comparability',GOLD)
  s.panel(900,235,950,125,'EXACT PROMPT','Shared inputs and constraints',GOLD);model(s,900,390,950,605)
 elif k==7:
  prompt(s)
  for j,name in enumerate(['MODEL A','MODEL B']):
   x=70+j*905;s.panel(x,375,875,620,name+' / EXACT VERSION','',CYAN);s.image_slot(x+25,450,300,330,'SOURCE PASSAGE');s.panel(x+355,450,495,330,'ACTUAL RESPONSE','Quote finding\nQuote supporting evidence\nIdentify an omission',GOLD,24);s.txt(x+25,870,'TASK COST / billed tokens + tools',22,GOLD);s.txt(x+25,920,'BENCHMARK / long-document metric + source',21,CYAN)
 elif k==8:
  prompt(s)
  for j,name in enumerate(['MODEL A','MODEL B']):
   x=70+j*905;s.panel(x,375,875,620,name+' / EXACT VERSION','',CYAN);s.panel(x+25,450,825,275,'ACTUAL PATCH','Paste the unedited code excerpt. Use a monospace image from the actual output when appropriate.',GOLD,26);s.chip(x+25,750,340,'EXECUTED CHECKS / EVIDENCE');s.txt(x+25,852,'TASK COST / include retries and tools',22,GOLD);s.txt(x+25,919,'BENCHMARK / same system setup?',22,CYAN)
 elif k==9:
  prompt(s)
  for j,name in enumerate(['MODEL A','MODEL B']):
   x=70+j*905;model(s,x,375,875,470,name);s.panel(x,870,875,125,'CITATION VERIFICATION','Source exists / supports claim / date checked',GOLD,23)
 elif k==10:
  s.image_slot(70,235,640,450,'IDENTICAL INPUT CHART');s.panel(70,710,640,285,'EXACT PROMPT','Question, requested units, assumptions, and output format.',GOLD)
  model(s,740,235,540,760);model(s,1310,235,540,760,'MODEL B')
 elif k==11:
  s.panel(70,235,1780,135,'EXACT PROMPT + SHARED DOCUMENT SET','Document IDs, lengths, requested findings, and evidence requirements.',GOLD)
  for j,label in enumerate(['INPUT DOCUMENTS','REQUIRED EVIDENCE','OBSERVED PRODUCTS']):s.panel(70+j*600,400,580,180,label,'Exact materials\nRecorded requirements' if j<2 else 'Unedited outputs',CYAN,24)
  s.arrow(650,490,665,490);s.arrow(1250,490,1265,490);model(s,70,610,875,385);model(s,975,610,875,385,'MODEL B')
 elif k==12:
  s.panel(70,235,550,760,'EXACT PROMPT + SCHEMA','Required keys\nAllowed types\nValidation rules\nShared input\n\nDo not repair the output silently.',GOLD)
  for j,name in enumerate(['MODEL A','MODEL B']):
   x=650+j*610;model(s,x,235,590,550,name);s.panel(x,815,590,180,'VALIDATION RESULT','Recorded validator output\nCost includes failed attempts',GOLD,24)
 elif k==13:
  prompt(s)
  for j,name in enumerate(['MODEL A','MODEL B']):
   y=375+j*310;s.panel(70,y,1780,290,name+' / EXACT VERSION / RECORDED AGENT SETUP','',CYAN)
   for z,t in enumerate(['Actual tool call','Observed response','Final product']):s.panel(95+z*490,y+77,460,128,t,'Paste trace evidence',GOLD,22)
   s.arrow(555,y+145,574,y+145);s.arrow(1045,y+145,1064,y+145);s.txt(1580,y+117,'TASK COST',20,GOLD);s.txt(1580,y+166,'BENCHMARK',20,CYAN);s.txt(95,y+260,'Record attempts, tool availability, and evaluator checks.',22,MUTED)
 elif k==14:
  prompt(s)
  s.panel(70,375,360,620,'RUBRIC','Meaning preserved\nTone matched\nLength respected\nFacts supported\nInstructions followed',GOLD,24)
  model(s,460,375,680,620);model(s,1170,375,680,620,'MODEL B')
 elif k==15:
  prompt(s)
  s.panel(70,375,500,620,'ATTEMPT RECORD','Exact prompt\nFirst output\nFailure reason\nRetry prompt\nFinal output\nAll billed usage',GOLD,26)
  model(s,600,375,610,620,'MODEL A / FIRST PASS');model(s,1240,375,610,620,'MODEL B / RETRY POLICY')
 elif k==16:
  prompt(s)
  s.panel(70,375,875,160,'CLOUD APP ENVIRONMENT','Plan, tools, routing, region, and access date.',GOLD);s.panel(975,375,875,160,'API ENVIRONMENT','Exact endpoint, version, settings, and tool setup.',GOLD)
  model(s,70,565,875,430,'APP / MODEL IDENTITY');model(s,975,565,875,430,'API / EXACT MODEL')
 elif k==17:
  prompt(s)
  for j,label in enumerate(['RECORDED SETTING A','RECORDED SETTING B','RECORDED SETTING C']):
   x=70+j*600;model(s,x,375,580,510,label);s.note(x,910,580,'Record the exact reasoning budget.')
 elif k==18:
  prompt(s)
  for j,label in enumerate(['SEARCH OFF','SEARCH ON']):
   x=70+j*905;model(s,x,375,875,500,'SAME MODEL / '+label);s.panel(x,900,875,95,'ENVIRONMENT NOTE','Record access to external sources and tool charges.',GOLD,22)
 elif k==19:
  s.image_slot(70,235,510,310,'IDENTICAL VISUAL INPUT');s.panel(70,575,510,420,'EXACT TEXT PROMPT','Shared image\nResolution and preprocessing\nRequested analysis\nEvidence checks',GOLD)
  model(s,610,235,605,760);model(s,1245,235,605,760,'MODEL B')
 elif k==20:
  s.panel(70,235,1780,180,'SOURCE TEXT + EXACT TRANSLATION INSTRUCTIONS','Original text / target language / terminology rules / preservation requirements.',GOLD,28)
  model(s,70,445,875,550);model(s,975,445,875,550,'MODEL B')
 elif k==21:
  prompt(s)
  s.table(70,375,650,['PROMPT REQUIREMENT','CHECK'],[['Constraint one','Recorded'],['Constraint two','Recorded'],['Constraint three','Recorded'],['Constraint four','Recorded']],widths=[440,210],row_h=94)
  model(s,750,375,535,620);model(s,1315,375,535,620,'MODEL B')
 elif k==22:
  prompt(s)
  model(s,70,375,875,480);model(s,975,375,875,480,'MODEL B')
  s.panel(70,885,875,110,'MEASURED TIME','First token + full completion / test conditions',GOLD,24);s.panel(975,885,875,110,'MEASURED TIME','First token + full completion / test conditions',GOLD,24)
 elif k==23:
  prompt(s)
  for j,name in enumerate(['MODEL A','MODEL B']):
   x=70+j*905;s.panel(x,375,875,125,'ACCESS CONDITIONS','Provider / region / plan / observation date',GOLD,25);model(s,x,530,875,465,name)
 elif k==24:
  prompt(s)
  model(s,70,375,700,620);s.panel(800,375,320,620,'PRODUCT CHECKS','Readable\nStructured\nNavigable\nPlain language\nAlt text checked',GOLD,24);model(s,1150,375,700,620,'MODEL B')
 elif k==25:
  prompt(s,text='Paste the same policy-relevant prompt; protect private or harmful details where needed.')
  for j,name in enumerate(['MODEL A','MODEL B']):
   x=70+j*905;model(s,x,375,875,465,name);s.panel(x,870,875,125,'OBSERVED BEHAVIOR','Refusal / safe alternative / scope limitation',GOLD,24)
 elif k==26:
  s.panel(70,235,1780,125,'EXACT PROMPT + INPUT LENGTH','Record identical input, requested evidence, and truncation behavior.',GOLD,25)
  s.panel(70,390,1780,150,'CONTEXT PROCESSING RECORD','Accepted input / rejected input / preprocessing / hidden truncation known or unknown',CYAN,26)
  model(s,70,570,875,425);model(s,975,570,875,425,'MODEL B')
 elif k==27:
  s.panel(70,235,1780,125,'EXACT BATCH PROMPT + ITEM SET','Shared dataset hash / per-item instructions / total task requirements',GOLD,25)
  for j,name in enumerate(['MODEL A','MODEL B']):
   x=70+j*905;model(s,x,390,875,440,name);s.panel(x,860,875,135,'BATCH OUTCOME RECORD','Per-item checks / total billed usage / failures',GOLD,24)
 elif k==28:
  prompt(s)
  model(s,70,375,570,620);s.table(670,375,580,['OUTPUT CLAIM','SOURCE CHECK'],[['Claim excerpt','Supported?'],['Claim excerpt','Supported?'],['Claim excerpt','Supported?']],widths=[290,290],row_h=110);model(s,1280,375,570,620,'MODEL B')
 else:
  s.panel(70,235,1780,160,'IDENTICAL PROMPT','Exact short prompt + task success requirement',GOLD,32)
  for j,name in enumerate(['MODEL A','MODEL B']):
   x=70+j*905;s.panel(x,425,875,570,name+' / EXACT VERSION','Actual short output\n\nTask cost / verified usage\n\nBenchmark / cited relevant score',CYAN,32)
 save(s,'comparison',title,usage,['prompt','product','model','cost','benchmark'])

# 30 benchmark explanation compositions, with explicit scope and no invented scores.
benchmarks=[
('Benchmark scope triptych','Explain what a benchmark measures, what it excludes, and a practical implication.'),
('Accuracy evidence anatomy','Explain numerator, denominator, task set, and evaluation rules without displaying fabricated accuracy.'),
('Benchmark version compatibility','Audit whether scores from different benchmark versions can be compared.'),
('Model versus evaluated system','Separate core model, tools, agent loop, and evaluator in reported results.'),
('Confidence interval explainer','Teach confidence bounds and ties using a schematic, not a numeric result.'),
('Contamination exposure map','Map how benchmark items can enter training or tuning data.'),
('Known limitations register','Display reported benchmark limitations, mitigation, and remaining uncertainty.'),
('Reasoning budget audit','Record computation and attempt budgets before comparing reasoning scores.'),
('Sample coverage audit','Explain tested samples, excluded samples, and task coverage.'),
('Metric direction explainer','Make metric units and better-direction explicit before ranking.'),
('Mathematical reasoning scope','Separate answer correctness from derivation quality and reproducibility.'),
('Coding evaluation spectrum','Distinguish code generation, test passing, and repository issue resolution.'),
('Tool-use success layers','Distinguish valid tool syntax from argument correctness and completed task.'),
('Long-context capability layers','Separate token acceptance, evidence retrieval, and synthesis.'),
('Human preference scope','Distinguish preference judgments from factual correctness and utility.'),
('Vision evaluation anatomy','Explain perception, grounding, reasoning, and input conditions.'),
('Benchmark relevance decision tree','Select evidence appropriate to the viewer task.'),
('Three evidence origins','Separate company-reported, independent, and original-show evaluation evidence.'),
('Single attempt and pass at k','Explain how allowing multiple attempts changes what a score means.'),
('Single output and selected output','Explain selection/reranking effects and the additional computation required.'),
('Frozen and refreshed test sets','Explain static versus refreshed evaluation sets and dates.'),
('Ranking uncertainty and ties','Show how ranking uncertainty limits claims of a unique winner.'),
('Benchmark saturation warning','Explain why an easy saturated benchmark may no longer distinguish models.'),
('Evaluation timeline integrity','Record model release, evaluation run, benchmark release, and publication dates.'),
('Prompt setup comparability','Audit system prompts, tools, inference settings, and evaluation harness.'),
('Overlapping uncertainty bands','Communicate that overlapping uncertainty is not proof of equivalence.'),
('Failure taxonomy explainer','Explain how error categories reveal practical weaknesses hidden by an aggregate score.'),
('Metric units reference','Separate percentages, preference scores, latency, and costs.'),
('Aggregate weighting audit','Reveal category weighting and avoid unsupported overall rankings.'),
('Task coverage matrix','Show capability coverage and evidence gaps for the tasks viewers care about.')]
for k,(title,usage) in enumerate(benchmarks):
 s=SVG(title,'benchmark explainer','Use a verified benchmark release and cited methodology; diagrams are explanatory templates.')
 if k==0:
  for j,(lab,bod) in enumerate([('MEASURES','Task family\nEvaluation metric\nAllowed resources'),('DOES NOT MEASURE','Uncovered abilities\nReal-world limits\nUnknown reliability'),('VIEWER IMPLICATION','Relevant use case\nPractical caveat\nNext task to test')]):s.panel(70+j*600,235,580,625,lab,bod,CYAN if j!=1 else GOLD,30)
  s.panel(70,890,1780,105,'CITATION','Benchmark / release / methodology URL / evaluation date',GOLD,23)
 elif k==1:
  s.panel(70,235,800,235,'SCORE DEFINITION','Correct outcomes ÷ evaluated outcomes\nRecord exact denominator and exclusions.',GOLD,30)
  s.panel(900,235,950,235,'EVALUATION RULES','Answer matching / evaluator / allowed tools / attempt policy',CYAN,29)
  for j,label in enumerate(['TASK SET','MEASURED OUTCOME','REPORTED METRIC']):s.panel(70+j*600,500,580,350,label,'Verified release\nDocumented evaluation\nSource-linked result',CYAN,29)
  s.note(70,885,1780,'A higher aggregate score does not guarantee success on an individual viewer task.')
 elif k==2:
  s.table(70,235,1780,['COMPATIBILITY FIELD','SCORE A','SCORE B'],[['Benchmark release','Record version','Record version'],['Task subset','Record subset','Record subset'],['Metric and units','Record metric','Record metric'],['Evaluation setup','Record setup','Record setup'],['Comparable?','Document decision','Document caveat']],widths=[490,645,645],row_h=106)
  s.note(70,922,1780,'If versions or rules differ materially, show separate results rather than a combined ranking.')
 elif k==3:
  for j,(lab,bod) in enumerate([('CORE MODEL','Exact model ID\nWeights / version'),('EXECUTION SYSTEM','Agent loop\nSearch and tools'),('EVALUATION','Harness / tests\nAttempt budget')]):s.panel(70+j*600,235,580,290,lab,bod,CYAN,30)
  s.arrow(650,380,665,380);s.arrow(1250,380,1265,380)
  s.panel(70,560,1780,300,'WHAT THE SCORE ACTUALLY DESCRIBES','State whether the result evaluates a model alone or an entire configured system. Preserve setup details alongside the score.',GOLD,35)
  s.note(70,895,1780,'Do not attribute agent, tool, or retry improvements solely to the underlying model.')
 elif k in (4,25):
  s.panel(70,235,530,620,'INTERPRETATION','Reported uncertainty\nSample size\nEstimator or method\n\nNo clear difference is not proven equivalence.',GOLD,27)
  s.rect(630,235,1220,620,CARD,LINE);s.txt(665,295,'SCHEMATIC ONLY / SUBSTITUTE ACTUAL INTERVALS',23,CYAN,weight='700')
  for j,label in enumerate(['MODEL A','MODEL B']):
   y=435+j*210;s.txt(665,y-55,label+' / exact version',26,WHITE);s.line(950,y,1720,y,LINE,2);s.line(1130+(j*60),y,1500+(j*100),y,CYAN if j==0 else GOLD,10);s.circle(1300+j*90,y,15,WHITE);s.txt(985,y+65,'Insert sourced estimate and interval',23,MUTED)
  s.note(70,890,1780,'Use published or reproducibly calculated intervals; never invent confidence bounds.')
 elif k==5:
  s.panel(70,235,470,270,'PUBLIC BENCHMARK ITEMS','Published questions\nPublic answer sets',GOLD,30)
  s.panel(690,235,470,270,'TRAINING OR TUNING','Exposure possible\nExposure unknown',CYAN,30)
  s.panel(1380,235,470,270,'REPORTED RESULT','Score may reflect\nprior exposure',GOLD,30)
  s.arrow(550,370,675,370,'possible exposure');s.arrow(1170,370,1365,370,'evaluation')
  s.panel(70,555,1780,370,'REQUIRED LIMITATION STATEMENT','Document what the source says about contamination controls. Distinguish evidence of exposure from a possibility; do not accuse a model of contamination without support.',CYAN,34)
 elif k==6:
  s.table(70,235,1780,['REPORTED LIMITATION','MITIGATION','REMAINING UNCERTAINTY'],[['Dataset coverage','Documented measure','What is still unknown'],['Answer evaluation','Documented measure','What is still unknown'],['Exposure and tuning','Documented measure','What is still unknown'],['Real-world transfer','Documented measure','What is still unknown']],row_h=135)
 elif k==7:
  s.panel(70,235,1780,150,'BEFORE COMPARING REASONING SCORES','Match or disclose test-time computation, token budget, time limit, and attempts.',GOLD,31)
  for j,label in enumerate(['MODEL A SETUP','MODEL B SETUP']):s.panel(70+j*905,415,875,440,label,'Reasoning setting\nOutput / reasoning limits\nNumber of attempts\nTool access\nProvider and evaluation date',CYAN,29)
  s.note(70,895,1780,'A score obtained with more computation may represent a different cost and latency tradeoff.')
 elif k==8:
  s.panel(70,235,540,620,'EVALUATED SAMPLES','Document count\nSelection procedure\nTask categories\nLanguage coverage',CYAN,29)
  s.panel(650,235,550,620,'EXCLUDED SAMPLES','Document exclusions\nFailure handling\nUnscored responses\nMissing observations',GOLD,29)
  s.panel(1240,235,610,620,'CLAIM BOUNDARY','Limit conclusions to evaluated conditions and adequately represented tasks.',CYAN,32)
  s.note(70,892,1780,'Small or unrepresentative samples require narrower claims, regardless of the displayed score.')
 elif k==9:
  s.panel(70,235,875,440,'HIGHER MAY BE BETTER','Examples: accuracy / successful tasks\n\nUse the source-defined direction and units.',CYAN,33);s.panel(975,235,875,440,'LOWER MAY BE BETTER','Examples: error / latency / task cost\n\nLower cost alone does not establish value.',GOLD,33)
  s.table(70,710,1780,['METRIC','UNITS','BETTER DIRECTION','CAVEAT'],[['Verified metric','Source units','Source definition','Task relevance'],['Verified metric','Source units','Source definition','Missing context']],row_h=90)
 elif k==10:
  for j,(lab,bod) in enumerate([('FINAL ANSWER','Does it match the expected answer?'),('DERIVATION','Is the reasoning valid and sufficient?'),('REPRODUCIBILITY','Can independent checks recover the result?')]):s.panel(70+j*600,235,580,475,lab,bod,CYAN if j!=1 else GOLD,32)
  s.panel(70,750,1780,230,'BENCHMARK SCOPE','Identify which of these dimensions the published test actually scores and which remain unmeasured.',GOLD,32)
 elif k==11:
  s.panel(70,235,520,570,'CODE GENERATION','Short task\nGenerated code\nDefined test suite',CYAN,30)
  s.panel(700,235,520,570,'TEST PASSING','Recorded execution\nPass criteria\nHidden test coverage',GOLD,30)
  s.panel(1330,235,520,570,'ISSUE RESOLUTION','Repository context\nAgent and tools\nValidated patch',CYAN,30)
  s.arrow(600,510,680,510);s.arrow(1230,510,1310,510);s.note(70,848,1780,'Different coding evaluations measure different products; preserve agent setup and attempt budget.')
 elif k==12:
  for j,(lab,bod) in enumerate([('VALID SYNTAX','Tool schema respected'),('CORRECT ARGUMENTS','Inputs match intent'),('TASK COMPLETED','Final result verified')]):s.panel(70+j*600,235,580,250,lab,bod,CYAN,30)
  s.arrow(650,350,665,350);s.arrow(1250,350,1265,350);s.panel(70,530,1780,385,'WHAT TO REPORT','Name the success layer actually evaluated. Show tool access, call traces, error handling, and end-to-end task checks.',GOLD,34)
 elif k==13:
  for j,(lab,bod) in enumerate([('ACCEPT INPUT','Token acceptance\nPreprocessing limits'),('FIND EVIDENCE','Relevant passages\nAccurate references'),('SYNTHESIZE','Consistent conclusions\nCross-document reasoning')]):s.panel(70+j*600,235,580,510,lab,bod,CYAN if j!=1 else GOLD,31)
  s.panel(70,785,1780,200,'VIEWER WARNING','A large advertised context window does not establish reliable synthesis across all of it.',GOLD,32)
 elif k==14:
  s.panel(70,235,620,570,'PREFERENCE VOTE','Blinded comparison\nJudges and sample\nPublished uncertainty\nTask distribution',CYAN,29)
  s.panel(730,235,1120,255,'FACTUAL CORRECTNESS','Requires separate source or objective checks.',GOLD,34)
  s.panel(730,530,1120,275,'TASK UTILITY','Requires the viewer task, constraints, and success criteria.',CYAN,34)
  s.note(70,850,1780,'Preference is useful evidence; do not silently relabel it as universal correctness.')
 elif k==15:
  s.image_slot(70,235,550,550,'IDENTICAL VISUAL INPUT')
  for j,(lab,bod) in enumerate([('PERCEPTION','Objects / text / spatial detail'),('GROUNDING','Evidence linked to image'),('REASONING','Supported interpretation')]):s.panel(660,235+j*190,1190,160,lab,bod,CYAN if j!=1 else GOLD,29)
  s.note(70,840,1780,'Record resolution, preprocessing, image limits, and the evaluation release.')
 elif k==16:
  s.panel(680,235,570,150,'VIEWER TASK','Define the required product.',GOLD,30)
  s.path('M 965 385 L 965 440 M 370 440 L 1550 440 M 370 440 L 370 490 M 965 440 L 965 490 M 1550 440 L 1550 490')
  for j,(lab,bod) in enumerate([('OBJECTIVE CHECKS','Use validated task tests.'),('HUMAN JUDGMENT','Use blinded rubric review.'),('TOOLS / SYSTEMS','Use end-to-end setup evidence.')]):s.panel(70+j*600,490,580,300,lab,bod,CYAN,30)
  s.panel(70,830,1780,160,'RELEVANCE RULE','Include a benchmark only when its measured ability helps explain the featured task.',GOLD,29)
 elif k==17:
  for j,(lab,bod) in enumerate([('COMPANY-REPORTED','Official publication\nDeveloper-controlled setup\nRecord methodology'),('INDEPENDENT','Evaluator publication\nTransparent test conditions\nRecord conflicts'),('SHOW TEST','Saved prompts and outputs\nRecorded billable usage\nReproducible scoring')]):s.panel(70+j*600,235,580,650,lab,bod,CYAN if j!=0 else GOLD,28)
  s.note(70,922,1780,'Use explicit origin labels; an official claim is not automatically independent verification.')
 elif k==18:
  s.panel(70,235,875,570,'SINGLE ATTEMPT','One output per task\nDefined success criterion\nRecorded first-pass result',CYAN,34)
  s.panel(975,235,875,570,'MULTIPLE ATTEMPTS','Allowed number of attempts\nSelection rule\nAny successful attempt\nTotal computation and cost',GOLD,30)
  s.note(70,850,1780,'Compare pass-at-one with pass-at-one; label any different attempt policy separately.')
 elif k==19:
  s.panel(70,235,530,250,'INPUT','Exact prompt and task',GOLD,31)
  for j in range(3):s.panel(670,235+j*180,540,150,'CANDIDATE OUTPUT','Recorded attempt '+chr(65+j),CYAN,25)
  s.panel(1310,415,540,240,'SELECTION STEP','Document selection rule\nDocument judge or reranker',GOLD,27)
  s.arrow(610,350,650,350);s.arrow(1225,490,1290,490);s.panel(70,805,1780,170,'ACCOUNTING RULE','Include every candidate and selection cost; never present selected best-of-many as first-pass output.',CYAN,28)
 elif k==20:
  s.panel(70,235,875,595,'FROZEN TEST SET','Stable reference\nKnown benchmark release\nComparable historical runs\nExposure risk to document',CYAN,31)
  s.panel(975,235,875,595,'REFRESHED TEST SET','Changing task set\nRun date and release essential\nDifferent sets may differ in difficulty\nRefresh procedure to document',GOLD,30)
  s.note(70,875,1780,'Historical scores require the dataset version, not only the benchmark family name.')
 elif k==21:
  s.table(70,235,1780,['MODEL','REPORTED RESULT','UNCERTAINTY','CLAIM'],[['Exact version A','Source value','Published bounds','Supported conclusion'],['Exact version B','Source value','Published bounds','Supported conclusion'],['Exact version C','Source value','Published bounds','Supported conclusion']],widths=[380,420,460,520],row_h=150)
  s.panel(70,870,1780,125,'TIE POLICY','Use a supported tie or uncertainty statement rather than forcing a unique winner.',GOLD,27)
 elif k==22:
  s.panel(70,235,650,580,'SATURATION CHECK','Are most contenders near the ceiling?\nDoes the score still distinguish relevant errors?\nIs a harder test available?',GOLD,31)
  s.panel(760,235,1090,250,'DISPLAYED SCORE','Sourced value / metric / benchmark version',CYAN,34);s.panel(760,525,1090,290,'REMAINING DISCRIMINATION','Show failure cases and a relevant task test instead of implying small score gaps prove superiority.',GOLD,30)
  s.note(70,860,1780,'Retire or de-emphasize benchmarks that no longer help explain viewer decisions.')
 elif k==23:
  labels=['BENCHMARK RELEASE','MODEL RELEASE','EVALUATION RUN','RESULT PUBLICATION']
  for j,label in enumerate(labels):
   y=235+j*182;s.circle(100,y+75,13,CYAN);s.panel(150,y,1700,150,label,'Record exact date and immutable release reference.',GOLD if j==2 else CYAN,29)
   if j<3:s.line(100,y+90,100,y+181,CYAN,3)
 elif k==24:
  s.table(70,235,1780,['SETUP FIELD','MODEL A','MODEL B'],[['System prompt','Saved exact input','Saved exact input'],['Tools / retrieval','Recorded availability','Recorded availability'],['Inference budget','Recorded setting','Recorded setting'],['Attempts / selection','Recorded policy','Recorded policy'],['Harness / scoring','Saved release','Saved release']],widths=[520,630,630],row_h=108)
 elif k==26:
  kinds=[('FACT ERROR','Unsupported or incorrect statement'),('INSTRUCTION ERROR','Ignored requirement'),('TOOL ERROR','Invalid or ineffective tool action'),('OMISSION','Necessary content missing'),('FORMAT ERROR','Output schema not respected'),('RELIABILITY GAP','Inconsistent repeated outcome')]
  for j,(lab,bod) in enumerate(kinds):s.panel(70+(j%3)*600,235+(j//3)*340,580,305,lab,bod,CYAN if j%2==0 else GOLD,29)
 elif k==27:
  s.table(70,235,1780,['METRIC FAMILY','UNITS TO RECORD','INTERPRETATION'],[['Task accuracy','Percentage / denominator','Correctness on tested tasks'],['Preference','Source-defined score','Relative preference in setup'],['Latency','Time + measurement method','Responsiveness under conditions'],['Cost','Currency + billing basis','Price of stated workload'],['Reliability','Failure rate + sample','Observed consistency']],widths=[460,600,720],row_h=109)
 elif k==28:
  for j,label in enumerate(['TASK CATEGORY A','TASK CATEGORY B','TASK CATEGORY C']):s.panel(70+j*600,235,580,280,label,'Sourced metric\nDocumented weight\nRelevant caveat',CYAN,30)
  s.path('M 360 515 L 360 575 L 1540 575 L 1540 515 M 950 575 L 950 630')
  s.panel(390,630,1140,265,'AGGREGATE RESULT','Preserve the published weighting. Do not invent an overall intelligence score from incompatible metrics.',GOLD,33)
 elif k==29:
  s.table(70,235,1780,['VIEWER TASK','RELEVANT EVIDENCE','GAP / LIMITATION'],[['Writing','Saved rubric / preference','Record gap'],['Code and tools','Validated execution','Record gap'],['Research and documents','Source verification','Record gap'],['Reasoning and data','Objective task checks','Record gap'],['Vision and multimedia','Input-specific evaluation','Record gap']],widths=[430,650,700],row_h=108)
 s=distinct_benchmark(s,k,title,SVG)
 save(s,'benchmark-explainer',title,usage,['benchmark-methodology','scope','uncertainty','citation'])

# 30 recommendation / verdict structures.
verdicts=[
('Qualified recommendation','A recommendation tied to the observed task and evidence scope.'),('Lowest-cost qualifying option','Identify the cheapest tested option meeting predeclared requirements.'),('When to upgrade','State the evidence-based condition requiring a more expensive service.'),('Task-specific choices','Separate recommendations for different tasks.'),('No clear winner','Communicate a supported tie and the remaining practical differentiators.'),('Provisional finding','Present a limited finding with a concrete verification step.'),('Insufficient evidence','Display an honest evidence gap instead of a forced ranking.'),('Task failed','Show the failed requirement and next defensible alternative.'),('Best observed product','Distinguish the best output in the observed sample from broad superiority.'),('Equivalence claim boundary','State that comparable observations do not prove statistical equivalence.'),('Task recommendation matrix','Quick reference aligning viewer task, recommendation, and caveat.'),('Budget decision path','Choose an option based on task success and cost boundaries.'),('Quality threshold verdict','Use a predeclared minimum quality threshold rather than winner language.'),('Avoid for this task','Show the specific observed failure limiting a recommendation.'),('Platform feature advantage','Recommend a platform based on an available feature and verified result.'),('Access-aware recommendation','Show availability conditions that qualify a recommendation.'),('Evidence confidence verdict','Separate evidence confidence from model preference.'),('Time-value tradeoff','Explain a measured speed/quality/cost decision.'),('Baseline and challenger','Compare a new contender with a stable prior baseline.'),('Specialist recommendation','Identify a narrow strength without claiming universal dominance.'),('Requirements checklist verdict','Make passed and failed requirements visible.'),('Risk and cost verdict','Show when risk tolerance changes the cheapest qualifying choice.'),('Task scope boundary','State where the recommendation applies and where it has not been tested.'),('Cost per successful task verdict','Explain value including all failed attempts.'),('Price-change verdict','Update value conclusions after a verified billing change.'),('Benchmark and demo disagreement','Make a disagreement between published evidence and an individual task visible.'),('Executive decision card','Readable short recommendation for screenshot recall.'),('Three practical takeaways','Summarize task choice, spending implication, and caveat.'),('Next verification trigger','State the evidence event that would change the recommendation.'),('Comparison index reference','Direct viewers to dated records and obsolete findings.')]
for k,(title,usage) in enumerate(verdicts):
 s=SVG(title,'verdict','Recommendations must be bounded by tested task, observed evidence, access conditions, and date.')
 if k in (0,1,8,19,26):
  s.panel(70,235,1120,415,'RECOMMENDATION / EXACT MODEL VERSION','Insert supported recommendation\n\nFor this task and these conditions',CYAN,37)
  s.panel(1220,235,630,415,'VALUE RECORD','Measured task cost\nRelevant benchmark\nObserved task success\nChecked date',GOLD,28)
  s.panel(70,685,1780,300,'WHY / LIMITATION','State the decisive output evidence, the cheaper alternative, and the condition where this finding may not apply.',GOLD,32)
 elif k in (2,11,12,21):
  s.panel(660,235,600,180,'TASK REQUIREMENT','Define the minimum acceptable result.',GOLD,31)
  s.path('M 960 415 L 960 465 M 500 465 L 1420 465 M 500 465 L 500 530 M 1420 465 L 1420 530')
  s.panel(70,530,860,290,'REQUIREMENT MET','Choose the lowest-cost tested option that satisfies the requirement.',CYAN,32)
  s.panel(990,530,860,290,'REQUIREMENT NOT MET','Upgrade, change setup, or disclose that no tested option qualifies.',GOLD,30)
  s.note(70,865,1780,'Record exact model, provider, task, test scope, cost basis, and the evidence supporting this path.')
 elif k in (3,10):
  s.table(70,235,1780,['VIEWER TASK','SUPPORTED CHOICE','COST BASIS','LIMITATION'],[['Task A','Exact model + provider','Verified task cost','Scope caveat'],['Task B','Exact model + provider','Verified task cost','Scope caveat'],['Task C','Exact model + provider','Verified task cost','Scope caveat']],widths=[340,520,440,480],row_h=180)
 elif k in (4,9):
  s.panel(70,235,875,490,'OBSERVATION A','Exact model\nObserved rubric outcome\nTotal task cost\nComparable benchmark context',CYAN,31)
  s.panel(975,235,875,490,'OBSERVATION B','Exact model\nObserved rubric outcome\nTotal task cost\nComparable benchmark context',GOLD,31)
  s.panel(70,765,1780,230,'SUPPORTED CONCLUSION','Insert the uncertainty statement. Absence of a clear difference does not prove equivalence.',GOLD,33)
 elif k in (5,6,16):
  s.panel(70,235,1780,220,'WHAT IS ESTABLISHED','Only the findings supported by available evidence.',CYAN,36)
  s.panel(70,490,860,320,'WHAT REMAINS UNKNOWN','Missing data / weak comparability / untested setup',GOLD,32)
  s.panel(970,490,880,320,'NEXT VALID CHECK','Concrete evidence or test that resolves the uncertainty.',CYAN,32)
  s.note(70,865,1780,'Do not turn incomplete evidence into a definitive recommendation.')
 elif k in (7,13):
  s.panel(70,235,540,600,'REQUIRED RESULT','Predeclared check\nEvidence needed\nAcceptable behavior',GOLD,30)
  s.panel(650,235,1200,285,'OBSERVED FAILURE','Actual output excerpt + executed verification',CYAN,35)
  s.panel(650,550,1200,285,'PRACTICAL CONSEQUENCE','State the task-specific limitation and a supported alternative.',GOLD,33)
  s.note(70,880,1780,'A failure in this task is evidence about this task and setup, not a universal model judgment.')
 elif k==14:
  s.image_slot(70,235,1000,505,'ACTUAL PLATFORM FEATURE SCREENSHOT');s.panel(1100,235,750,505,'FEATURE VERDICT','Feature / plan / region\nObserved user benefit\nLimitations\nCost basis',GOLD,31)
  s.panel(70,780,1780,210,'REPRODUCIBLE WORKFLOW','Inputs → feature settings → actual product → verification',CYAN,32)
 elif k==15:
  s.table(70,235,1780,['ACCESS CONDITION','RECOMMENDATION DEPENDENCY'],[['Cloud provider / endpoint','Record exact service'],['Plan and feature availability','Record tested access tier'],['Region / language / rollout','Record limitations'],['Observation date','Record verification date']],widths=[640,1140],row_h=140)
  s.note(70,958,1780,'Confirm current availability before recommending a feature or model.')
 elif k==17:
  for j,(lab,bod) in enumerate([('QUALITY','Recorded task outcome'),('TIME','Measured response completion'),('COST','Total billed task cost')]):s.panel(70+j*600,235,580,360,lab,bod,CYAN if j!=2 else GOLD,34)
  s.panel(70,640,1780,330,'VIEWER DECISION','Explain which tradeoff matters for this task. Use measured timing; label estimates and avoid unsupported productivity claims.',GOLD,34)
 elif k==18:
  s.panel(70,235,875,545,'SAVED BASELINE','Exact model + date\nSaved prompt and product\nMeasured task cost\nRelevant benchmark source',CYAN,31)
  s.panel(975,235,875,545,'CHALLENGER','Exact model + date\nSame prompt and constraints\nMeasured task cost\nRelevant benchmark source',GOLD,31)
  s.panel(70,820,1780,175,'CHANGE IN RECOMMENDATION','What evidence justifies keeping or replacing the prior choice?',CYAN,29)
 elif k==20:
  s.table(70,235,1780,['REQUIREMENT','OBSERVED EVIDENCE','OUTCOME','FOLLOW-UP'],[['Objective check A','Output / executed test','Verified result','Needed action'],['Objective check B','Output / source check','Verified result','Needed action'],['Objective check C','Output / rubric check','Verified result','Needed action'],['Total task cost','Saved billing data','Verified amount','Cost consequence']],widths=[420,620,330,410],row_h=135)
 elif k==22:
  s.panel(70,235,875,605,'APPLIES TO','Specific task\nRecorded model version\nRecorded provider\nRecorded settings\nSaved input conditions',CYAN,30)
  s.panel(975,235,875,605,'NOT ESTABLISHED','Other task categories\nOther service defaults\nUntested languages\nFuture model releases\nUnmeasured reliability',GOLD,30)
  s.note(70,885,1780,'Keep recommendation scope visible wherever the finding is reused.')
 elif k==23:
  s.panel(70,235,650,600,'ALL ATTEMPTS','Successful attempts\nFailed attempts\nRetries\nTools / reasoning\nTotal billing',GOLD,30)
  s.panel(760,235,1090,270,'VALUE METRIC','Total measured task spending ÷ verified successful tasks',CYAN,36)
  s.panel(760,540,1090,295,'SUPPORTED CHOICE','State the observed result and sample limits. Do not exclude unsuccessful attempts.',GOLD,32)
  s.note(70,885,1780,'Report first-pass success separately from eventual success.')
 elif k==24:
  s.panel(70,235,875,295,'PREVIOUS PRICE BASIS','Saved official rate / date / workload',CYAN,34)
  s.panel(975,235,875,295,'CURRENT PRICE BASIS','Verified official rate / date / same workload',GOLD,34)
  s.panel(70,570,1780,400,'UPDATED VALUE CONCLUSION','Recalculate using the same measured usage. Explain whether the price change affects the recommendation without implying untested quality changes.',CYAN,35)
 elif k==25:
  s.panel(70,235,875,510,'PUBLISHED BENCHMARK','Source / setup / version\nRelevant score\nMeasured capability\nKnown limitations',CYAN,31)
  s.panel(975,235,875,510,'OBSERVED TASK PRODUCT','Exact prompt and setup\nActual output\nRubric outcome\nMeasured task cost',GOLD,31)
  s.panel(70,790,1780,205,'WHY THEY MAY DIFFER','Task coverage, sampling, tools, settings, or unknown factors; mark inferences explicitly.',GOLD,30)
 elif k==27:
  for j,(lab,bod) in enumerate([('MODEL CHOICE','Exact model for the stated task'),('SPENDING','Verified cost and supported savings'),('LIMITATION','Where the evidence stops')]):s.panel(70+j*600,235,580,640,lab,bod,CYAN if j!=1 else GOLD,35)
  s.note(70,921,1780,'Keep these takeaways visible long enough for viewers to read or pause.')
 elif k==28:
  s.panel(70,235,1780,210,'CURRENT FINDING','Bounded conclusion / date / evidence references',CYAN,36)
  for j,(lab,bod) in enumerate([('PRICE EVENT','A verified rate change'),('CAPABILITY EVENT','A relevant model or feature update'),('EVIDENCE EVENT','A reproducible result or correction')]):s.panel(70+j*600,490,580,350,lab,bod,GOLD if j==0 else CYAN,30)
  s.note(70,889,1780,'A trigger initiates rechecking; it does not automatically reverse the recommendation.')
 else:
  s.panel(70,235,650,610,'SEARCHABLE RECORD','Task tags\nExact model\nCost basis\nEpisode link\nVerification date',CYAN,31)
  s.panel(760,235,1090,285,'CURRENT FINDING','Recommendation + source-linked evidence',GOLD,35)
  s.panel(760,560,1090,285,'HISTORICAL FINDING','Mark superseded records and link the replacement.',CYAN,35)
  s.note(70,893,1780,'Generate this index from the same evidence records used by the episode.')
 s=distinct_verdict(s,k,title,SVG)
 save(s,'verdict',title,usage,['recommendation','task-scope','viewer-decision'])

# 30 change reporting layouts. All previous/current labels are unfilled evidence slots.
changes=[
('New cloud model release','Show launch facts, access, relevant comparisons, and evidence gaps.'),('Official model retirement','Explain officially announced deprecation and verified migration options.'),('Verified price decrease','Separate a price reduction from unmeasured capability changes.'),('Verified price increase','Explain new billing with identical-workload cost implications.'),('Context capability change','Report input/output limit changes with actual handling evidence.'),('Multimodal capability added','Report new supported modalities and verified cloud availability.'),('Platform feature release','Show a new feature with a tested user workflow.'),('Tool access expanded','Report a tool or connector change and its effect on the evaluated system.'),('Rate limit change','Report changed limits and user consequences without guessing throughput.'),('Measured latency change','Compare verified timing under recorded conditions.'),('Default routing change','Distinguish provider routing changes from fixed-version model changes.'),('Changelog evidence strip','Show source-linked change entries and practical implications.'),('Benchmark method changed','Explain how evaluation method revisions affect comparison validity.'),('Published result revised','Preserve previous and revised results with the source explanation.'),('Evaluator update','Explain scoring changes without attributing them to model improvement.'),('Region access expanded','Show verified regional availability and remaining restrictions.'),('Subscription plan changed','Report plan changes separately from API rates.'),('API endpoint changed','Explain verified endpoint and compatibility changes.'),('Billing rules changed','Report changes to token/tool/cache billing and workload impact.'),('Output limit changed','Show changed output limits without implying better long-form accuracy.'),('Reasoning control added','Explain new reasoning settings and cost/latency tradeoffs.'),('Citations feature changed','Show new source presentation and required citation checks.'),('Memory feature changed','Explain user controls and practical limitations.'),('Connector release','Show newly supported connected data and access permissions.'),('Artifact feature changed','Explain new product-generation or export capabilities.'),('Error handling changed','Compare observed error behavior and documented fixes.'),('Source evidence updated','Track changes to a cited source and affected episode claims.'),('Model access withdrawn','Explain verified loss of access and supported alternatives.'),('Documented defect fix','Connect an official fix to reproduced behavior and test limits.'),('Episode correction card','Clearly correct an earlier statement and link the updated evidence.')]
for k,(title,usage) in enumerate(changes):
 s=SVG(title,'change report','Previous and current facts require dated source evidence; an announcement is not a completed test.')
 variant=k%10
 if variant==0:
  s.image_slot(70,235,950,440,'OFFICIAL ANNOUNCEMENT / CAPTURE');s.panel(1050,235,800,440,'VERIFIED CHANGE','Exact model / feature\nRelease date\nCloud availability\nSource-linked facts',GOLD,30)
  s.panel(70,715,875,270,'VIEWER IMPACT','What the change enables\nWhat should be retested',CYAN,29);s.panel(975,715,875,270,'EVIDENCE BOUNDARY','Announced / available / tested\nUnknown or unverified claims',GOLD,29)
 elif variant==1:
  s.panel(70,235,1780,170,'OFFICIAL CHANGE NOTICE','Exact affected model / date / source / availability status',GOLD,32)
  for j,(lab,bod) in enumerate([('BEFORE','Saved conditions and evidence'),('AFTER','Verified conditions and evidence'),('USER ACTION','Evidence-based next step')]):s.panel(70+j*600,445,580,420,lab,bod,CYAN if j!=2 else GOLD,31)
  s.note(70,910,1780,'Label announced future changes separately from changes currently in effect.')
 elif variant==2:
  s.table(70,235,1780,['FIELD','PREVIOUS / dated','CURRENT / dated'],[['Affected product','Exact identity','Exact identity'],['Changed condition','Saved verified fact','Current verified fact'],['Price / limits','Saved billing basis','Current billing basis'],['Source evidence','URL / date / snapshot','URL / date / snapshot']],widths=[440,670,670],row_h=135)
  s.note(70,930,1780,'Recompute only affected claims; preserve earlier records as historical evidence.')
 elif variant==3:
  s.panel(70,235,1780,210,'WHAT CHANGED','One precise, sourced statement of the change.',CYAN,40)
  s.panel(70,485,875,420,'VALUE IMPLICATION','Same task / measured usage\nRecalculated cost or access\nPractical user consequence',GOLD,33)
  s.panel(975,485,875,420,'WHAT IS NOT ESTABLISHED','Untested quality effects\nUnmeasured reliability\nUnconfirmed rollout access',CYAN,33)
 elif variant==4:
  s.panel(70,235,530,680,'CHANGE LOG','Source / update date\nPrevious condition\nCurrent condition\nAffected products',GOLD,30)
  s.panel(640,235,1210,295,'BEFORE / SAVED EVIDENCE','Exact prior fact, output, or behavior.',CYAN,36)
  s.panel(640,570,1210,345,'AFTER / VERIFIED EVIDENCE','Exact revised fact, output, or behavior. Explain comparability.',GOLD,34)
 elif variant==5:
  for j,(lab,bod) in enumerate([('ANNOUNCED','What the source promises'),('AVAILABLE','What users can access'),('TESTED','What the show has verified')]):s.panel(70+j*600,235,580,500,lab,bod,CYAN if j!=0 else GOLD,34)
  s.panel(70,775,1780,210,'DO NOT COLLAPSE THESE STATES','Record the date, plan, region, and evidence for each state.',GOLD,32)
 elif variant==6:
  s.image_slot(70,235,850,500,'PREVIOUS EVIDENCE / SNAPSHOT');s.image_slot(1000,235,850,500,'CURRENT EVIDENCE / SNAPSHOT');s.arrow(935,480,985,480)
  s.panel(70,775,1780,210,'VERIFIED DIFFERENCE','Mark the changed passage or behavior; keep original captures intact.',GOLD,32)
 elif variant==7:
  for j,(lab,bod) in enumerate([('PREVIOUS STATE','Saved record / date'),('CHANGE EVENT','Official evidence / date'),('CURRENT STATE','Verified record / date')]):
   y=235+j*215;s.panel(170,y,1680,175,lab,bod,GOLD if j==1 else CYAN,30);s.circle(100,y+82,14,CYAN)
   if j<2:s.line(100,y+98,100,y+210,CYAN,3)
 elif variant==8:
  s.panel(70,235,1780,170,'AFFECTED VIEWER WORKFLOW','Exact task, platform feature, or API workload.',GOLD,32)
  for j,(lab,bod) in enumerate([('INPUTS','What users supply'),('BEHAVIOR','What the service changed'),('RESULT','What users obtain')]):s.panel(70+j*600,445,580,365,lab,bod,CYAN,32)
  s.arrow(650,620,665,620);s.arrow(1250,620,1265,620);s.note(70,860,1780,'Preserve billing, region, plan, and verification date beside any practical claim.')
 else:
  s.panel(70,235,780,600,'EARLIER STATEMENT','Exact original statement\nEpisode / timestamp\nOriginal supporting evidence',GOLD,33)
  s.panel(890,235,960,285,'CORRECTED STATEMENT','Precise replacement supported by current evidence.',CYAN,35)
  s.panel(890,570,960,265,'REASON + EFFECT','Why it changed and which recommendations or graphics are affected.',GOLD,31)
  s.note(70,882,1780,'Keep the correction discoverable in the episode index and evidence history.')
 # Distinct change-specific ribbon prevents replacing actual context with generic before/after claims.
 change_fields=[['Exact release ID','Launch versus availability','Comparable baseline'],['Official last-use date','Replacement endpoint','Migration behavior'],['Previous input/output rates','Current input/output rates','Same saved workload'],['Billing effective date','Changed price basis','Same measured usage'],['Accepted input limit','Output limit','Observed truncation'],['New input modality','Supported output mode','Plan and region'],['Feature controls','Actual product','Access eligibility'],['Available tools','Permission scope','Full-system result'],['Request/token limits','Limit window','Observed failure handling'],['First token timing','Full completion timing','Repeated conditions'],['Routing policy','Model identity certainty','Pinned comparison'],['Source passage','Change timestamp','Practical consequence'],['Metric definition','Attempt policy','Comparable release'],['Previous score record','Revised score record','Source explanation'],['Evaluator release','Rubric change','Rescoring scope'],['Provider region','Rollout status','Account eligibility'],['Included usage','Feature entitlements','API separate'],['Endpoint ID','Deprecation schedule','Compatibility test'],['Reasoning/tool charges','Cache rules','Price basis'],['Documented maximum','Actual task output','Reliability untested'],['Setting names','Billing implications','Observed product'],['Link existence','Claim support','Citation presentation'],['Memory controls','Persistence behavior','Privacy permissions'],['Connector identity','Granted permissions','Retrieved source'],['Generated artifact','Export format','Actual usability'],['Observed error','Retry behavior','Cost consequence'],['Changed source fact','Affected claim IDs','Dependent scenes'],['Access status','Notice date','Supported alternative'],['Official fix ID','Reproduction setup','Observed validation'],['Original claim','Corrected claim','Impacted conclusions']]
 # Specific text is part of a complete semantic template, not a fabricated result.
 s=distinct_change(s,k,title,change_fields[k],SVG)
 s.txt(70,1004,'CHECK: '+' / '.join(change_fields[k]),18,MUTED)
 save(s,'change-report',title,usage,['before-after','verified-change','date'])

# 30 feature tutorials with varied user flow structures and feature-specific input checks.
features=[
('Cloud project workspace','Help users organize reusable context in a cloud workspace.'),('Custom instruction setup','Teach a user to set, scope, and verify custom instructions.'),('PDF analysis workflow','Teach cloud PDF upload, evidence requests, and source checks.'),('Web browsing with citations','Teach source-backed browsing and claim verification.'),('Deep research workflow','Teach research brief, evidence review, and useful report extraction.'),('Cloud coding agent workflow','Teach scoped coding work with reviewed diffs and executed checks.'),('Canvas editing workflow','Teach iterative editing in a cloud writing or coding canvas.'),('Structured output setup','Teach cloud response schemas and independent validation.'),('Function call workflow','Teach tool definitions, permissions, calls, and end-to-end verification.'),('Connector permission workflow','Teach minimal connected-data permissions and source verification.'),('Memory controls workflow','Teach viewing, editing, disabling, and checking cloud memory.'),('Voice interaction workflow','Teach cloud voice session controls and transcript checks.'),('Image creation workflow','Teach image briefs, revisions, export, and labeling.'),('Vision analysis workflow','Teach visual input preparation and evidence-based interpretation.'),('Document creation workflow','Teach generating and verifying a useful exported document.'),('Data analysis workflow','Teach dataset preparation, computation, and chart verification.'),('Artifact creation workflow','Teach a reusable cloud artifact with tested outputs.'),('Reasoning setting workflow','Teach choosing and verifying a reasoning setting for a task.'),('Batch API workflow','Teach cloud batch preparation, status, validation, and billing.'),('Prompt cache workflow','Teach cache eligibility, usage verification, and cost accounting.'),('Usage dashboard workflow','Teach measuring cloud spending with official usage data.'),('API key permission workflow','Teach secure access management without exposing secrets.'),('Rate limit handling workflow','Teach documented limits, retries, and monitoring.'),('Share and export workflow','Teach permissions and useful exports from cloud platforms.'),('Model version pinning workflow','Teach choosing, recording, and updating exact model versions.'),('Team workspace workflow','Teach roles, shared context, access boundaries, and review.'),('Region availability workflow','Teach confirming cloud availability and plan restrictions.'),('Citation audit workflow','Teach checking whether a linked source supports each claim.'),('Mobile cloud feature workflow','Teach a mobile cloud workflow with readable outputs and export.'),('Multi-step platform workflow','Teach a composed cloud workflow with verification at each stage.')]
feature_steps=[
['Create workspace','Add verified reference files','Set scoped instructions','Test recall / update'],['Define desired behavior','Set instruction scope','Run contrasting test prompts','Correct unwanted behavior'],['Upload supported PDF','Ask for cited passages','Compare output with pages','Export verified summary'],['Ask focused question','Review retrieved sources','Verify key claims','Save cited answer'],['Define research goal','Record constraints and sources','Review evidence and conflicts','Extract useful report'],['Set task and boundaries','Review agent plan','Inspect diff and run checks','Accept validated product'],['Open editable canvas','Specify desired edit','Review changed passages','Export clean version'],['Define response schema','Send exact request','Validate actual response','Handle invalid output'],['Define tools and permissions','Run cloud request','Review call traces','Verify completed task'],['Select required connector','Grant minimal access','Inspect retrieved evidence','Remove unneeded permission'],['Review saved memory','Edit or remove an item','Change controls','Test expected behavior'],['Start voice session','Set speaking controls','Review transcript','Save useful product'],['Describe purpose and composition','Generate cloud image','Inspect and revise','Export and label'],['Upload clear image','Ask bounded question','Check visible evidence','Record uncertainty'],['State document purpose','Generate editable document','Verify layout and facts','Export final artifact'],['Upload clean dataset','Request reproducible analysis','Check calculations and chart','Export results'],['Specify usable artifact','Generate cloud component','Test actual behavior','Export reusable version'],['Choose reasoning setting','Run same task','Record product and usage','Compare quality / cost'],['Prepare exact batch inputs','Submit cloud batch','Validate per-item products','Reconcile billed usage'],['Confirm cache eligibility','Submit reusable prefix','Check reported cached usage','Calculate actual savings'],['Choose reporting window','Inspect official usage','Reconcile task records','Track billing differences'],['Create scoped key','Store without exposing it','Test authorized access','Rotate or revoke safely'],['Read documented limits','Use bounded retries','Inspect errors and spending','Adjust supported workload'],['Select useful export','Inspect access permissions','Check exported product','Share intended version'],['Select exact model ID','Record endpoint and settings','Save baseline test','Retest when updating'],['Set workspace roles','Share scoped materials','Review access and outputs','Maintain useful references'],['Check region and plan','Confirm feature rollout','Run authorized test','Record access limitations'],['Open source link','Locate supporting passage','Check date and scope','Correct unsupported claim'],['Choose supported cloud feature','Prepare readable input','Verify output on phone','Export or continue on desktop'],['Prepare verified inputs','Use platform feature','Validate intermediate product','Export checked result']]
for k,(title,usage) in enumerate(features):
 s=SVG(title,'platform how-to','Use current official documentation; show actual controls and note plan, region, and rollout restrictions.')
 steps=feature_steps[k];v=k%10
 if v==0:
  s.image_slot(70,235,960,600,'ACTUAL PLATFORM UI / CURRENT CAPTURE')
  for j,step in enumerate(steps):s.panel(1065,235+j*150,785,126,'STEP '+str(j+1),step,CYAN if j!=3 else GOLD,25)
  s.note(70,875,1780,'Feature / tested plan / region / verified date / source / observed limitation')
 elif v==1:
  s.panel(70,235,1780,180,'USER GOAL','Define the useful product and successful behavior.',GOLD,34)
  for j,step in enumerate(steps):s.panel(70+j*450,455,430,360,'STEP '+str(j+1),step,CYAN if j%2==0 else GOLD,30)
  s.note(70,865,1780,'Test the resulting behavior; a configured control is not proof that instructions will always be followed.')
 elif v==2:
  s.panel(70,235,480,610,'BEFORE YOU START','Input requirements\nPlan and region\nPermissions\nData format\nDocumented limits',GOLD,30)
  for j,step in enumerate(steps):s.panel(590+(j%2)*645,235+(j//2)*320,615,285,'STEP '+str(j+1),step,CYAN,31)
  s.note(70,895,1780,'Keep real screenshots and the completed product in the episode evidence record.')
 elif v==3:
  s.image_slot(70,235,875,480,'CONTROL / SOURCE UI');s.image_slot(975,235,875,480,'ACTUAL PRODUCT / VERIFIED OUTPUT')
  for j,step in enumerate(steps):s.panel(70+j*450,755,430,220,'STEP '+str(j+1),step,GOLD if j==2 else CYAN,25)
 elif v==4:
  for j,step in enumerate(steps):
   y=235+j*182;s.circle(100,y+70,14,CYAN);s.panel(160,y,1030,150,'STEP '+str(j+1),step,CYAN if j!=2 else GOLD,29)
   if j<3:s.line(100,y+87,100,y+178,CYAN,3)
  s.panel(1230,235,620,680,'REVIEW BEFORE USING','Source existence\nClaim support\nUsable output\nCost / time limits\nPrivacy / permission scope',GOLD,28)
 elif v==5:
  s.panel(70,235,1780,145,'WORKFLOW GOAL','Useful cloud-produced artifact with recorded evidence and explicit success criteria.',GOLD,29)
  s.panel(70,420,840,245,'PREPARE',steps[0]+'\n'+steps[1],CYAN,31)
  s.panel(1010,420,840,245,'VERIFY',steps[2]+'\n'+steps[3],GOLD,31);s.arrow(930,540,990,540)
  s.image_slot(70,705,1780,275,'ACTUAL COMPLETED PRODUCT / INSPECTED RESULT')
 elif v==6:
  s.panel(70,235,560,690,'SETUP',steps[0]+'\n\n'+steps[1]+'\n\nRecord plan and controls.',GOLD,30)
  s.image_slot(670,235,1180,390,'ACTUAL CLOUD FEATURE SCREENSHOT')
  s.panel(670,665,1180,260,'VALIDATE AND EXPORT',steps[2]+'\n'+steps[3],CYAN,30)
 elif v==7:
  s.table(70,235,1780,['ACTION','WHY IT MATTERS','EVIDENCE TO SAVE'],[[steps[0],'Defines task and setup','Input / settings'],[steps[1],'Produces actual behavior','Response / trace'],[steps[2],'Checks result','Validator / source check'],[steps[3],'Makes result usable','Export / billing record']],widths=[730,520,530],row_h=132)
  s.note(70,923,1780,'Do not display credentials, private records, or unapproved personal data in demonstration captures.')
 elif v==8:
  s.panel(70,235,850,295,'PREPARATION',steps[0]+'\n'+steps[1],GOLD,32)
  s.panel(1000,235,850,295,'VALIDATION',steps[2]+'\n'+steps[3],CYAN,32)
  s.path('M 490 530 L 490 600 L 1430 600 L 1430 530 M 960 600 L 960 660')
  s.panel(430,660,1060,275,'COMPLETED WORKFLOW','Save actual products, errors, per-item checks, and total cloud billing.',GOLD,33)
 else:
  s.image_slot(70,235,630,630,'CURRENT FEATURE UI');s.panel(740,235,1110,200,'PERMISSION / INPUT BOUNDARY',steps[0]+'\n'+steps[1],GOLD,30)
  s.panel(740,475,1110,390,'EVIDENCE AND OUTCOME',steps[2]+'\n\n'+steps[3]+'\n\nRecord access scope and unsupported behavior.',CYAN,31)
  s.note(70,915,1780,'Use official controls and sources; do not claim a feature is available to every account.')
 s=distinct_feature(s,k,title,steps,SVG)
 s.txt(70,1004,'FEATURE DEMO / '+title+' / exact platform + current documentation required',18,MUTED)
 save(s,'feature-how-to',title,usage,['platform-feature','tutorial','cloud-only','actual-ui'])

# 15 provenance-specific layouts.
provenance=[
('Visible source attribution','A readable attribution composition for evidence images.'),('Screenshot capture record','Metadata accompanying a captured webpage or selected element.'),('Claim evidence record','Connect one claim to exact source passages and saved evidence.'),('Episode citation list','A readable list of episode-specific sources with claim mapping.'),('Source quality rubric','Explain source authority, transparency, independence, and currency.'),('Verification timestamp card','Show when facts were checked and which dates are distinct.'),('Evidence chain map','Trace source, claim, graphic, narration, and recommendation.'),('Original and annotated capture','Preserve original website capture beside reversible editorial annotations.'),('Evaluation methodology record','Capture the full setup for a cited evaluation.'),('Conflicting source record','Display conflicting sources and the supported resolution.'),('Asset reuse permission record','Track actual license and reuse restrictions before public distribution.'),('Evidence change history','Track source revisions and dependent claims.'),('Screenshot integrity checklist','Verify a screenshot represents the cited source accurately.'),('Original asset attribution','Carry license and attribution for reusable show-generated artwork.'),('Publication evidence gate','A final gate for claim support, current pricing, and reproducibility.')]
for k,(title,usage) in enumerate(provenance):
 s=SVG(title,'citation and provenance')
 if k==0:
  s.image_slot(70,235,1780,440,'REAL SOURCE IMAGE / EXACT RELEVANT EXCERPT');s.panel(70,715,1780,280,'VISIBLE ATTRIBUTION','Publisher / page title / publication or update date\nSource URL / capture date / benchmark release\nCompany-reported, independent, or original test',GOLD,29)
 elif k==1:
  s.image_slot(70,235,950,760,'PRESERVED ORIGINAL CAPTURE');s.panel(1050,235,800,760,'CAPTURE METADATA','Exact URL\nPage title\nCapture timestamp + timezone\nViewport and element selector\nContent date\nOriginal file hash\nReuse restrictions',GOLD,28)
 elif k==2:
  s.panel(70,235,1780,170,'CLAIM ID / EXACT STATEMENT','The precise factual statement supported by this record.',CYAN,32)
  s.panel(70,445,875,375,'SUPPORTING PASSAGE','Source title / URL / date\nExact location / excerpt\nScope and context',GOLD,31);s.panel(975,445,875,375,'CLAIM VALIDATION','How the source supports it\nConflicts or limitations\nDate checked / checker',CYAN,31)
  s.note(70,865,1780,'A source being reputable does not mean it supports this particular claim.')
 elif k==3:
  s.table(70,235,1780,['SOURCE','CLAIMS SUPPORTED','VERIFIED DATE'],[['Official release / exact URL','Claim IDs / slide references','Checked date'],['Benchmark maintainer / URL','Claim IDs / method references','Checked date'],['Independent evaluator / URL','Claim IDs / score references','Checked date'],['Original show run / record','Claim IDs / product references','Run date']],widths=[810,640,330],row_h=145)
 elif k==4:
  for j,(lab,bod) in enumerate([('AUTHORITY','Does this source own or directly evaluate the fact?'),('TRANSPARENCY','Can the method or original record be inspected?'),('INDEPENDENCE','Are affiliations and conflicts stated?'),('CURRENCY','Is this the current applicable version?')]):s.panel(70+(j%2)*905,235+(j//2)*375,875,340,lab,bod,CYAN if j%2==0 else GOLD,32)
 elif k==5:
  s.table(70,235,1780,['DATE TYPE','WHAT IT MEANS','RECORD'],[['Event date','When the change occurred','Source date'],['Publication date','When the source published it','Source date'],['Capture date','When evidence was saved','Timestamp + timezone'],['Verification date','When the claim was checked','Timestamp + scope']],widths=[450,880,450],row_h=145)
 elif k==6:
  for j,(lab,bod) in enumerate([('SOURCE','Exact URL + snapshot'),('CLAIM','Supported statement'),('GRAPHIC','Data + rendered visual')]):s.panel(70+j*600,235,580,245,lab,bod,CYAN,28)
  s.arrow(650,350,665,350);s.arrow(1250,350,1265,350)
  s.panel(70,545,875,340,'NARRATION','Spoken claim mapped to evidence ID and slide cue.',GOLD,32);s.panel(975,545,875,340,'RECOMMENDATION','Bounded conclusion mapped to claim and task record.',CYAN,32)
  s.note(70,928,1780,'A corrected source should identify every dependent graphic, statement, and recommendation.')
 elif k==7:
  s.image_slot(70,235,875,480,'PRESERVED ORIGINAL / UNALTERED');s.image_slot(975,235,875,480,'EDITORIAL OVERLAY / SEPARATE LAYER');s.panel(70,755,1780,235,'INTEGRITY RULE','Never alter source values or remove context that changes meaning. Keep crop coordinates and highlight layers separately.',GOLD,32)
 elif k==8:
  s.panel(70,235,1780,145,'EVALUATION IDENTITY','Benchmark version / evaluator / exact model / run date',CYAN,30)
  s.table(70,420,1780,['CONFIGURATION','REPRODUCIBILITY RECORD'],[['Inputs and system prompt','Saved exact inputs / hash'],['Tools and inference','Recorded tools / budgets / settings'],['Attempts and selection','Recorded repetition and selection policy'],['Scoring and sample','Recorded rubric / denominator / uncertainty']],widths=[620,1160],row_h=111)
 elif k==9:
  s.panel(70,235,875,380,'SOURCE A','Exact claim / date\nSource passage\nMethod or authority',CYAN,31);s.panel(975,235,875,380,'SOURCE B','Exact claim / date\nSource passage\nMethod or authority',GOLD,31)
  s.panel(70,655,1780,340,'RESOLUTION OR UNRESOLVED CONFLICT','Explain differences in date, version, scope, or setup. If evidence does not resolve the conflict, preserve the uncertainty.',GOLD,33)
 elif k==10:
  s.table(70,235,1780,['REUSE FIELD','REQUIRED RECORD'],[['Origin and creator','Original page / creator name'],['License or permission','Exact license / permission evidence'],['Attribution requirement','Required text and links'],['Restrictions','Commercial / modification / trademark conditions'],['Approval status','Confirmed / restricted / unknown']],widths=[620,1160],row_h=106)
 elif k==11:
  for j,(lab,bod) in enumerate([('ORIGINAL EVIDENCE','Saved snapshot / date / hash'),('REVISED EVIDENCE','Current snapshot / date / hash'),('AFFECTED CLAIMS','Claim IDs / scenes / index entries')]):s.panel(70+j*600,235,580,520,lab,bod,CYAN if j!=1 else GOLD,30)
  s.panel(70,790,1780,200,'CORRECTION RECORD','Reason / exact replacement / date / dependent outputs regenerated',GOLD,29)
 elif k==12:
  s.image_slot(70,235,925,630,'EXACT PAGE OR ELEMENT CAPTURE');s.panel(1035,235,815,630,'INTEGRITY CHECKS','Correct source and page\nVisible values preserved\nUnits and labels visible\nRelevant context retained\nNo private credentials\nCapture date recorded\nOriginal saved intact',GOLD,27)
  s.note(70,908,1780,'Use a source-faithful crop; separate screenshot evidence from explanatory editorial graphics.')
 elif k==13:
  s.panel(70,235,1780,275,'ORIGINAL SHOW ASSET','Title / purpose / creator / original source file',CYAN,36)
  s.panel(70,550,875,330,'LICENSE','CC BY 4.0\nAI Update Sources\nRecord modifications when reused',GOLD,32);s.panel(975,550,875,330,'ASSET IDENTITY','Asset ID / file hash\nEditable source\nProduction use tags',CYAN,32)
  s.note(70,925,1780,'Original asset licensing does not extend to third-party screenshots, trademarks, or imported media.')
 else:
  for j,(lab,bod) in enumerate([('FACTS SUPPORTED','Claim-linked evidence'),('PRICES CURRENT','Official billing checked'),('COMPARISONS FAIR','Conditions and limits saved'),('OUTPUTS GENUINE','Actual products preserved'),('REUSE PERMITTED','Asset rights recorded'),('TIMING VERIFIED','Narration and cues reviewed')]):s.panel(70+(j%3)*600,235+(j//3)*350,580,315,lab,bod,CYAN if j%2==0 else GOLD,30)
 save(s,'provenance',title,usage,['citation','integrity','reproducibility'])

# 15 cost-specific layouts.
costs=[
('Input and output token billing','Separate API input and output rates and actual billed usage.'),('Measured task cost equation','Explain the full task bill using saved usage and current official rates.'),('Dollar and percentage savings','Calculate savings against an explicitly named comparable baseline.'),('Retries and failed-attempt costs','Include failed attempts in the total task spending.'),('Prompt cache cost explanation','Separate cache eligibility, reported usage, and verified savings.'),('Batch pricing explanation','Explain batch rates, completion constraints, and per-item results.'),('Reasoning token accounting','Display provider-documented reasoning billing and observed usage.'),('Tool and search charges','Add provider tool charges to model token cost.'),('Subscription versus API pricing','Keep subscription entitlement and API task costs separate.'),('Billing reconciliation','Reconcile local records against the official usage dashboard.'),('Cost per successful task','Include total spending and verified successful products.'),('Long-context task spending','Explain how shared input length changes workload cost.'),('Currency and effective date','Record price currency, taxes where relevant, and effective dates.'),('Provider and regional cost basis','Separate the same model’s provider, region, and pricing conditions.'),('Price audit and correction','Verify published prices and update every dependent calculation.')]
for k,(title,usage) in enumerate(costs):
 s=SVG(title,'cost explanation','Use official rates and observed billing; mark estimates explicitly and keep currencies and units visible.')
 if k==0:
  s.panel(70,235,875,455,'INPUT SIDE','Actual input tokens\nUncached / cached distinction\nOfficial rate per million\nProvider and date',CYAN,32);s.panel(975,235,875,455,'OUTPUT SIDE','Actual output tokens\nReasoning billing rules\nOfficial rate per million\nProvider and date',GOLD,32)
  s.panel(70,730,1780,260,'TOTAL TASK COST','Include documented tools, retries, and other charges. Store the canonical calculation once.',CYAN,34)
 elif k==1:
  for j,(lab,bod) in enumerate([('MODEL TOKENS','Billed input + output + reasoning'),('TOOLS AND ATTEMPTS','Search / tools / failed attempts'),('TOTAL TASK BILL','Saved canonical calculation')]):s.panel(70+j*600,235,580,400,lab,bod,CYAN if j!=1 else GOLD,30)
  s.panel(70,680,1780,300,'REPRODUCIBLE ACCOUNTING','Link actual usage, applicable official rates, calculation version, and the exact task record.',GOLD,34)
 elif k==2:
  s.panel(70,235,875,270,'NAMED BASELINE','Exact model / task / total cost',CYAN,34);s.panel(975,235,875,270,'CHEAPER OPTION','Same requirements / observed result / total cost',GOLD,31)
  s.panel(70,545,1780,210,'DOLLAR SAVINGS','Baseline cost − alternative cost',CYAN,38);s.panel(70,795,1780,190,'PERCENTAGE SAVINGS','Dollar savings ÷ positive baseline cost × 100',GOLD,33)
 elif k==3:
  s.table(70,235,1780,['ATTEMPT','OBSERVED OUTCOME','BILLED USAGE','TASK COST'],[['First pass','Saved result / check','Actual usage','Calculated cost'],['Retry','Saved result / check','Actual usage','Calculated cost'],['Additional attempt','Saved result / check','Actual usage','Calculated cost'],['Total','Final verified success','All attempts','Total spending']],widths=[330,610,440,400],row_h=145)
 elif k==4:
  s.panel(70,235,550,610,'ELIGIBILITY','Provider cache rules\nPrefix requirements\nLifetime and pricing\nDocumented limitations',GOLD,30)
  s.panel(660,235,1190,275,'OBSERVED CACHE USAGE','Use reported cached-token counts; do not assume every repeated input was cached.',CYAN,33)
  s.panel(660,555,1190,290,'VERIFIED SPENDING','Actual cached and uncached billing with the same saved workload.',GOLD,33)
  s.note(70,897,1780,'A published discount is not proof of realized savings on the tested task.')
 elif k==5:
  for j,(lab,bod) in enumerate([('BATCH SETUP','Exact items / endpoint / completion window'),('ITEM OUTCOMES','Actual products / failures / validation'),('BILLING','Official batch rate / observed usage')]):s.panel(70+j*600,235,580,540,lab,bod,CYAN if j!=2 else GOLD,31)
  s.note(70,820,1780,'Include latency and failure handling when recommending batch processing.')
 elif k==6:
  s.panel(70,235,1780,190,'PROVIDER BILLING RULE','Record whether and how reasoning tokens are included in billable output.',GOLD,35)
  s.panel(70,465,875,400,'REQUEST SETTINGS','Exact reasoning setting\nToken limits\nAttempts and tools\nRecorded model version',CYAN,31);s.panel(975,465,875,400,'OBSERVED USAGE','Reported token categories\nTotal billed usage\nMeasured completion time\nActual task result',GOLD,31)
  s.note(70,918,1780,'Do not infer hidden reasoning-token counts from the visible answer length.')
 elif k==7:
  s.table(70,235,1780,['CHARGE COMPONENT','USAGE RECORD','PRICE BASIS'],[['Model inference','Actual billed token categories','Official rates'],['Search or browsing','Actual reported tool use','Official tool price'],['Other cloud tools','Actual chargeable actions','Official billing rule'],['Retries and selection','All billable attempts','Saved calculation']],widths=[550,680,550],row_h=145)
 elif k==8:
  s.panel(70,235,875,605,'SUBSCRIPTION','Monthly plan price\nIncluded features and usage\nLimits and availability\nDo not infer exact per-task cost',GOLD,32)
  s.panel(975,235,875,605,'API','Usage-based rates\nExact model endpoint\nActual billable categories\nMeasured or estimated task cost',CYAN,32)
  s.note(70,889,1780,'Compare within a stated pricing basis; these are different purchase and usage models.')
 elif k==9:
  s.panel(70,235,875,480,'TASK RECORDS','Request IDs\nToken and tool usage\nRates applied\nLocal calculated spending',CYAN,32)
  s.panel(975,235,875,480,'OFFICIAL USAGE','Reporting window\nProvider totals\nBilling adjustments\nActual charged spending',GOLD,32)
  s.panel(70,755,1780,235,'RECONCILIATION','Explain mismatches and reporting delays before labeling a calculation as measured billing.',GOLD,32)
 elif k==10:
  s.panel(70,235,650,640,'ALL TASK SPENDING','Inference\nFailed attempts\nRetries\nTool charges\nSelection charges',GOLD,32)
  s.panel(760,235,1090,285,'VERIFIED SUCCESS COUNT','Use predeclared checks. Record incomplete or failed products separately.',CYAN,34)
  s.panel(760,560,1090,315,'COST PER SUCCESS','Total task spending ÷ verified successful tasks\n\nUndefined when no tasks succeed.',GOLD,31)
 elif k==11:
  s.panel(70,235,1780,150,'SHARED INPUT','Exact document set / tokenization method / context handling / caching status',GOLD,30)
  for j,label in enumerate(['MODEL A WORKLOAD','MODEL B WORKLOAD']):s.panel(70+j*905,425,875,420,label,'Actual accepted input usage\nActual generated output usage\nTools and preprocessing\nTotal task bill',CYAN,32)
  s.note(70,893,1780,'Different tokenizers and preprocessing can change usage even when the source documents are identical.')
 elif k==12:
  s.table(70,235,1780,['PRICE FIELD','REQUIRED VALUE','SOURCE'],[['Currency','Published currency','Official page'],['Effective date','Rate applicability date','Official notice'],['Units','Per token / task / month','Official documentation'],['Taxes / fees','Applicable or excluded','Documented basis'],['Verification date','When checked','Saved record']],widths=[430,740,610],row_h=109)
 elif k==13:
  s.panel(70,235,1780,155,'EXACT MODEL DOES NOT FULLY DEFINE COST','Record the serving provider, region, plan, and endpoint.',GOLD,33)
  s.table(70,430,1780,['SERVICE','CONDITIONS','RATE SOURCE'],[['Provider A / exact endpoint','Region / plan / billing rule','Official price + date'],['Provider B / exact endpoint','Region / plan / billing rule','Official price + date'],['Provider C / exact endpoint','Region / plan / billing rule','Official price + date']],widths=[620,670,490],row_h=145)
 else:
  for j,(lab,bod) in enumerate([('OFFICIAL PRICE','Current page / date / units'),('CANONICAL CALCULATION','Saved actual usage × applicable rates'),('DEPENDENT OUTPUTS','Graphics / script / index / verdict')]):s.panel(70+j*600,235,580,520,lab,bod,CYAN if j!=1 else GOLD,30)
  s.arrow(650,480,665,480);s.arrow(1250,480,1265,480);s.panel(70,795,1780,200,'CORRECTION RULE','Preserve prior values, document the change, and regenerate every affected output.',GOLD,30)
 save(s,'cost-explanation',title,usage,['pricing','billing','value','canonical-data'])

assert len(records)==180,len(records)
assert len(list(OUT.glob('*.svg')))==180
assert len({r['sha256'] for r in records})==180
(ROOT/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'README.md').write_text('''# Evidence-first comparison production templates\n\n180 original editable SVG assets, designed for 1920 × 1080 cloud-AI episodes.\n\nAll files are templates. No factual model scores, prices, outcomes, official logos, or screenshots are embedded. Replace placeholders with verified evidence. A benchmark score and a single task product must not be treated as interchangeable measures.\n\nCategories: 30 comparison panels; 30 benchmark explainers; 30 verdicts; 30 change reports; 30 feature tutorials; 15 provenance layouts; 15 cost explanations.\n\n## License\nCC BY 4.0. Recommended attribution: **AI Update Sources**. This license covers original SVG artwork only. Third-party screenshots, logos, and inserted media keep their own applicable rights.\n\n## Regenerate\nRun `python generate.py`. Metadata and SHA-256 checksums are written to `manifest.json`.\n\nSVG text, cards, arrows, and source-image slots remain editable. Use actual products and real screenshots when completing an episode.\n''',encoding='utf-8')
print(json.dumps({'asset_count':len(records),'categories':{c:sum(r['tags'][3]==c for r in records) for c in sorted({r['tags'][3] for r in records})},'manifest':str(ROOT/'manifest.json')},indent=2))
