"""Task-specific compositions: avoid repeating generic layouts with only new labels."""
CYAN='#63dcec'; GOLD='#efc26d'; WHITE='#f4f8fc'; MUTED='#abc0cf'; LINE='#294456'; NAVY='#081421'; CARD='#112637'

def distinct_benchmark(s,k,title,SVG):
 if k!=25:return s
 s=SVG(title,'benchmark explainer','Schematic only: replace the bands with sourced estimates and uncertainty.')
 s.panel(70,235,1780,180,'OBSERVED OVERLAP','Published or reproducibly calculated uncertainty may overlap; do not force a unique winner.',GOLD,33)
 s.rect(70,450,1130,350,CARD,LINE);s.txt(100,499,'SCHEMATIC / NO MEASURED VALUES',23,CYAN,weight='700')
 s.rect(635,535,145,170,NAVY,LINE,r=4)
 s.line(230,570,780,570,CYAN,9);s.circle(520,570,13,WHITE);s.txt(100,574,'A',27,WHITE)
 s.line(635,665,1080,665,GOLD,9);s.circle(850,665,13,WHITE);s.txt(100,669,'B',27,WHITE)
 s.txt(525,766,'Insert exact estimates, interval method, and sample.',22,MUTED)
 s.panel(1240,450,610,350,'CLAIM LIMIT','No clear difference\n≠ proven equivalence\n\nUse a predeclared equivalence test if claiming equivalence.',GOLD,26)
 s.note(70,852,1780,'Disclose interval type and estimator; interval overlap alone is not a complete hypothesis test.')
 return s

