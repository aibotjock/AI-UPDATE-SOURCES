import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const sharp=require(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES ? path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,'sharp') : 'sharp');
const root=path.dirname(fileURLToPath(import.meta.url));
const repo=path.resolve(root,'../../..');
const outputIndex=process.argv.indexOf('--output-dir');
if(outputIndex>=0&&!process.argv[outputIndex+1])throw Error('--output-dir requires a path');
const output=outputIndex>=0 ? path.resolve(process.argv[outputIndex+1]) : fs.mkdtempSync(path.join(os.tmpdir(),'ai-update-background-qa-'));
fs.mkdirSync(output,{recursive:true});
const assets=JSON.parse(fs.readFileSync(path.join(repo,'library/asset-index.json'),'utf8')).assets.filter(a=>a.collection==='background-motion');
if(assets.length!==200)throw Error('Expected 200 background/motion assets');
const rendered=[];
for(let i=0;i<assets.length;i+=8){
 const batch=await Promise.all(assets.slice(i,i+8).map(async asset=>{
  const source=path.resolve(repo,asset.path);
  if(!source.startsWith(repo+path.sep))throw Error('Asset path leaves repository');
  const bytes=fs.readFileSync(source);
  if(crypto.createHash('sha256').update(bytes).digest('hex')!==asset.sha256)throw Error('Hash mismatch: '+asset.id);
  const buffer=await sharp(bytes).resize(320,180).png().toBuffer();
  return {asset,buffer};
 }));
 rendered.push(...batch);
}
const samples=rendered.filter(x=>x.asset.path.endsWith('-01.svg'));
if(samples.length!==40)throw Error('Expected 40 family samples');
const comps=[];
const escape=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
for(let i=0;i<samples.length;i++){
 const x=(i%5)*320,y=Math.floor(i/5)*210;
 comps.push({input:samples[i].buffer,left:x,top:y});
 const label=escape(samples[i].asset.title.split(' — ')[0]);
 const xml=`<svg width="320" height="30" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="30" fill="#0c273d"/><text x="12" y="20" font-family="DejaVu Sans, sans-serif" font-size="13" fill="#eaf7ff">${samples[i].asset.category==='background'?'BG':'MOTION'} ${label}</text></svg>`;
 comps.push({input:Buffer.from(xml),left:x,top:y+180});
}
await sharp({create:{width:1600,height:1680,channels:3,background:'#061423'}}).composite(comps).png().toFile(path.join(output,'contact-sheet.png'));
const report={rendered:rendered.length,failed:0,sampled_families:samples.length,source_catalog:'library/asset-index.json',all_committed_hashes_match:true,contact_sheet:'contact-sheet.png',animation_playback_verified:false,render_engine:'sharp/libvips static SVG rasterization',notes:['All 200 committed SVGs rasterize successfully.','Contact sheet shows static fallback frames, not browser animation playback.','Some transition assets begin off-canvas by design.','Narration/audio mixing and PowerPoint export are outside this check.']};
fs.writeFileSync(path.join(output,'render-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report,output_directory:output}));
