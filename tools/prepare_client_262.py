#!/usr/bin/env python3
"""Populate ignored26.2publisher caches for host integration checks; original files only."""
from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures
root=Path(__file__).resolve().parents[1];r=root/'build/version122-research';r.mkdir(parents=True,exist_ok=True)
row=json.loads((root/'client/26.2.lock.json').read_text())['versions'][0];data=urllib.request.urlopen(row['metadata']['url'],timeout=60).read();assert hashlib.sha1(data).hexdigest()==row['metadata']['sha1'];(r/'26.2.json').write_bytes(data);m=json.loads(data)
def download(a,path):
 path.parent.mkdir(parents=True,exist_ok=True)
 for candidate in [path,root/'.tools/client'/path.name]:
  if candidate.is_file() and candidate.stat().st_size==a['size'] and hashlib.sha1(candidate.read_bytes()).hexdigest()==a['sha1']:
   return
 for attempt in range(3):
  try:
   data=urllib.request.urlopen(a['url'],timeout=60).read();assert len(data)==a['size']and hashlib.sha1(data).hexdigest()==a['sha1'];path.write_bytes(data);return
  except Exception:
   if attempt==2:raise
download(m['downloads']['client'],r/'26.2-client.jar')
jobs=[]
for lib in m['libraries']:
 if ':natives-'in lib['name']or(lib['name'].startswith('io.netty:netty-transport-native-')and len(lib['name'].split(':'))>3)or'artifact'not in lib.get('downloads',{}):continue
 if 'rules'in lib and not any(rule.get('action')=='allow'and rule.get('os',{}).get('name','linux')=='linux'for rule in lib['rules']):continue
 a=lib['downloads']['artifact'];jobs.append((a,r/Path(a['path']).name))
index=m['assetIndex'];download(index,r/('assets-'+index['id']+'.json'))
for obj in json.loads((r/('assets-'+index['id']+'.json')).read_text())['objects'].values():
 h=obj['hash'];p=root/'.tools/client-assets/objects'/h[:2]/h
 if p.is_file()and p.stat().st_size==obj['size']and hashlib.sha1(p.read_bytes()).hexdigest()==h:continue
 jobs.append(({'url':'https://resources.download.minecraft.net/'+h[:2]+'/'+h,'sha1':h,'size':obj['size']},r/'objects'/h[:2]/h))
with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:list(pool.map(lambda job:download(*job),jobs))
print('Verified26.2publisher cache',len(jobs),'dependency/asset candidates')
