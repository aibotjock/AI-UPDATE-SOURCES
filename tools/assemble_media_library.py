#!/usr/bin/env python3
"""Assemble the curated asset collection; metadata/support files are not assets."""
from __future__ import annotations
import argparse, base64, collections, datetime, hashlib, html, json, math, shutil, struct, wave
from pathlib import Path
import xml.etree.ElementTree as ET

GROUPS = {
    'comparison-assets': ('graphics/panels',180),
    'technical-diagrams': ('graphics/diagrams',180),
    'background-motion': (None,200),
    'icons': ('icons/lucide',320),
    'brands': ('logos/community',40),
    'sound-effects': ('sound-effects',60),
    'evidence-labels': ('graphics/evidence-labels',20),
}

def records(path):
    data=json.loads(path.read_text())
    return data if isinstance(data,list) else data['assets']

def resolve_file(base, record):
    raw=record.get('relative_path') or record['path']
    p=Path(raw)
    candidates=[p] if p.is_absolute() else [base/p,base.parent/p]
    for p in candidates:
        if p.is_file() and p.resolve().is_relative_to(base.resolve()): return p
    raise ValueError(f'Cannot safely resolve {raw} in {base}')

def svg_check(path):
    root=ET.fromstring(path.read_bytes())
    if root.tag.split('}')[-1]!='svg': raise ValueError(f'Not SVG: {path}')
    for element in root.iter():
        tag=element.tag.split('}')[-1]
        if tag in ('script','foreignObject'): raise ValueError(f'Active SVG content: {path}')
        for key,value in element.attrib.items():
            if key.split('}')[-1].lower().startswith('on'): raise ValueError(f'Event handler: {path}')
            if key.split('}')[-1] in ('href','src') and value.startswith(('http:','https:','javascript:','data:')):
                if tag=='image' and value.startswith('data:image/png;base64,'):
                    embedded=base64.b64decode(''.join(value.split(',',1)[1].split()),validate=True)
                    if not embedded.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError(f'Invalid embedded PNG: {path}')
                else:raise ValueError(f'External/active SVG resource: {path}')
    vb=root.attrib.get('viewBox','').split()
    if len(vb)!=4 or float(vb[2])<=0 or float(vb[3])<=0: raise ValueError(f'Invalid viewBox: {path}')
    return {'viewBox':' '.join(vb),'width':float(vb[2]),'height':float(vb[3])}

def wav_check(path):
    with wave.open(str(path),'rb') as audio:
        if audio.getsampwidth()!=2 or audio.getframerate()!=48000 or audio.getnchannels()!=1:
            raise ValueError(f'Unexpected PCM format: {path}')
        frames=audio.getnframes();samples=struct.unpack('<'+'h'*frames,audio.readframes(frames))
        peak=max(map(abs,samples));duration=frames/audio.getframerate()
        if peak<=0 or peak>=32767: raise ValueError(f'Silent/clipped audio: {path}')
        return {'duration_seconds':duration,'sample_rate':48000,'channels':1,'bit_depth':16,
                'peak_dbfs':round(20*math.log10(peak/32767),3),'first_sample':samples[0],'last_sample':samples[-1]}

