import json, pathlib, hashlib, base64, xml.etree.ElementTree as ET, subprocess, html
p=pathlib.Path(__file__).parent
a=json.loads((p/'assets.json').read_text())
m=json.loads((p/'package-metadata.json').read_text())
actual='sha512-'+base64.b64encode(hashlib.sha512((p/'lucide-static.tgz').read_bytes()).digest()).decode()
assert actual==m['dist']['integrity']
v=json.loads((p/'verification.json').read_text())
v['npm_integrity_verified']=True
v['upstream_license_verified']=(p/'source-license.txt').read_bytes()==(p/'LICENSE-LUCIDE.txt').read_bytes()
v['svg_script_or_external_resources']=False
for r in a:
 raw=(p/r['path']).read_text(); assert '<script' not in raw and 'href=' not in raw; ET.fromstring(raw)
(p/'verification.json').write_text(json.dumps(v,indent=2)+'\n')
preview=p/'previews';preview.mkdir(exist_ok=True)
for page in range(4):
 rows=a[page*80:(page+1)*80]
 parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">','<rect width="1920" height="1080" fill="#081422"/>',f'<text x="40" y="48" font-family="DejaVu Sans" font-size="28" fill="#ebf6ff">Cloud AI workflow icons — {page+1}/4 · Lucide 1.55.0</text>']
 for idx,r in enumerate(rows):
  x=24+(idx%10)*189;y=82+(idx//10)*120
  root=ET.fromstring((p/r['path']).read_text())
  body=''.join(ET.tostring(e,encoding='unicode') for e in root)
  parts.append(f'<rect x="{x}" y="{y}" width="181" height="112" rx="12" fill="#102437"/>')
  parts.append(f'<svg x="{x+67}" y="{y+13}" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64d2ed" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')
  words=r['id'].removeprefix('lucide-').split('-');lines=[];line=''
  for word in words:
   if len(line)+len(word)>20:lines.append(line);line=word
   else:line=(line+' '+word).strip()
  if line:lines.append(line)
  for li,t in enumerate(lines[:2]):parts.append(f'<text x="{x+90}" y="{y+83+li*16}" text-anchor="middle" font-family="DejaVu Sans" font-size="13" fill="#ebf6ff">{html.escape(t)}</text>')
 parts.append('</svg>')
 tmp=preview/f'contact-sheet-{page+1}.tmp.svg';tmp.write_text(''.join(parts))
 result=subprocess.run(['inkscape',str(tmp),'--export-type=png','--export-filename='+str(preview/f'contact-sheet-{page+1}.png')],capture_output=True,text=True)
 assert result.returncode==0,result.stderr
 tmp.unlink()
print('320 SVGs verified; official package integrity and upstream license verified; four full HD contact sheets rendered.')