def distinct_verdict(s,k,title,SVG):
 indices={1,8,19,26,11,12,21,9,10,6,16,13}
 if k not in indices:return s
 s=SVG(title,'verdict','Use saved task products, exact models, costs, and qualified evidence for the conclusion.')
 if k==1:
  s.table(70,235,1780,['TESTED OPTION','REQUIREMENTS MET?','TOTAL TASK COST'],[['Exact model A','Verified rubric result','Actual billed cost'],['Exact model B','Verified rubric result','Actual billed cost'],['Exact model C','Verified rubric result','Actual billed cost']],widths=[660,630,490],row_h=132)
  s.panel(70,805,1780,190,'LOWEST-COST QUALIFYING CHOICE','Insert the qualifying option with the lowest total observed cost; disclose task and sample limits.',GOLD,31)
 elif k==8:
  s.image_slot(70,235,1140,560,'ACTUAL BEST OBSERVED PRODUCT / UNEDITED')
  s.panel(1250,235,600,560,'OBSERVED EVIDENCE','Exact model and provider\nPredeclared rubric\nAll tested outputs\nTask cost\nBenchmark source',GOLD,27)
  s.panel(70,835,1780,150,'CLAIM SCOPE','Best observed in this task sample; broader superiority is not established.',CYAN,29)
 elif k==19:
  s.panel(570,235,780,245,'NARROW TASK STRENGTH','Exact model / specialist task / observed product',CYAN,34)
  s.panel(70,525,530,345,'SUPPORT','Relevant benchmark\nActual output\nObjective check',GOLD,30)
  s.panel(640,525,640,345,'ECONOMICS','Total measured cost\nAlternative task result\nSupported value claim',CYAN,30)
  s.panel(1320,525,530,345,'BOUNDARY','Untested tasks\nAccess restrictions\nKnown limitations',GOLD,30)
  s.note(70,920,1780,'A task-specific strength does not establish a universal best model.')
 elif k==26:
  s.panel(210,235,1500,285,'USE THIS / FOR THIS TASK','Exact cloud model + task + verified date',CYAN,45)
  s.panel(210,560,730,245,'COST','Measured task bill\nNamed cheaper alternative',GOLD,33)
  s.panel(980,560,730,245,'WHY','Decisive product evidence\nRelevant benchmark context',CYAN,31)
  s.note(210,865,1500,'LIMITATION: state the most important boundary on this recommendation.')
 elif k==11:
  s.panel(70,235,1780,180,'TASK SUCCESS COMES FIRST','Record minimum requirements and the maximum acceptable task spending.',GOLD,33)
  s.panel(70,465,520,355,'LOWER-COST OPTION','Actual result\nQualifies?\nTotal cost',CYAN,32)
  s.panel(700,465,520,355,'UPGRADE OPTION','Actual result\nQualifies?\nTotal cost',GOLD,32)
  s.panel(1330,465,520,355,'DECISION','Pick the lowest-cost option meeting the requirement.',CYAN,31)
  s.arrow(605,635,680,635);s.arrow(1235,635,1310,635)
  s.note(70,875,1780,'Do not impose a spending ceiling as a quality requirement; record the actual tradeoff.')
 elif k==12:
  s.panel(70,235,620,635,'PREDECLARED THRESHOLD','Required accuracy\nRequired format\nRequired evidence\nPermitted failures\nTask scope',GOLD,30)
  s.table(730,235,1120,['OPTION','CHECK RESULTS','QUALIFIES?'],[['Exact model A','Saved verification','Verified result'],['Exact model B','Saved verification','Verified result'],['Exact model C','Saved verification','Verified result']],widths=[350,460,310],row_h=135)
  s.note(70,920,1780,'Set the threshold before reviewing outputs and preserve all failed checks.')
 elif k==21:
  s.panel(70,235,1780,170,'RISK TOLERANCE / TASK CONSEQUENCE','State the actual consequence of a wrong or incomplete output.',GOLD,32)
  s.table(70,445,1780,['OPTION','FAILURE EVIDENCE','TASK COST','FIT'],[['Exact model A','Observed errors / sample','Total spending','Task-specific decision'],['Exact model B','Observed errors / sample','Total spending','Task-specific decision']],widths=[400,670,350,360],row_h=150)
  s.panel(70,930,1780,65,'DECISION RECORD','',CYAN)
  s.txt(440,971,'Choose within the stated risk and quality requirements.',24,WHITE)
 elif k==9:
  s.panel(70,235,1780,170,'WHAT WAS OBSERVED','Similar outcomes in the saved task sample.',CYAN,36)
  s.panel(70,450,550,345,'OBSERVATION','Recorded model versions\nTask and rubric\nRepetition count',CYAN,30)
  s.panel(670,450,550,345,'LIMITATION','Sample uncertainty\nDifferent unseen tasks\nUntested conditions',GOLD,30)
  s.panel(1270,450,580,345,'ALLOWED CLAIM','Comparable observed outcomes under these conditions.',CYAN,32)
  s.arrow(635,620,655,620);s.arrow(1235,620,1255,620)
  s.note(70,852,1780,'Do not claim equivalence without an appropriate predeclared test and supporting sample.')
 elif k==10:
  s.table(70,235,1780,['TASK','EXACT SERVICE','OBSERVED PRODUCT','COST','CAVEAT'],[['Writing task','Verified identity','Saved output / rubric','Billed task','Scope'],['Code task','Verified identity','Executed checks','Billed task','Scope'],['Research task','Verified identity','Citations checked','Billed task','Scope'],['Document task','Verified identity','Passages verified','Billed task','Scope']],widths=[300,420,500,260,300],row_h=140)
  s.note(70,964,1780,'Every recommendation links to dated evidence; keep superseded findings visible as history.')
 elif k==6:
  s.panel(70,235,1780,230,'NO DEFENSIBLE RANKING YET','Specify the missing evidence that prevents a fair comparison.',GOLD,38)
  s.panel(70,505,875,390,'MISSING INPUTS','Comparable benchmark setup\nActual task outputs\nCurrent official prices\nModel identity / access',CYAN,31)
  s.panel(975,505,875,390,'NEXT USEFUL ACTION','Collect the missing source or test\nPreserve unresolved conflicts\nAvoid invented products\nUpdate after verification',GOLD,29)
 elif k==16:
  s.panel(70,235,760,610,'EVIDENCE ORIGINS','Official source\nIndependent evaluator\nOriginal show task\nConflicting or missing evidence',GOLD,31)
  s.panel(870,235,980,285,'SUPPORTED CLAIM','Record the precise conclusion that evidence supports.',CYAN,36)
  s.panel(870,560,980,285,'CONFIDENCE LIMIT','Explain provenance, sample, comparability, and unresolved gaps without inventing a confidence percentage.',GOLD,30)
  s.note(70,910,1780,'Confidence describes support for the claim; it is not a model benchmark score.')
 elif k==13:
  s.panel(70,235,1780,190,'AVOID / ONLY FOR THIS SPECIFIC TASK','Exact service / observed failure / task boundary',GOLD,35)
  s.image_slot(70,465,800,390,'ACTUAL FAILURE EXCERPT / VALIDATION')
  s.panel(910,465,940,190,'SUPPORTED ALTERNATIVE','Exact tested option and qualifying evidence.',CYAN,31)
  s.panel(910,695,940,160,'WHAT WOULD CHANGE THIS','A relevant retest, fix, or confirmed feature update.',GOLD,27)
  s.note(70,916,1780,'Preserve all source and product records; this is not a general warning about the company.')
 return s

