#!/usr/bin/env python3
"""Execute the exact181 animation/lifecycle core on actual macOS GLFW/Zink.

Explicit native inputs only. SDL dummy draws offscreen on real lavapipe, so no
VideoOut, positive kopper surface, refresh or launcher handoff is established.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
from host_toolchain import ROOT, executable

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cc',required=True)
    for name in ('glfw-library','frontend','glfw-headers','gl-headers'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    if platform.system()!='Darwin':raise RuntimeError('Current research lane is macOS/lavapipe; no platform substitution')
    cc=executable('clang',override=args.cc);library=args.glfw_library.resolve();frontend=args.frontend.resolve()
    audit=json.loads(library.with_name('audit.json').read_text())
    assert sha(library)==audit['output_sha256']
    for name,digest in audit['local_source_sha256'].items():assert sha(ROOT/'client/ports/glfw'/name)==digest
    front_audit=json.loads(frontend.with_suffix('.json').read_text())
    assert sha(frontend)==front_audit['output_sha256']
    for name,digest in front_audit['source']['recipe']['frontend'].items():assert sha(ROOT/'client/ports/zink'/name)==digest
    work=ROOT/'build/zink-present-host';work.mkdir(exist_ok=True)
    binary=work/'probe'
    subprocess.run([cc,'-std=c11','-g','-fsanitize=address,undefined','-Wall','-Wextra','-Werror',
        '-DPS5ZINK_CYCLE_MILLISECONDS=120','-I'+str(args.glfw_headers.resolve()),'-I'+str(args.gl_headers.resolve()),
        str(ROOT/'client/zink_present/present.c'),str(ROOT/'tools/fixtures/zink_present_host.c'),str(library),str(frontend),
        '-Wl,-rpath,'+str(frontend.parent),'-o',str(binary)],check=True)
    env=dict(os.environ,LIBGL_ALWAYS_SOFTWARE='true',SDL_VIDEODRIVER='dummy',
        ASAN_OPTIONS='detect_leaks=0:handle_segv=0:handle_sigbus=0:handle_sigfpe=0',UBSAN_OPTIONS='halt_on_error=1',
        MESA_SHADER_CACHE_DIR=str(work/'shader-cache'))
    result=subprocess.run([str(binary)],env=env,capture_output=True,text=True,timeout=60)
    output=result.stdout+result.stderr;(work/'run.log').write_text(output)
    assert result.returncode==0,output[-5000:]
    assert output.count('Cycle complete: real GLFW/SDL teardown; next cycle must reacquire display')==3,output
    assert 'PASS actual GLFW/Zink animation and triple teardown/reinit' in output
    assert 'ERROR: AddressSanitizer' not in output and 'runtime error:' not in output
    print('PASS exact181 animation core: actual GLFW/Zink clear/scissor/swap/readback/guards and3 complete teardown/reinit cycles; ASan/UBSan; host offscreen only')
    (work/'audit.json').write_text(json.dumps({'probe_sha256':sha(ROOT/'client/zink_present/present.c'),
        'glfw_sha256':sha(library),'frontend_sha256':sha(frontend),'result':'PASS',
        'scope':__doc__,'sanitizers':'Frontend/GLFW/driver ASan+UBSan; Mesa/ICD ordinary builds',
        'cycle_ms':120,'ps5':'NOT TESTED'},indent=2)+'\n')

if __name__=='__main__':main()
