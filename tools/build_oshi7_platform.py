#!/usr/bin/env python3
"""Compile an opt-in OSHI7 SPI provider without replacing publisher classes."""
from pathlib import Path
import argparse,hashlib,json,subprocess,urllib.request,zipfile,shutil
ROOT=Path(__file__).resolve().parents[1]
def build(java_home,offline=False):
 source=ROOT/'client/ports/oshi7';spec=json.loads((source/'sources.json').read_text());pin=spec['artifact'];archive=ROOT/'.tools/oshi-common-7.7.2.jar'
 if not archive.exists():
  if offline:raise FileNotFoundError(archive)
  urllib.request.urlretrieve(pin['url'],archive)
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 assert archive.stat().st_size==pin['size'] and sha(archive)==pin['sha256']
 assert sha(source/'LICENSE')==spec['license']['sha256']
 work=ROOT/'build/client-ports/oshi7';work.mkdir(parents=True,exist_ok=True);classes=work/'classes';shutil.rmtree(classes,ignore_errors=True);classes.mkdir()
 shared=ROOT/'client/ports/oshi/java/oshi/ps5/Ps5Hardware.java'
 subprocess.run([str(java_home/'bin/javac'),'--release','25','-cp',str(archive),'-d',str(classes),str(shared),*map(str,sorted((source/'java').rglob('*.java')))],check=True)
 output=work/'oshi-7.7.2-ps5-provider.jar'
 with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(classes.rglob('*.class')):
   info=zipfile.ZipInfo(p.relative_to(classes).as_posix());info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
  z.writestr(zipfile.ZipInfo('META-INF/services/oshi.spi.SystemInfoProvider'),'oshi.ps5.Ps5SystemInfoProvider\n')
  z.writestr(zipfile.ZipInfo('META-INF/OSHI-LICENSE.txt'),(source/'LICENSE').read_bytes())
 audit={'scope':spec['scope'],'artifact':pin,'output_sha256':sha(output),'source_sha256':{p.relative_to(ROOT).as_posix():sha(p)for p in [shared,*sorted(source.rglob('*.java'))]},'game_jar_modified':False,'console':'pending'}
 (work/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print('PASS OSHI7 SPI provider',sha(output));return output
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--java-home',type=Path,required=True);p.add_argument('--offline',action='store_true');a=p.parse_args();build(a.java_home,a.offline)