def distinct_change(s,k,title,fields,SVG):
 if k<10:return s
 s=SVG(title,'change report','Only source-backed previous/current facts are permitted; distinguish availability from testing.')
 if k==10:
  s.panel(70,235,1780,170,'ROUTING CHANGE','Official provider notice / exact affected service / effective date',GOLD,33)
  s.panel(70,445,560,360,'BEFORE','Saved routing policy\nModel identity certainty',CYAN,30)
  s.panel(690,445,560,360,'AFTER','Verified routing policy\nPinned version available?',GOLD,30)
  s.panel(1310,445,540,360,'COMPARISON EFFECT','Retest service behavior\nDo not invent model identity',CYAN,29)
  s.arrow(645,620,675,620);s.arrow(1265,620,1295,620)
  s.note(70,863,1780,'A routed service result may not be attributable to a single fixed model version.')
 elif k==11:
  for j,label in enumerate(['CHANGE ENTRY','CHANGE ENTRY','CHANGE ENTRY']):
   y=235+j*230;s.panel(70,y,450,190,'OFFICIAL SOURCE','Exact title / URL / date',GOLD,27);s.panel(550,y,800,190,label,'Exact relevant passage',CYAN,31);s.panel(1380,y,470,190,'VIEWER IMPACT','Practical consequence',GOLD,27)
 elif k==12:
  s.table(70,235,1780,['METHODOLOGY FIELD','PREVIOUS','REVISED'],[['Metric definition','Saved definition','Current definition'],['Attempt budget','Saved setup','Current setup'],['Tools and scoring','Saved procedure','Current procedure']],widths=[520,630,630],row_h=150)
  s.panel(70,875,1780,120,'COMPARABILITY VERDICT','Explain whether historical scores can still be compared.',GOLD,26)
 elif k==13:
  s.panel(70,235,875,300,'PREVIOUS PUBLISHED RESULT','Saved exact metric / version / source date',CYAN,32)
  s.panel(975,235,875,300,'REVISED PUBLISHED RESULT','Updated exact metric / version / source date',GOLD,32)
  s.image_slot(70,575,760,400,'SOURCE EXPLANATION / CAPTURE')
  s.panel(870,575,980,400,'AFFECTED CLAIMS','Record corrected claim IDs\nRevise dependent rankings\nPreserve original record\nExplain source-provided reason',CYAN,31)
 elif k==14:
  s.panel(70,235,520,690,'EVALUATOR IDENTITY','Benchmark\nHarness version\nSource\nChange date\nRescoring scope',GOLD,30)
  s.panel(630,235,1220,200,'METHOD CHANGE','What the evaluator changed, exactly.',CYAN,34)
  s.panel(630,475,1220,200,'SCORE IMPACT','Published or reproducibly recalculated effect.',GOLD,33)
  s.panel(630,715,1220,210,'CLAIM LIMIT','Evaluator changes do not establish that the model itself improved.',CYAN,32)
 elif k==15:
  s.table(70,235,1780,['ACCESS FIELD','SAVED STATE','CURRENT VERIFIED STATE'],[['Region','Saved supported regions','Current supported regions'],['Account / plan','Saved eligibility','Current eligibility'],['Feature rollout','Saved access state','Current access state'],['Cloud endpoint','Saved endpoint','Current endpoint']],widths=[420,660,700],row_h=130)
  s.note(70,917,1780,'Do not use national flags as proof of cloud availability; cite actual service documentation.')
 elif k==16:
  s.panel(70,235,1780,170,'PLAN CHANGE / EFFECTIVE DATE','Official plan page / currency / eligibility / update date',GOLD,33)
  s.table(70,445,1780,['ENTITLEMENT','PREVIOUS PLAN','CURRENT PLAN'],[['Included model access','Saved plan terms','Current plan terms'],['Feature and usage limits','Saved plan terms','Current plan terms'],['Monthly subscription','Saved price basis','Current price basis']],widths=[590,595,595],row_h=135)
  s.note(70,937,1780,'Subscription changes do not automatically change API token rates.')
 elif k==17:
  s.panel(70,235,840,370,'PREVIOUS ENDPOINT','Exact API identifier\nSaved version\nCompatibility record',CYAN,32)
  s.panel(1010,235,840,370,'CURRENT ENDPOINT','Exact API identifier\nDocumented replacement\nTested request behavior',GOLD,32)
  s.arrow(930,415,990,415)
  s.panel(70,645,1780,300,'MIGRATION CHECK','Request schema / response format / authentication / billing / tool support / pinned model identity',CYAN,32)
 elif k==18:
  s.table(70,235,1780,['BILLING CATEGORY','OLD RULE','NEW RULE'],[['Input / output tokens','Saved rate and units','Current rate and units'],['Reasoning tokens','Saved billing rule','Current billing rule'],['Cache / batch','Saved eligibility and price','Current eligibility and price'],['Tools and search','Saved charge basis','Current charge basis']],widths=[560,610,610],row_h=134)
  s.panel(70,942,1780,53,'RECALCULATE THE SAME WORKLOAD / PRESERVE THE ORIGINAL USAGE RECORD','',GOLD)
 elif k==19:
  s.panel(70,235,1780,185,'DOCUMENTED OUTPUT LIMIT CHANGE','Exact model / cloud provider / old limit / new limit / source date',GOLD,32)
  s.panel(70,460,700,430,'TASK PRODUCT','Actual response\nObserved truncation\nRequested format\nBilled output usage',CYAN,31)
  s.panel(810,460,1040,430,'WHAT THE LIMIT DOES NOT PROVE','Long-form accuracy\nInstruction consistency\nFull-length reliability\nSuccess on untested tasks',GOLD,32)
 elif k==20:
  s.image_slot(70,235,710,450,'NEW REASONING CONTROL / ACTUAL UI')
  s.panel(820,235,1030,210,'AVAILABLE SETTINGS','Official setting names / limits / access plan',GOLD,32)
  s.panel(820,485,1030,200,'TESTED BEHAVIOR','Same prompt / actual product / saved settings',CYAN,30)
  s.table(70,725,1780,['SETTING','ACTUAL TASK RESULT','BILLING / TIME'],[['Recorded setting A','Saved product / rubric','Actual usage / timing'],['Recorded setting B','Saved product / rubric','Actual usage / timing']],row_h=85)
 elif k==21:
  s.image_slot(70,235,875,460,'PREVIOUS CITATION PRESENTATION');s.image_slot(975,235,875,460,'CURRENT CITATION PRESENTATION')
  for j,label in enumerate(['LINK EXISTS','PASSAGE SUPPORTS CLAIM','DATE AND SCOPE APPLY']):s.panel(70+j*600,735,580,225,label,'Record actual source verification.',GOLD if j==1 else CYAN,26)
 elif k==22:
  s.panel(70,235,1780,145,'MEMORY CHANGE','Official control or behavior change / update date',GOLD,32)
  s.panel(70,420,550,450,'USER CONTROLS','View\nEdit\nRemove\nDisable\nPermission scope',CYAN,32)
  s.panel(660,420,580,450,'ACTUAL BEHAVIOR','Saved user setting\nObserved recall\nCross-session conditions\nKnown limitations',GOLD,30)
  s.panel(1280,420,570,450,'USER CONSEQUENCE','Useful retained context\nPrivacy implications\nHow to test and correct',CYAN,30)
 elif k==23:
  s.panel(70,235,580,625,'NEW CONNECTOR','Exact identity\nCloud availability\nOfficial source\nAccess conditions',CYAN,31)
  s.panel(690,235,560,625,'PERMISSION','Granted data scope\nAuthentication method\nRead/write boundary\nRevocation control',GOLD,30)
  s.panel(1290,235,560,625,'ACTUAL RESULT','Retrieved evidence\nSource trace\nTask product\nObserved limitation',CYAN,30)
  s.note(70,907,1780,'Never expose connected private data or account tokens in an episode capture.')
 elif k==24:
  s.image_slot(70,235,1180,505,'ACTUAL GENERATED ARTIFACT / USABLE PRODUCT')
  s.panel(1290,235,560,505,'NEW CAPABILITY','Feature controls\nSupported export\nPlan and rollout\nVerified usability',GOLD,30)
  s.panel(70,780,1780,205,'USER WORKFLOW','Exact input → new feature → inspected product → tested export',CYAN,32)
 elif k==25:
  s.panel(70,235,875,320,'BEFORE / ERROR RECORD','Saved request\nActual error\nRetry behavior\nTotal charges',GOLD,31)
  s.panel(975,235,875,320,'AFTER / OBSERVED BEHAVIOR','Same reproduction setup\nActual response\nRetry behavior\nTotal charges',CYAN,29)
  s.panel(70,600,1780,365,'FIX VALIDATION','Link the official change to the reproduced behavior. State which error cases were tested and which remain unverified.',GOLD,34)
 elif k==26:
  s.panel(70,235,570,675,'CHANGED SOURCE','URL\nOriginal snapshot\nCurrent snapshot\nSource update date',GOLD,31)
  for j,label in enumerate(['AFFECTED CLAIMS','DEPENDENT VISUALS','REVISED CONCLUSIONS']):s.panel(680,235+j*230,1170,195,label,'IDs / exact change / saved correction evidence',CYAN if j!=1 else GOLD,29)
 elif k==27:
  s.panel(70,235,1780,190,'ACCESS STATUS','Exact service / verified notice / affected accounts / observation date',GOLD,33)
  s.panel(70,465,760,400,'USER IMPACT','Unavailable model or feature\nSaved workflow affected\nOfficial migration instructions',CYAN,32)
  s.panel(870,465,980,400,'SUPPORTED ALTERNATIVE','Verified available option\nComparable task evidence\nNew cost basis\nAccess limitations',GOLD,31)
  s.note(70,920,1780,'Loss of access is distinct from model quality and official retirement.')
 elif k==28:
  s.panel(70,235,1780,160,'OFFICIAL DEFECT NOTICE','Exact issue / affected versions / source / fix release',GOLD,33)
  s.panel(70,435,575,400,'REPRODUCTION','Saved trigger\nPrior actual behavior\nExpected result',CYAN,31)
  s.panel(675,435,575,400,'FIX TEST','Same trigger\nCurrent actual behavior\nExecuted checks',GOLD,31)
  s.panel(1280,435,570,400,'VERDICT','Observed outcome\nTest scope\nRemaining uncertainty',CYAN,31)
  s.note(70,891,1780,'An official fix announcement and a reproduced successful test are separate pieces of evidence.')
 else:
  s.panel(70,235,1780,180,'CORRECTION / EXACT REPLACEMENT STATEMENT','State the corrected fact clearly before explaining the history.',GOLD,34)
  s.panel(70,455,875,370,'ORIGINAL RECORD','Episode / timestamp\nExact earlier statement\nSupporting record\nReason it was wrong or stale',CYAN,30)
  s.panel(975,455,875,370,'NEW EVIDENCE','Current source and date\nSupported replacement\nImpacted recommendation\nUpdated index record',GOLD,30)
  s.note(70,879,1780,'Preserve the earlier version and make the correction visible wherever the old claim is reused.')
 return s

