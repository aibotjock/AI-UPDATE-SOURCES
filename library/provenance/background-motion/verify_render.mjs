import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const sharp=require(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES+'/sharp');
const root=path.dirname(new URL(import.meta.url).pathname);
const catalog=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
const rendered=[];
for(let i=0;i<catalog.assets.length;i+=8){
 const batch=await Promise.all(catalog.assets.slice(i,i+8).map(async a=>{
  const b=await sharp(path.join(root,a.path)).resize(320,180).png().toBuffer();
  const stat=await sharp(b).stats();
  return {asset:a,buffer:b,stats:stat};
 }));
 rendered.push(...batch);
}
const samples=rendered.filter(x=>x.asset.path.endsWith('-01.svg'));
const width=1600,height=1680;
const comps=[];
for(let i=0;i<samples.length;i++){
 const x=(i%5)*320,y=Math.floor(i/5)*210;
 comps.push({input:samples[i].buffer,left:x,top:y});
 const label=samples[i].asset.title.split(' — ')[0];
 const xml=`<svg width="320" height="30" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="30" fill="#0c273d"/><text x="12" y="20" font-family="DejaVu Sans, sans-serif" font-size="13" fill="#eaf7ff">${i<20?'BG':'MOTION'} ${label}</text></svg>`;
 comps.push({input:Buffer.from(xml),left:x,top:y+180});
}
await sharp({create:{width,height,channels:3,background:'#061423'}}).composite(comps).png().toFile(path.join(root,'contact-sheet.png'));
const report={rendered:rendered.length,failed:0,sampled_families:samples.length,contact_sheet:'contact-sheet.png',animation_playback_verified:false,render_engine:'sharp/libvips static SVG rasterization',notes:['All 200 SVGs rasterize successfully.','Motion contact sheet shows SVG static fallback frames, not browser animation playback.','Some transition assets begin off-canvas by design.','Static fallback frames of animated overlays are not intended as final PowerPoint animation.']};
fs.writeFileSync(path.join(root,'render-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
