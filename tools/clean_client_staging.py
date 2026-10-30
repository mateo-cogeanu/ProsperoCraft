#!/usr/bin/env python3
"""Remove byte-verified duplicate staging for frozen client probes;dry-run by default."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
FROZEN={
 'opengl_bootstrap':'Client_OpenGL_Provider',
 'stb_bootstrap':'Client_STB_Codecs',
 'freetype_bootstrap':'Client_FreeType_Fonts',
 'vma_bootstrap':'Client_VMA_Allocator',
 'spvc_bootstrap':'Client_SPIRV_Cross',
}
def sha(path):
 with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args();total=0
 for variant,milestone in FROZEN.items():
  record=json.loads((ROOT/'tests/fixtures/historical-validation'/milestone/'validation.json').read_text());preserved=ROOT/'dist/milestones'/(milestone+'-'+record['app_version'])/'PPSA99874-full-local.zip'
  if not preserved.is_file()or sha(preserved)!=record['tested_full_package_sha256']:raise ValueError('Missing/corrupt preserved package: '+str(preserved))
  work=ROOT/('build/client-'+variant+'-probe');candidates=[]
  with zipfile.ZipFile(preserved)as package:
   if package.testzip():raise ValueError('Package CRC failure')
   for folder,prefix in [('PPSA99874','PPSA99874/'),('assets','PPSA99874/assets/')]:
    path=work/folder
    if not path.exists():continue
    files=list(path.rglob('*'))
    for file in files:
     if file.is_symlink():raise ValueError('Unexpected staging symlink: '+str(file))
     if file.is_file():
      name=prefix+file.relative_to(path).as_posix()
      if file.read_bytes()!=package.read(name):raise ValueError('Staging differs from frozen package: '+str(file))
    size=sum(p.stat().st_size for p in files if p.is_file());candidates.append((path,size))
  duplicate=ROOT/('dist/client-'+variant)/'PPSA99874.zip'
  if duplicate.is_file():
   if sha(duplicate)!=record['tested_full_package_sha256']:raise ValueError('Candidate differs from frozen package: '+str(duplicate))
   candidates.append((duplicate,duplicate.stat().st_size))
  if args.apply and (work/'assets/java25').exists():
   audit=work/'package-audits';audit.mkdir(exist_ok=True)
   for file in (work/'assets/java25').glob('*audit.json'):shutil.copyfile(file,audit/file.name)
  for path,size in candidates:
   print(('REMOVE 'if args.apply else'WOULD REMOVE ')+str(path.relative_to(ROOT))+f' ({size/1024**2:.1f} MiB logical)');total+=size
   if args.apply:
    if path.is_dir():shutil.rmtree(path)
    else:path.unlink()
 print(f'Logical duplicate bytes: {total}; APFS clones/compression mean physical space recovered may be lower.')
 print('Preserved frozen full ZIPs,release assets,symbols,source,logs,active startup staging and dependency objects. Older package tests may require restaging.')
if __name__=='__main__':main()
