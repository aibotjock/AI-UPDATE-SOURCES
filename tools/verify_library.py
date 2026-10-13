#!/usr/bin/env python3
"""Validate the indexed payloads, including new assets added after the starter kit."""
import collections,hashlib,json,wave,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    catalog=json.loads((ROOT/'library/asset-index.json').read_text());assets=catalog['assets'];ids=set();hashes=set()
    for asset in assets:
        p=ROOT/asset['path']
        if not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Asset path leaves repository')
        data=p.read_bytes();digest=hashlib.sha256(data).hexdigest()
        if digest!=asset['sha256']:raise ValueError('Hash mismatch: '+asset['id'])
        if len(data)!=asset['bytes']:raise ValueError('Byte count mismatch: '+asset['id'])
        if asset['id'] in ids or digest in hashes:raise ValueError('Duplicate asset')
        ids.add(asset['id']);hashes.add(digest)
        if p.suffix=='.svg':ET.fromstring(data)
        elif p.suffix=='.wav':
            with wave.open(str(p),'rb') as f:
                if f.getframerate()!=48000 or f.getnchannels()!=1 or f.getsampwidth()!=2:raise ValueError('Unexpected audio format')
        if not asset.get('title') or not asset.get('category') or not asset.get('rights_status'):raise ValueError('Missing provenance/usage fields')
        if asset.get('is_empirical_evidence') and not asset.get('source_url'):raise ValueError('Empirical chart missing source')
    counts=dict(collections.Counter(a['category'] for a in assets))
    if len(assets)!=catalog['total_assets'] or counts!=catalog['counts']:raise ValueError('Inventory count mismatch')
    print(json.dumps({'assets':len(assets),'counts':counts,'paths_hashes_bytes_and_formats':'passed','unique_assets':'passed'}))
if __name__=='__main__':main()
