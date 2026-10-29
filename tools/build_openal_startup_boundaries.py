#!/usr/bin/env python3
"""Build private ALC scopes and graceful missing-cwd data discovery."""
from pathlib import Path
import hashlib
import json
import re
import shlex
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
LLVM=Path('/opt/homebrew/opt/llvm/bin')
LLD=Path('/opt/homebrew/opt/lld/bin/ld.lld')
MEMBER='CMakeFiles/OpenAL.dir/alc/alc.cpp.o'
HELPERS_MEMBER='CMakeFiles/OpenAL.dir/core/helpers.cpp.o'
ANCHORS=[
 ('alcGetError','ALC_API ALCenum ALC_APIENTRY alcGetError(ALCdevice *device) noexcept\n{','device'),
 ('alcGetString','ALC_API auto ALC_APIENTRY alcGetString(ALCdevice *Device, ALCenum param) noexcept -> const ALCchar*\ntry {','Device'),
 ('alcGetIntegerv','ALC_API void ALC_APIENTRY alcGetIntegerv(ALCdevice *device, ALCenum param, ALCsizei size,\n    ALCint *values) noexcept\ntry {','device, param, size, values'),
 ('alcCreateContext','ALC_API auto ALC_APIENTRY alcCreateContext(ALCdevice *device, const ALCint *attrList) noexcept\n    -> ALCcontext*\ntry {','device'),
 ('alcMakeContextCurrent','ALC_API auto ALC_APIENTRY alcMakeContextCurrent(ALCcontext *context) noexcept -> ALCboolean\ntry {','context'),
]
def sha(path):return hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
def command(line):
 args=shlex.split(line)
 if '&&'in args:args=args[args.index('&&')+1:];args=args[:args.index('&&')]if'&&'in args else args
 return args
def compile_copy(base,member,original,patched,obj,header=None,extra_flags=()):
 lines=subprocess.check_output(['ninja','-C',str(base),'-t','commands',member],text=True).splitlines();args=command(lines[-1])
 args[args.index('-o')+1]=str(obj);args[args.index('-c')+1]=str(patched)
 if '-MF'in args:args[args.index('-MF')+1]=str(obj)+'.d'
 args+=['-iquote',str(original.parent),'-iquote',str(ROOT/'client/ports/openal')]
 args+=list(extra_flags)
 if header:args+=['-include',str(header)]
 subprocess.run(args,cwd=base,check=True)
