"""Verify and preview committed icons; omitted acquisition archives are not rechecked."""
import argparse, hashlib, html, json, pathlib, subprocess, tempfile
import xml.etree.ElementTree as ET

repo=pathlib.Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser()
parser.add_argument('--output-dir',type=pathlib.Path)
args=parser.parse_args()
output=args.output_dir or pathlib.Path(tempfile.mkdtemp(prefix='ai-update-icons-qa-'))
output.mkdir(parents=True,exist_ok=True)
assets=[a for a in json.loads((repo/'library/asset-index.json').read_text())['assets'] if a['collection']=='icons']
if len(assets)!=320:raise ValueError('Expected 320 committed icon records')
for asset in assets:
 source=(repo/asset['path']).resolve()
 if not source.is_relative_to(repo):raise ValueError('Asset path leaves repository')
 raw=source.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=asset['sha256']:raise ValueError('Hash mismatch: '+asset['id'])
 svg=ET.fromstring(raw)
 for element in svg.iter():
  if element.tag.split('}')[-1] in ('script','foreignObject'):raise ValueError('Active SVG content')
  for key,value in element.attrib.items():
   if key.split('}')[-1].lower().startswith('on'):raise ValueError('SVG event handler')
   if key.split('}')[-1] in ('href','src') and not value.startswith('#'):raise ValueError('External SVG resource')
for page in range(4):
 rows=assets[page*80:(page+1)*80]
 parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">','<rect width="1920" height="1080" fill="#081422"/>',f'<text x="40" y="48" font-family="DejaVu Sans" font-size="28" fill="#ebf6ff">AI UPDATE workflow icons — {page+1}/4 · Lucide 1.55.0</text>']
 for index,asset in enumerate(rows):
  x=24+(index%10)*189;y=82+(index//10)*120
  svg=ET.fromstring((repo/asset['path']).read_text())
  body=''.join(ET.tostring(element,encoding='unicode') for element in svg)
  parts.append(f'<rect x="{x}" y="{y}" width="181" height="112" rx="12" fill="#102437"/>')
  parts.append(f'<svg x="{x+67}" y="{y+13}" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64d2ed" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')
  words=asset['id'].removeprefix('lucide-').split('-');lines=[];line=''
  for word in words:
   if len(line)+len(word)>20:lines.append(line);line=word
   else:line=(line+' '+word).strip()
  if line:lines.append(line)
  for offset,text in enumerate(lines[:2]):parts.append(f'<text x="{x+90}" y="{y+83+offset*16}" text-anchor="middle" font-family="DejaVu Sans" font-size="13" fill="#ebf6ff">{html.escape(text)}</text>')
 parts.append('</svg>')
 svg_path=output/f'contact-sheet-{page+1}.svg';svg_path.write_text(''.join(parts))
 subprocess.run(['inkscape',str(svg_path),'--export-type=png','--export-filename='+str(output/f'contact-sheet-{page+1}.png')],check=True,capture_output=True,text=True)
 svg_path.unlink()
report={'assets':len(assets),'all_committed_hashes_match':True,'svg_xml_and_active_resource_checks':'passed','contact_sheets_rendered':4,'source_catalog':'library/asset-index.json','upstream_package_integrity_rechecked':False,'upstream_license_identity_rechecked':False,'limitations':'Checks committed assets; original package/archive inputs are not committed.'}
(output/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({**report,'output_directory':str(output)}))