def build(source, repo, benchmark=None):
    library=repo/'library';assets=[];support=[];seen_ids=set();seen_hashes={};counts={}
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for group,(destination,expected) in GROUPS.items():
        base=source/group
        mf=next((p for p in (base/'manifest.json',base/'metadata.json') if p.exists()),None)
        if not mf: raise ValueError(f'Missing catalog: {group}')
        batch=records(mf)
        if len(batch)!=expected: raise ValueError(f'{group}: expected {expected}, got {len(batch)}')
        counts[group]=len(batch)
        for rec in batch:
            rec=dict(rec);origin=resolve_file(base,rec)
            if group=='background-motion':
                category='background' if 'backgrounds' in origin.parts else 'motion'
                dest=library/('images/backgrounds' if category=='background' else 'motion/overlays')/origin.name
            elif group=='sound-effects':
                category='sound-effect';dest=library/destination/origin.relative_to(base)
            else:
                category={'comparison-assets':'presentation-component','technical-diagrams':'diagram',
                          'icons':'icon','brands':'logo','evidence-labels':'evidence-label'}[group]
                dest=library/destination/origin.name
            identifier=rec['id']
            if identifier in seen_ids: raise ValueError(f'Duplicate ID {identifier}')
            seen_ids.add(identifier)
            digest=hashlib.sha256(origin.read_bytes()).hexdigest()
            if digest in seen_hashes: raise ValueError(f'Duplicate bytes: {origin} and {seen_hashes[digest]}')
            seen_hashes[digest]=str(origin)
            if rec.get('sha256') and rec['sha256']!=digest: raise ValueError(f'Hash mismatch: {origin}')
            validation=svg_check(origin) if origin.suffix=='.svg' else wav_check(origin)
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(origin,dest)
            rec.update(path=str(dest.relative_to(repo)),category=category,collection=group,
                       sha256=digest,bytes=origin.stat().st_size,validation=validation)
            rec.setdefault('kind',category)
            rec.setdefault('intended_use',rec.get('use','Reusable cloud-AI show production asset.'))
            rec.setdefault('source_url',None)
            rec.setdefault('retrieved_at',rec.get('downloaded_at',rec.get('created_at',now)))
            rec.setdefault('version','2026-10-starter')
            rec.setdefault('episode_uses',[])
            rec.setdefault('rights_status','original' if rec.get('origin')=='original' else 'licensed')
            rec['is_empirical_evidence']=False
            if category=='presentation-component':rec['requires_verified_episode_data']=True
            if category=='motion':rec['powerpoint_use']='Render animated SVG to video or recreate motion natively; SVG import alone is static.'
            # Remove preview paths that do not belong to the committed asset inventory.
            for key in ['preview_path','relative_path','license_file','license_path']:
                if key in rec:rec['upstream_'+key]=rec.pop(key)
            assets.append(rec)
        # Keep generator/acquisition notes and exact license notices, without large download archives.
        target=library/'provenance'/group;target.mkdir(parents=True,exist_ok=True)
        for path in list(base.glob('*.py'))+list(base.glob('*.js'))+list(base.glob('*.mjs'))+list(base.glob('*.md'))+list(base.glob('*.txt')):
            if path.name.lower().startswith('license') or path.suffix in ('.py','.js','.mjs','.md'):
                shutil.copy2(path,target/path.name);support.append(str((target/path.name).relative_to(repo)))
        for folder in ['licenses']:
            if (base/folder).is_dir():
                for path in (base/folder).glob('*'):
                    if path.is_file() and path.suffix in ('.txt','.md'):
                        shutil.copy2(path,target/path.name);support.append(str((target/path.name).relative_to(repo)))
        for name in ['verification.json','qa-report.json','render-report.json','upstream-release-ref.json']:
            path=base/name
            if path.exists():shutil.copy2(path,target/name);support.append(str((target/name).relative_to(repo)))
    assert len(assets)==1000
    if benchmark and (benchmark/'manifest.json').exists():
        batch=records(benchmark/'manifest.json')
        for rec in batch:
            rec=dict(rec);origin=resolve_file(benchmark,rec)
            if origin.suffix!='.svg':raise ValueError('Benchmark inventory must count SVG charts only, not PNG derivatives')
            svg_check(origin);dest=library/'graphics/benchmarks'/origin.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(origin,dest)
            digest=hashlib.sha256(origin.read_bytes()).hexdigest()
            if rec['id'] in seen_ids or digest in seen_hashes:raise ValueError('Duplicate benchmark asset')
            seen_ids.add(rec['id']);seen_hashes[digest]=str(origin)
            rec.update(path=str(dest.relative_to(repo)),category='benchmark-chart',kind='benchmark-chart',
                       collection='verified-benchmarks',sha256=digest,bytes=origin.stat().st_size,
                       is_empirical_evidence=True,retrieved_at=rec.get('retrieved_at',now))
            rec.setdefault('rights_status','original-factual-data-chart')
            assets.append(rec)
        counts['verified-benchmarks']=len(batch)
        evidence=library/'reproducibility/benchmarks-2026-10-13';evidence.mkdir(parents=True,exist_ok=True)
        for path in benchmark.rglob('*'):
            if path.is_file() and path.suffix in ('.csv','.json','.py','.md','.txt') and path.name!='manifest.json':
                dest=evidence/path.relative_to(benchmark);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
    index={'schema_version':2,'updated_at':now,'base_asset_count':1000,'total_assets':len(assets),
           'counts':dict(collections.Counter(a['category'] for a in assets)),
           'inventory_policy':'Counts only distinct reusable assets. Previews, licenses, metadata and scripts are not asset counts.',
           'assets':assets}
    (library/'asset-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
    (library/'INDEX.md').write_text(markdown_index(index))
    (library/'gallery.html').write_text(gallery(index))
    report={'verified_at':now,'base_asset_count':1000,'total_assets':len(assets),'counts':index['counts'],
            'all_paths_exist':True,'all_hashes_match':True,'unique_asset_ids':len(seen_ids),
            'unique_asset_hashes':len(seen_hashes),'svg_xml_and_resource_checks':'passed',
            'audio_format_clipping_and_silence_checks':'passed',
            'playback_limits':'SMIL motion assets need browser/video rendering. Native PowerPoint animated SVG playback is not asserted. Voiceover mixing not tested.',
            'benchmark_status':'See chart-specific source dates, coverage and methodology. No universal winner is inferred across incompatible metrics.'}
    (library/'verification-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'total_assets':len(assets),'counts':index['counts'],'asset_bytes':sum(a['bytes'] for a in assets),'support_files':len(support)}))

def markdown_index(index):
    lines=['# Media library: searchable inventory','',f"**{index['total_assets']} distinct assets**, including 1,000 starter assets and {index['total_assets']-1000} sourced benchmark charts.",'',
           'Download the branch ZIP and open `library/gallery.html` for a searchable visual/audio gallery. This HTML file is an offline catalog, not a hosted website. All paths and metadata are in `asset-index.json`.',
           '', 'Templates require verified episode data. Diagrams simplify concepts. Brand marks remain subject to their owners’ rights. Benchmark charts are dated snapshots, not permanent recommendations.','',
           '| Category | Count |','| --- | ---: |']
    lines += [f'| {cat} | {n} |' for cat,n in sorted(index['counts'].items())]
    for cat in sorted(index['counts']):
        lines += ['',f'## {cat}','', '| Asset | Intended use |','| --- | --- |']
        for a in index['assets']:
            if a['category']==cat:
                label=a['title'].replace('|','/');use=a.get('intended_use','').replace('|','/').replace('\n',' ')
                relative=Path(a['path']).relative_to('library')
                lines.append(f'| [{label}]({relative}) | {use} |')
    return '\n'.join(lines)+'\n'

def gallery(index):
    data=json.dumps(index['assets'],ensure_ascii=False).replace('</','<\\/')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI UPDATE — Media Library</title>
<style>*{box-sizing:border-box}body{margin:0;background:#081421;color:#f0f6fa;font:16px system-ui,sans-serif}header{padding:28px 5%;background:#10273a;position:sticky;top:0;z-index:2}h1{margin:0 0 12px;font-size:28px}p{color:#bdd2df;line-height:1.45}input,select{background:#fff;color:#112b3e;border:0;border-radius:7px;padding:12px;font-size:16px}input{width:min(55vw,650px)}button,a.link{background:#efc26d;color:#122537;border:0;padding:8px 12px;border-radius:5px;text-decoration:none;cursor:pointer}main{padding:24px 5%}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:18px}.card{background:#10273a;border:1px solid #24465f;border-radius:10px;overflow:hidden}.preview{height:170px;display:flex;align-items:center;justify-content:center;background:#fff;overflow:hidden}.preview img{width:100%;height:100%;object-fit:contain}.preview.icon img,.preview.logo img{width:72%;height:65%;padding:8px}.card .info{padding:15px}h2{font-size:17px;margin:0 0 9px}.tag{font-size:12px;color:#63dcec;display:block;margin-bottom:8px}.use{font-size:13px;min-height:42px;color:#bfd5e2}.warning{font-size:12px;color:#efc26d}.meta{font-size:12px;color:#a6c1d1;line-height:1.5}audio{width:95%}#more{margin:25px auto;display:block}#count{margin-top:12px;font-size:14px}@media(max-width:600px){header{position:static}input{width:100%;margin-bottom:9px}select{width:100%}.grid{grid-template-columns:1fr}}</style>
<header><h1>AI UPDATE — Media Library</h1><p>Original production graphics, licensed icons, company marks, sound effects and dated benchmark charts. Logos identify companies; templates contain no measured results.</p><input id="q" placeholder="Search cloud, prompt, Claude, evidence, cost…" aria-label="Search assets"> <select id="category" aria-label="Asset category"><option value="">All categories</option></select><div id="count"></div></header><main><div class="grid" id="grid"></div><button id="more">Show more</button></main>
<script>const assets='''+data+''';const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const categories=[...new Set(assets.map(x=>x.category))].sort();const select=document.querySelector('#category');categories.forEach(c=>{const o=document.createElement('option');o.value=c;o.textContent=c;select.append(o)});let filtered=[],limit=60;function render(){const query=document.querySelector('#q').value.toLowerCase().trim(),cat=select.value;filtered=assets.filter(a=>(!cat||a.category===cat)&&JSON.stringify([a.title,a.tags,a.intended_use,a.source_url,a.category]).toLowerCase().includes(query));document.querySelector('#count').textContent=filtered.length+' matching assets · '+assets.length+' total';document.querySelector('#grid').innerHTML=filtered.slice(0,limit).map(a=>{const path=(a.path.startsWith('library/')?a.path.slice(8):a.path);const sound=a.category==='sound-effect';const preview=sound?'<audio controls preload="none" src="'+esc(path)+'"></audio>':'<img loading="lazy" src="'+esc(path)+'" alt="'+esc(a.title)+'">';const note=a.category==='presentation-component'?'Template — add verified episode data':a.category==='motion'?'Animated SVG — render to video for PowerPoint':a.category==='logo'?'Community-maintained brand mark; trademark rules apply':a.category==='benchmark-chart'?'Dated factual chart; check source and coverage':'';return '<article class="card"><div class="preview '+esc(a.category)+'">'+preview+'</div><div class="info"><span class="tag">'+esc(a.category)+'</span><h2>'+esc(a.title)+'</h2><div class="use">'+esc(a.intended_use)+'</div><p class="warning">'+esc(note)+'</p><p class="meta">'+esc(a.license||a.rights_status||'')+'<br>'+esc([a.source_version,a.source_snapshot,a.source_date||a.data_date,a.retrieved_at?'Retrieved '+a.retrieved_at:''].filter(Boolean).join(' · '))+'</p><a class="link" href="'+esc(path)+'" download>Download asset</a> '+(a.source_url?'<a style="color:#63dcec" href="'+esc(a.source_url)+'" target="_blank" rel="noreferrer">Source</a>':'')+'</div></article>'}).join('');document.querySelector('#more').hidden=limit>=filtered.length}document.querySelector('#q').addEventListener('input',()=>{limit=60;render()});select.addEventListener('change',()=>{limit=60;render()});document.querySelector('#more').addEventListener('click',()=>{limit+=60;render()});render();</script></html>'''

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--repo',type=Path,required=True);parser.add_argument('--benchmark',type=Path)
    args=parser.parse_args();build(args.source,args.repo,args.benchmark)