def distinct_feature(s,k,title,steps,SVG):
 if k<10:return s
 s=SVG(title,'platform how-to','Current official controls, access conditions, actual UI captures, and verified product required.')
 if k==10:
  s.image_slot(70,235,850,460,'ACTUAL SAVED MEMORY CONTROLS')
  s.panel(960,235,890,200,'REVIEW / CHANGE',steps[0]+'\n'+steps[1],GOLD,31)
  s.panel(960,475,890,220,'VERIFY / CORRECT',steps[2]+'\n'+steps[3],CYAN,31)
  s.panel(70,735,1780,250,'CONTROL BOUNDARY','Show what is retained, how the user controls it, and observed recall. Do not assume every platform remembers the same information.',GOLD,30)
 elif k==11:
  s.panel(70,235,470,610,'USER CONTROLS','Start\nPause / resume\nInterrupt\nMute\nEnd session',CYAN,34)
  s.image_slot(580,235,820,360,'ACTUAL VOICE INTERFACE')
  s.panel(1440,235,410,610,'TRANSCRIPT CHECK','Recognition errors\nUnsupported answers\nSaved useful product',GOLD,27)
  s.panel(580,635,820,210,'VERIFY THE PRODUCT',steps[2]+'\n'+steps[3],CYAN,29)
  s.note(70,910,1780,'Availability, turn-taking, and voice controls must be verified on the actual cloud service.')
 elif k==12:
  s.panel(70,235,1780,140,'IMAGE BRIEF','Purpose / subject / composition / dimensions / export requirements',GOLD,32)
  s.image_slot(70,415,860,400,'ACTUAL INITIAL CLOUD IMAGE')
  s.image_slot(990,415,860,400,'ACTUAL REVISED CLOUD IMAGE')
  s.arrow(950,610,970,610)
  s.panel(70,855,1780,140,'REVIEW AND EXPORT','Inspect text, details, and suitability; keep image generation separate from exact data graphics.',CYAN,27)
 elif k==13:
  s.image_slot(70,235,910,610,'EXACT VISUAL INPUT / EVIDENCE')
  s.panel(1020,235,830,220,'BOUNDED QUESTION',steps[1]+'\nRecord the exact image and prompt.',GOLD,29)
  s.panel(1020,495,830,350,'VERIFICATION','Point to visible evidence\nCheck OCR and spatial claims\nRecord uncertain inferences\nPreserve original response',CYAN,31)
  s.note(70,907,1780,'A confident model description is not proof that a feature is visible in the image.')
 elif k==14:
  s.panel(70,235,570,580,'DOCUMENT BRIEF','Purpose and audience\nRequired structure\nVerified content\nEditable export\nAccessibility checks',GOLD,30)
  s.image_slot(680,235,550,580,'EDITABLE DOCUMENT / ACTUAL PRODUCT')
  s.image_slot(1270,235,580,580,'RENDERED DOCUMENT / LAYOUT CHECK')
  s.panel(70,855,1780,140,'FINAL REVIEW','Check facts, spacing, page breaks, links, and the actual exported file.',CYAN,28)
 elif k==15:
  s.image_slot(70,235,560,420,'ACTUAL INPUT DATASET')
  s.panel(670,235,570,420,'REPRODUCIBLE ANALYSIS','Saved code or formulas\nUnits and assumptions\nCalculated results\nIndependent spot checks',CYAN,30)
  s.image_slot(1280,235,570,420,'VERIFIED RESULT / CHART')
  s.arrow(640,445,655,445);s.arrow(1250,445,1265,445)
  s.panel(70,695,1780,280,'VERIFY BEFORE EXPORT','Check source data, calculations, labels, axes, and conclusions. Save the actual analysis and useful exported artifact.',GOLD,33)
 elif k==16:
  s.panel(70,235,1780,150,'ARTIFACT SPECIFICATION','Intended use / user inputs / observable outputs / acceptance checks',GOLD,31)
  s.image_slot(70,425,1000,540,'ACTUAL CLOUD ARTIFACT / INTERACTIVE PRODUCT')
  s.panel(1110,425,740,245,'BEHAVIOR CHECKS','Run representative inputs\nCheck error and empty states\nInspect real outputs',CYAN,28)
  s.panel(1110,710,740,255,'REUSE RECORD','Save source and export\nRecord platform dependencies\nDocument limitations',GOLD,29)
 elif k==17:
  s.panel(70,235,560,625,'SAME TASK','Exact prompt\nIdentical inputs\nPredeclared rubric\nExact cloud model',GOLD,31)
  s.table(670,235,1180,['SETTING','PRODUCT','USAGE / TIME'],[['Recorded A','Actual output / checks','Billed usage / measured time'],['Recorded B','Actual output / checks','Billed usage / measured time'],['Recorded C','Actual output / checks','Billed usage / measured time']],widths=[330,390,460],row_h=145)
  s.note(70,907,1780,'Choose a setting from actual task quality and cost; do not assume more reasoning always helps.')
 elif k==18:
  s.panel(70,235,1780,150,'EXACT BATCH INPUTS','Saved per-item prompts / endpoint / model version / item identifiers',GOLD,30)
  for j,label in enumerate(['SUBMIT','MONITOR','VALIDATE','RECONCILE']):
   s.panel(70+j*450,425,430,420,label,steps[j],CYAN if j%2==0 else GOLD,30)
  s.note(70,895,1780,'Save per-item failures and the provider’s actual billed usage; record the completion window.')
 elif k==19:
  s.panel(70,235,1780,170,'REUSABLE PREFIX','Exact shared prefix / provider cache rules / supported cache duration',GOLD,32)
  s.panel(70,445,875,290,'ACTUAL REQUEST','Prefix and new task inputs\nSaved endpoint and settings\nProvider eligibility',CYAN,29)
  s.panel(975,445,875,290,'REPORTED CACHE USAGE','Actual cached token categories\nUncached token categories\nOfficial applicable rates',GOLD,29)
  s.panel(70,775,1780,210,'SAVINGS VERIFICATION','Compare actual billable usage against the stated uncached baseline; do not assume a cache hit.',CYAN,31)
 elif k==20:
  s.image_slot(70,235,1090,590,'OFFICIAL CLOUD USAGE DASHBOARD / REDACT SECRETS')
  s.panel(1200,235,650,280,'REPORTING WINDOW','Provider / account scope\nCurrency / billing categories\nStart and end dates',GOLD,29)
  s.panel(1200,555,650,270,'RECONCILIATION','Request IDs and task logs\nReporting delays\nDifferences explained',CYAN,28)
  s.note(70,885,1780,'Keep account identifiers and private billing details out of public screenshots.')
 elif k==21:
  for j,(lab,bod) in enumerate([('CREATE SCOPED ACCESS','Required permissions only'),('STORE SECURELY','Use secret storage / never a slide'),('VERIFY AUTHORIZATION','Test permitted operations'),('ROTATE OR REVOKE','Document access lifecycle')]):s.panel(70+(j%2)*905,235+(j//2)*330,875,295,lab,bod,CYAN if j%2==0 else GOLD,31)
  s.note(70,932,1780,'Use a redacted interface capture; never embed real keys, session tokens, or credentials.')
 elif k==22:
  s.panel(70,235,550,670,'DOCUMENTED LIMITS','Request window\nToken window\nConcurrency\nProvider headers\nRetry guidance',GOLD,30)
  s.panel(660,235,1190,185,'NORMAL REQUEST','Saved cloud request and observed response.',CYAN,32)
  s.panel(660,460,1190,185,'LIMIT OR ERROR RESPONSE','Actual status, headers, and error body; redact private data.',GOLD,29)
  s.panel(660,685,1190,220,'BOUNDED RECOVERY','Documented backoff / attempt cap / total charges / final outcome',CYAN,29)
 elif k==23:
  s.panel(70,235,840,360,'SOURCE PRODUCT','Actual cloud artifact\nOwner and permissions\nEditable version\nIntended audience',CYAN,31)
  s.panel(1010,235,840,360,'EXPORTED PRODUCT','Actual saved format\nLayout and content checked\nPermission scope\nVersion identity',GOLD,30)
  s.arrow(930,405,990,405)
  s.panel(70,635,1780,340,'SHARE ONLY THE INTENDED VERSION','Inspect links, embedded media, and public visibility. Verify that recipients see the correct product and permission level.',CYAN,34)
 elif k==24:
  s.table(70,235,1780,['VERSION RECORD','SAVED BASELINE','UPDATE CHECK'],[['Exact model ID','Pinned endpoint / date','Documented replacement'],['Inference and tools','Saved settings','Changed settings disclosed'],['Task products','Saved prompt / output','Same task retested'],['Cost and recommendations','Saved rate / usage','Recalculated current result']],widths=[480,650,650],row_h=130)
  s.note(70,918,1780,'Do not replace version-specific records with a moving marketing family name.')
 elif k==25:
  s.panel(70,235,1780,150,'TEAM WORKSPACE BOUNDARY','Roles / shared context / data permissions / review responsibility',GOLD,30)
  s.panel(70,425,530,450,'SETUP','Required access only\nScoped reference files\nCurrent instructions',CYAN,31)
  s.panel(640,425,640,450,'COLLABORATIVE PRODUCT','Actual shared artifact\nVersion and ownership\nReview comments\nAccepted corrections',GOLD,30)
  s.panel(1320,425,530,450,'MAINTAIN','Remove obsolete access\nUpdate useful references\nPreserve history',CYAN,30)
 elif k==26:
  s.panel(70,235,1780,150,'VERIFY BEFORE DEMONSTRATING','Cloud provider / account plan / service region / rollout state',GOLD,31)
  s.table(70,425,1780,['CONDITION','OFFICIAL DOCUMENTATION','OBSERVED ACCESS'],[['Model availability','Exact URL + checked date','Actual endpoint / UI'],['Feature availability','Exact rollout statement','Actual account controls'],['Usage restrictions','Official plan terms','Observed limits']],widths=[520,730,530],row_h=160)
 elif k==27:
  s.panel(70,235,570,675,'MODEL CLAIM','Exact statement\nCitation link\nAnswer date\nRequested scope',CYAN,32)
  s.panel(680,235,1170,205,'OPEN THE LINK','Source exists and is the actual cited source.',GOLD,32)
  s.panel(680,470,1170,205,'LOCATE SUPPORT','Find the passage that supports the precise claim.',CYAN,32)
  s.panel(680,705,1170,205,'CHECK APPLICABILITY','Date, units, limitations, and contradictions match the statement.',GOLD,30)
 elif k==28:
  s.image_slot(90,235,440,710,'ACTUAL MOBILE CLOUD UI')
  s.panel(570,235,1280,200,'PREPARE READABLE INPUT',steps[0]+'\n'+steps[1],GOLD,30)
  s.panel(570,475,1280,200,'CHECK ON THE DEVICE',steps[2]+'\nInspect clipping, controls, and actual output.',CYAN,30)
  s.panel(570,715,1280,230,'EXPORT OR CONTINUE',steps[3]+'\nPreserve product and version across devices.',GOLD,30)
 else:
  s.panel(70,235,1780,135,'VERIFIED INPUTS','Current sources / exact task / cloud platform / success criteria',GOLD,29)
  for j,label in enumerate(['FEATURE ACTION','INTERMEDIATE PRODUCT','VERIFIED FINAL PRODUCT']):s.panel(70+j*600,410,580,375,label,steps[j+1] if j<3 else '',CYAN if j!=1 else GOLD,31)
  s.arrow(650,585,665,585);s.arrow(1250,585,1265,585)
  s.panel(70,825,1780,160,'CHECK EACH STAGE','Save the actual input, output, error, cost, and acceptance check at every consequential step.',GOLD,28)
 return s