def build(host=False,speakers=False,host_objects=()):
 source=ROOT/'.tools/openal-soft-src';pin=json.loads((ROOT/'client/ports/openal/sources.json').read_text())
 assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==pin['commit']
 subprocess.run(['git','-C',str(source),'diff','--exit-code','HEAD'],check=True)
 base=ROOT/('build/openal-host'if host else'build/openal-ps5')
 out=ROOT/('build/openal-startup-boundary-host'if host else'build/openal-startup-boundary-ps5');out.mkdir(exist_ok=True)
 original=source/'alc/alc.cpp';text=original.read_text()
 for name,anchor,value in ANCHORS:
  assert text.count(anchor)==1,name
  text=text.replace(anchor,anchor+'\n    client_openal_boundary::Scope startup_scope{"'+name+'", '+value+'};')
 if speakers:
  text=text.replace('#include "backends/null.h"','#include "backends/null.h"\n#include "ps5_backend.h"')
  anchor='    BackendInfo{"null"sv, NullBackendFactory::getFactory},'
  assert text.count(anchor)==1
  text=text.replace(anchor,'    BackendInfo{"ps5"sv, Ps5BackendFactory::getFactory},\n'+anchor)
 patched=out/'alc.cpp';patched.write_text(text)
 header=ROOT/'client/ports/openal/startup_boundary.hpp';obj=out/'alc.cpp.o'
 compile_copy(base,MEMBER,original,patched,obj,header)
 helpers_original=source/'core/helpers.cpp';helpers=out/'helpers.cpp';helpers_obj=out/'helpers.cpp.o'
 text=helpers_original.read_text()
 before='''    else if(auto curpath = fs::current_path(); !curpath.empty())
        DirectorySearch(curpath, ext, &results);'''
 after='''    else
    {
        TRACE("App-local data search current_path begin");
        auto error = std::error_code{};
        auto curpath = fs::current_path(error);
        TRACE("App-local data search current_path result {}", error.value());
        if(error)
            WARN("Skipping app-local data search: current_path failed ({})", error.value());
        else if(!curpath.empty())
            DirectorySearch(curpath, ext, &results);
    }'''
 # Pinned file has Windows and POSIX overloads;patch only the latter.
 assert text.count(before)==2
 position=text.rfind(before)
 text=text[:position]+after+text[position+len(before):]
 before='''    if(auto localpath = al::getenv("ALSOFT_LOCAL_PATH"))
        DirectorySearch(*localpath, ext, &results);'''
 after='''    if(auto localpath = al::getenv("ALSOFT_LOCAL_PATH"))
    {
        TRACE("App-local data search explicit path selected");
        DirectorySearch(*localpath, ext, &results);
    }'''
 assert text.count(before)==1;text=text.replace(before,after)
 before='''        auto fpath = path.lexically_normal();
        if(!fs::exists(fpath))
            return;'''
 after='''        TRACE("Data directory normalization begin");
        auto fpath = path.lexically_normal();
        TRACE("Data directory normalization end; existence begin");
        const auto present = fs::exists(fpath);
        TRACE("Data directory existence result {}", present);
        if(!present)
            return;'''
 assert text.count(before)==1;text=text.replace(before,after)
 before='''        for(auto&& dirent : fs::directory_iterator{fpath})'''
 after='''        TRACE("Data directory iteration begin");
        for(auto&& dirent : fs::directory_iterator{fpath})'''
 assert text.count(before)==1;text=text.replace(before,after)
 before='''    const auto newlist = std::span{*results}.subspan(base);'''
 assert text.count(before)==1;text=text.replace(before,'    TRACE("Data directory iteration scope complete");\n'+before)
 helpers.write_text(text);compile_copy(base,HELPERS_MEMBER,helpers_original,helpers,helpers_obj)
 speaker_obj=out/'ps5_backend.cpp.o'
 if speakers:
  speaker_source=ROOT/'client/ports/openal/ps5_backend.cpp'
  compile_copy(base,'CMakeFiles/OpenAL.dir/alc/backends/null.cpp.o',source/'alc/backends/null.cpp',speaker_source,speaker_obj,extra_flags=['-fsanitize=address,undefined'] if host else [])

 logging_obj=None
 if speakers:
  logging_original=source/'core/logging.cpp';logging=out/'logging.cpp';logging_obj=out/'logging.cpp.o'
  text=logging_original.read_text();assert text.count('auto LogCallbackMutex = std::mutex{};')==1
  text=text.replace('auto LogCallbackMutex = std::mutex{};','auto LogCallbackMutex = ps5audio::Mutex{};')
  logging.write_text(text)
  compile_copy(base,'CMakeFiles/OpenAL.dir/core/logging.cpp.o',logging_original,logging,logging_obj,ROOT/'client/ports/openal/ps5_audio_mutex.hpp')
 audit={'pin':pin,'original_source_sha256':sha(original),'patched_source_sha256':sha(patched),'header_sha256':sha(header),'unit_object_sha256':sha(obj),'functions':[x[0]for x in ANCHORS],'scope':'At most128native API body scopes/256records,errno preserved;scope-exit includes exception unwinding,not success/return proof','game_jar_modified':False}
 audit['cwd_discovery_repair']={'original_source_sha256':sha(helpers_original),'patched_source_sha256':sha(helpers),'unit_object_sha256':sha(helpers_obj),'behavior':'Nonthrowing current_path(error_code);skip unavailable app-local search with warning,retain configured/local-valid/global/default HRTF discovery','console':'Host missing-cwd abort reproduced;PS5 cause/resolution unverified'}
 if host:
  lines=subprocess.check_output(['ninja','-C',str(base),'-t','commands','OpenAL'],text=True).splitlines()
  args=command(next(line for line in lines if '-dynamiclib'in line));library=out/'libopenal-boundary.dylib'
  args[args.index('-o')+1]=str(library);args[args.index(MEMBER)]=str(obj);args[args.index(HELPERS_MEMBER)]=str(helpers_obj)
  if speakers:args[args.index('CMakeFiles/OpenAL.dir/core/logging.cpp.o')]=str(logging_obj)
  if speakers:args += [str(speaker_obj),*[str(p)for p in host_objects],'-fsanitize=address,undefined']
  subprocess.run(args,cwd=base,check=True);result=library
 else:
  original_archive=base/'libopenal.a';before=sha(original_archive);archive=out/'libopenal-boundary.a';shutil.copy2(original_archive,archive)
  assert subprocess.check_output([str(LLVM/'llvm-ar'),'t',str(archive)],text=True).splitlines().count('alc.cpp.o')==1
  assert subprocess.check_output([str(LLVM/'llvm-ar'),'t',str(archive)],text=True).splitlines().count('helpers.cpp.o')==1
  subprocess.run([str(LLVM/'llvm-ar'),'r',str(archive),str(obj),str(helpers_obj),*([str(speaker_obj),str(logging_obj)]if speakers else [])],check=True)
  raw=out/'openal-raw.o';subprocess.run([str(LLD),'-r','--whole-archive',str(archive),'--no-whole-archive','-o',str(raw)],check=True)
  result=out/'openal.o';subprocess.run([str(LLVM/'llvm-objcopy'),'--redefine-syms='+str(base/'provider-bindings.txt'),str(raw),str(result)],check=True)
  sections=subprocess.check_output([str(LLVM/'llvm-readelf'),'-SW',str(result)],text=True);ctors=sorted(set(re.findall(r'\]\s+(\.(?:init_array|ctors)(?:\.\S+)?)\s',sections)));opts=[]
  for name in ctors:
   suffix=name.rsplit('.',1)[-1];priority=(65535-int(suffix)if name.startswith('.ctors.')else int(suffix))if suffix.isdigit()else 65535
   opts+=['--rename-section',name+'=.data.rel.ro.clientopenal.init_array.'+f'{priority:05d}'+name]
  if opts:subprocess.run([str(LLVM/'llvm-objcopy'),*opts,str(result)],check=True)
  assert sha(original_archive)==before
  audit.update(original_archive_sha256=before,private_archive_sha256=sha(archive),original_archive_unchanged=True,constructor_sections=ctors,replaced_members=['alc.cpp.o','helpers.cpp.o']+(['logging.cpp.o']if speakers else []))
 if speakers:
  audit['audio_mutex']={'source_sha256':sha(ROOT/'client/ports/openal/ps5_audio_mutex.hpp'),'logging_original_sha256':sha(logging_original),'logging_patched_sha256':sha(logging),'logging_object_sha256':sha(logging_obj),'scope':'Only OpenAL logging callback and PS5 AudioState/retained-port locks;normal nonrecursive acquire/release;64spin/50usbackoff;SDK/global/JVM locks unchanged'}
  audit['speaker_backend']={'source_sha256':sha(ROOT/'client/ports/openal/ps5_backend.cpp'),'header_sha256':sha(ROOT/'client/ports/openal/ps5_backend.h'),'port_pool_header_sha256':sha(ROOT/'client/ports/openal/ps5_port_pool.hpp'),'object_sha256':sha(speaker_obj),'name':'ps5/PS5 Speakers','format':'ActualOpenALmixer->AudioOutSYSTEM/main,48kHz,stereoS16,256frames;outputpacedworker,joinbeforeclose','console':'PendingactualPS5sound'}
 audit['output_sha256']=sha(result);(out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
 return result,audit
