#!/usr/bin/env python3
"""Build a separate, title-scoped native crash-capture payload; never load it.

Reviewed pinned GPL PS5 DevTools sources stay in ignored caches. This companion
needs the user's normal ELF loader and debugger privileges on their own PS5.
It changes no application ELF, game JAR, memory protection or runtime policy.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]

def scoped_source(text):
 start=text.index('static bool watch_policy(const char *title_id)\n{')
 end=text.index('\nstatic ',start+1)
 text=text[:start]+'''/* ProsperoCraft diagnostic adaptation: attach only our title. */
static bool watch_policy(const char *title_id)
{
    return !strcmp(title_id, "PPSA99874");
}
'''+text[end:]
 old='''                    !strncmp(ai.title_id, "NPXS", 4))'''
 assert text.count(old)==1
 text=text.replace(old,'''                    strcmp(ai.title_id, "PPSA99874"))''')
 start=text.index('    } else if (!strcmp(target, "/api/test/fault") && !strcmp(method, "POST")) {')
 end=text.index('    } else if (!strcmp(target, "/api/quit")',start)
 text=text[:start]+text[end:]
 text=text.replace('api_crash(fd, target + 11, !strcmp(method, "DELETE"));','api_crash(fd, target + 11, false);')
 text=text.replace('''    else if (!strcmp(target, "/api/errors"))
        api_errors(fd);''','''    else if (!strcmp(target, "/api/errors"))
        reply_text(fd, 404, "application/json", "{\\"error\\":\\"disabled in title-scoped capture\\"}");''')
 # api_errors is retained upstream code, but cannot be requested by this variant.
 text=text.replace('static void api_errors(', 'static __attribute__((unused)) void api_errors(')
 before='''    if (!strcmp(method, "OPTIONS"))'''
 assert text.count(before)==1
 text=text.replace(before,'''    if (strcmp(method, "GET") && !( !strcmp(method, "POST") && !strcmp(target, "/api/quit"))) {
        reply_text(fd, 405, "application/json", "{\\"error\\":\\"read-only capture; POST quit is available\\"}");
        close(fd);
        return;
    }
'''+before)
 # System crash reporting may stop a title before a POSIX fatal signal arrives.
 # Capture that stop as evidence, then preserve upstream SIGSTOP/detach behavior.
 before='''            say("%s pid %d: stop requested, detaching", t->title_id, pid);'''
 after='''            char stopped_id[96];
            capture(t, pid, SIGSTOP, stopped_id, sizeof stopped_id);
            finish_report(stopped_id, "stop-observed", t->name, t->last_crash);
            pthread_mutex_lock(&g_lock);
            t->reports++;
            pthread_mutex_unlock(&g_lock);
            say("%s pid %d: stop snapshot saved; SIGSTOP is not proof of a crash", t->title_id, pid);
            say("%s pid %d: stop requested, detaching", t->title_id, pid);'''
 assert text.count(before)==1
 text=text.replace(before,after)
 text=text.replace('POST /api/test/fault:', 'Unused upstream test state:')
 assert '/api/test/fault' not in text and 'api_crash(fd, target + 11, false);' in text
 return text

def build(runtime,source,llvm):
 pin=json.loads((ROOT/'client/diagnostics/crash-capture-upstream.json').read_text())
 if not source.exists():
  subprocess.run(['git','clone','--no-checkout',pin['repository'],str(source)],check=True)
  subprocess.run(['git','-C',str(source),'checkout','--detach',pin['commit']],check=True)
 assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==pin['commit']
 for name,digest in pin['files'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest,name
 private=ROOT/'build/client-crash-capture';(private/'payload').mkdir(parents=True,exist_ok=True);(private/'web').mkdir(exist_ok=True)
 for name in ['payload/Makefile','web/dashboard.html','LICENSE']:shutil.copy2(source/name,private/name)
 dashboard=private/'web/dashboard.html'
 dashboard.write_text(dashboard.read_text()+'''<button onclick="fetch('/api/quit',{method:'POST'}).then(r=>r.json()).then(v=>{this.textContent=v.still_attached?'Detach pending':'Capture stopped; detached';this.disabled=true})">Stop capture and detach</button>''')
 patched=scoped_source((source/'payload/main.c').read_text());(private/'payload/main.c').write_text(patched)
 sdk=runtime/'.tools/ps5-payload-sdk'
 env=dict(os.environ,PS5_PAYLOAD_SDK=str(sdk),LLVM_CONFIG=str(llvm/'llvm-config'))
 subprocess.run(['make','-C',str(private/'payload')],env=env,check=True)
 elf=private/'build/ps5devtools.elf';assert elf.read_bytes()[:6]==b'\x7fELF\x02\x01'
 audit={'upstream':pin,'adaptations':['Only PPSA99874 is sampled or attached;watch.txt cannot broaden scope','HTTP crash deletion,all-title error history and deliberate test-fault requests disabled','GET diagnostics and POST quit/detach retained;normal upstream crash forwarding unchanged','Save SIGSTOP register/thread snapshot as stop-observed before existing detach;not a proven fatal signal'],'source_sha256':hashlib.sha256(patched.encode()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'firmware':'Upstream tested13.60;actual crash history reports13.60','console':'Pending payload load,successful attach and repeat exact159 capture','not_a_game_build':True}
 (private/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
 print('Built title-scoped diagnostic payload:',elf)
 print('SHA256',audit['elf_sha256'],';not loaded;PS5 capture pending')
 return elf,audit

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);p.add_argument('--source-cache',type=Path);p.add_argument('--llvm-bin',type=Path,default=Path('/opt/homebrew/opt/llvm/bin'));a=p.parse_args()
 build(a.runtime_workspace.resolve(),(a.source_cache or ROOT/'.tools/ps5-devtools').resolve(),a.llvm_bin)
