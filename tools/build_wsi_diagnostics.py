#!/usr/bin/env python3
"""Build native WSI diagnostics/retry in a private archive;preserve pinned inputs."""
from pathlib import Path
import hashlib,json,shlex,shutil,subprocess,os
ROOT=Path(__file__).resolve().parents[1];LLVM=Path('/opt/homebrew/opt/llvm/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 out=ROOT/'build/wsi-diagnostics';out.mkdir(exist_ok=True)
 mesa=ROOT/'.tools/PS5_Mesa';pin=json.loads((ROOT/'client/graphics/sources.json').read_text())['mesa']['commit'];relative='src/vulkan/wsi/wsi_common_videoout.c'
 original=subprocess.check_output(['git','-C',str(mesa),'show',pin+':'+relative]);assert (mesa/relative).read_bytes()==original,'Dirty pinned WSI input'
 source=out/'wsi_common_videoout.c';source.write_bytes(original);patch=ROOT/'client/ports/mesa/0001-videoout-checkpoints.patch'
 subprocess.run(['git','apply','--unsafe-paths','--directory='+str(out),str(patch)],check=True)
 retry=ROOT/'client/ports/mesa/0002-videoout-open-retry.patch'
 subprocess.run(['git','apply','--unsafe-paths','--directory='+str(out),str(retry)],check=True)
 resources=ROOT/'client/ports/mesa/0003-videoout-resources.patch'
 subprocess.run(['git','apply','--unsafe-paths','--directory='+str(out),str(resources)],check=True)
 early=ROOT/'client/ports/mesa/0004-videoout-early-owner.patch'
 subprocess.run(['git','apply','--unsafe-paths','--directory='+str(out),str(early)],check=True)
 present=ROOT/'client/ports/mesa/0005-videoout-present-progress.patch'
 subprocess.run(['git','apply','--unsafe-paths','--directory='+str(out),str(present)],check=True)
 cursor=ROOT/'client/ports/mesa/0006-videoout-menu-cursor.patch'
 subprocess.run(['git','apply','--unsafe-paths','--directory='+str(out),str(cursor)],check=True)
 keyboard=ROOT/'client/ports/mesa/0007-videoout-keyboard-overlay.patch'
 for name in ['keyboard_overlay.h','keyboard_layout.h']:shutil.copy2(ROOT/'client/ports/mesa'/name,out/name)
 subprocess.run(['git','apply','--unsafe-paths','--directory='+str(out),str(keyboard)],check=True)
 worker=ROOT/'client/ports/mesa/0008-videoout-reserved-worker.patch'
 subprocess.run(['git','apply','--unsafe-paths','--directory='+str(out),str(worker)],check=True)
 input_trace=ROOT/'client/ports/mesa/0009-input-present-checkpoints.patch'
 subprocess.run(['git','apply','--unsafe-paths','--directory='+str(out),str(input_trace)],check=True)
 database=json.loads((ROOT/'build/graphics-radv/compile_commands.json').read_text());rows=[r for r in database if r['file'].endswith('/wsi_common_videoout.c')];assert len(rows)==1;row=rows[0];arguments=shlex.split(row['command']);old_object=arguments[arguments.index('-o')+1]
 obj=out/'wsi_common_videoout.c.o';arguments[arguments.index('-o')+1]=str(obj);arguments[arguments.index('-MF')+1]=str(obj)+'.d';arguments[arguments.index('-MQ')+1]=str(obj);arguments[arguments.index('-c')+1]=str(source)
 subprocess.run(arguments,cwd=row['directory'],env=dict(os.environ,LLVM_CONFIG=str(LLVM/'llvm-config'),PATH=str(LLVM)+':'+os.environ['PATH']),check=True)
 original_archive=ROOT/'build/graphics-radv/src/amd/vulkan/libvulkan_radeon.a';before=sha(original_archive);archive=out/'libvulkan_radeon-diagnostic.a';assert original_archive.read_bytes()[:8]==b'!<arch>\n';shutil.copy2(original_archive,archive)
 members=subprocess.check_output([str(LLVM/'llvm-ar'),'t',str(archive)],text=True).splitlines();assert members.count(obj.name)==1
 subprocess.run([str(LLVM/'llvm-ar'),'r',str(archive),str(obj)],check=True);assert sha(original_archive)==before
 assert subprocess.check_output([str(LLVM/'llvm-ar'),'p',str(archive),obj.name])==obj.read_bytes()
 audit={'scope':'Early initialization of same WSI-owned output;native checkpoints and one delayed pre-resource VideoOut retry;max2 OS opens,success handle retained,negative results remain failure;read-only before/after kernel memory queries;first8 present/fence/flip progress and errors;64events/384byte formatting','mesa_commit':pin,'original_source_sha256':hashlib.sha256(original).hexdigest(),'patch_sha256':sha(patch),'retry_patch_sha256':sha(retry),'resources_patch_sha256':sha(resources),'early_owner_patch_sha256':sha(early),'present_progress_patch_sha256':sha(present),'cursor_patch_sha256':sha(cursor),'keyboard_patch_sha256':sha(keyboard),'reserved_worker_patch_sha256':sha(worker),'input_present_patch_sha256':sha(input_trace),'keyboard_headers_sha256':{name:sha(ROOT/'client/ports/mesa'/name)for name in ['keyboard_overlay.h','keyboard_layout.h']},'patched_source_sha256':sha(source),'object_sha256':sha(obj),'original_archive_sha256':before,'private_archive_sha256':sha(archive),'replaced_member':obj.name,'original_archive_unchanged':True,'console':'PENDING PS5 rejection checkpoint/crash investigation'}
 (out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print('PASS diagnostic WSI target compile/private archive member substitution;original archive retained');return archive,audit
if __name__=='__main__':build()
