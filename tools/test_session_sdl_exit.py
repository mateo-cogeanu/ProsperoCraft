#!/usr/bin/env python3
"""Real embedded HotSpot exit hook, Java shutdown observer and host exec barrier."""
import os,subprocess,tempfile,argparse
from pathlib import Path
from host_toolchain import ROOT,java_home,executable

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sdl-include',type=Path,required=True);p.add_argument('--sdl-library',type=Path,required=True);a=p.parse_args()
 jdk=java_home();system=os.uname().sysname
 if system not in ('Darwin','Linux'):raise RuntimeError('macOS/Linux required')
 server=jdk/'lib/server';library=server/('libjvm.dylib'if system=='Darwin'else'libjvm.so')
 if not library.is_file():raise FileNotFoundError(library)
 with tempfile.TemporaryDirectory(prefix='prospero-vm-exit-')as folder:
  w=Path(folder)
  (w/'VmExitCheck.java').write_text('''public final class VmExitCheck{
 static native void arm();
 public static void main(String[]args){
  new ProsperoExit(()->{if(args[0].equals("reject"))throw new IllegalStateException("PRIVATE");},VmExitCheck::arm,System.err);
  System.exit(args[0].equals("nonzero")?7:0);
 }
}''')
  subprocess.run([jdk/'bin/javac','--release','25','-d',w,ROOT/'client/launcher/java/ProsperoExit.java',w/'VmExitCheck.java'],check=True)
  source=w/'check.cpp';source.write_text(r'''#include <jni.h>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <unistd.h>
#include <thread>
#include "session_restart.hpp"
#include "final_cleanup.h"
#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>
static prospero_session::CleanExitGate gate;
static const char *program,*report_path;static FILE* report;
static void JNICALL arm(JNIEnv*,jclass){fprintf(report,"ARM\n");fflush(report);gate.arm();}
extern "C" int sceSystemServiceLoadExec(const char*path,const char*const*args){
 if(strcmp(path,"/app0/eboot.bin")||strcmp(args[0],"--prospero-library")||args[1])_Exit(95);
 fprintf(report,"RESTART\n");fflush(report);
 const char*next[]={program,"fresh",report_path,nullptr};execv(program,const_cast<char*const*>(next));return -5;
}
static void JNICALL exit_hook(jint code){
 bool accepted=gate.take(code);fprintf(report,"EXIT:%d:%d\n",code,accepted);fflush(report);
 if(accepted){if(SDL_WasInit(0))_Exit(98);fprintf(report,"SDL:%u\n",SDL_WasInit(0));fflush(report);int rc=prospero_session::restart_library();fprintf(report,"RETURNED:%d\n",rc);fflush(report);_Exit(96);}
}
int main(int argc,char**argv){
 if(argc==3&&!strcmp(argv[1],"fresh")){report=fopen(argv[2],"a");if(!report)return 97;fprintf(report,"FRESH\n");fclose(report);return 0;}
 if(argc!=5)return 94;program=argv[0];report_path=argv[3];report=fopen(report_path,"w");if(!report)return 93;
 SDL_SetMainReady();if(!SDL_Init(SDL_INIT_AUDIO|SDL_INIT_GAMEPAD|SDL_INIT_EVENTS|SDL_INIT_VIDEO))return 99;
 bool wrong_thread=true;std::thread worker([&]{wrong_thread=prospero_sdl_finalize();});worker.join();if(wrong_thread)return 97;
 if(prospero_sdl_finalize())return 96; // Live VIDEO is never forcibly stopped here.
 SDL_QuitSubSystem(SDL_INIT_VIDEO);
 if(!prospero_sdl_finalize())return 98;
 char cp[8192];if(snprintf(cp,sizeof(cp),"-Djava.class.path=%s",argv[1])>=int(sizeof(cp)))return 92;
 JavaVMOption options[]={{cp,nullptr},{const_cast<char*>("exit"),reinterpret_cast<void*>(&exit_hook)},{const_cast<char*>("-Xcheck:jni"),nullptr}};
 JavaVMInitArgs args{};args.version=JNI_VERSION_1_8;args.nOptions=3;args.options=options;
 JavaVM*vm=nullptr;JNIEnv*env=nullptr;if(JNI_CreateJavaVM(&vm,reinterpret_cast<void**>(&env),&args)!=JNI_OK)return 91;
 jclass cls=env->FindClass("VmExitCheck");if(!cls||env->ExceptionCheck())return 90;
 JNINativeMethod method{const_cast<char*>("arm"),const_cast<char*>("()V"),reinterpret_cast<void*>(&arm)};
 if(env->RegisterNatives(cls,&method,1)!=JNI_OK)return 89;
 jclass strings=env->FindClass("java/lang/String");if(!strings||env->ExceptionCheck())return 88;
 jobjectArray values=env->NewObjectArray(1,strings,nullptr);if(!values||env->ExceptionCheck())return 87;
 jstring mode=env->NewStringUTF(argv[2]);if(!mode||env->ExceptionCheck())return 86;
 env->SetObjectArrayElement(values,0,mode);if(env->ExceptionCheck())return 85;
 jmethodID main=env->GetStaticMethodID(cls,"main","([Ljava/lang/String;)V");if(!main||env->ExceptionCheck())return 84;
 env->CallStaticVoidMethod(cls,main,values);return 83;
}
''')
  subprocess.run([executable('clang++',env='CXX'),'-std=c++20','-pthread','-I'+str(a.sdl_include.resolve()),'-I'+str(ROOT/'client/ports/sdl'),'-I'+str(ROOT/'client/startup'),'-I'+str(jdk/'include'),'-I'+str(jdk/'include'/('darwin'if system=='Darwin'else'linux')),source,'-L'+str(server),'-ljvm',str(a.sdl_library.resolve()),'-Wl,-rpath,'+str(a.sdl_library.resolve().parent),'-Wl,-rpath,'+str(server),'-o',w/'check'],check=True)
  for mode,expected,code in [('clean','ARM\nEXIT:0:1\nSDL:0\nRESTART\nFRESH\n',0),('reject','EXIT:0:0\n',0),('nonzero','ARM\nEXIT:7:0\n',7)]:
   out=w/(mode+'.log');result=subprocess.run([w/'check',w,mode,out,'reserved'],text=True,capture_output=True,timeout=25,env=dict(os.environ,SDL_VIDEODRIVER="dummy",SDL_AUDIODRIVER="dummy"))
   assert result.returncode==code,(mode,result.returncode,result.stderr)
   assert out.read_text()==expected,(mode,out.read_text())
   assert 'PRIVATE'not in result.stderr
   assert 'WARNING in native method'not in result.stdout+result.stderr,result.stdout+result.stderr
 print('PASS embedded genuine HotSpot System.exit with actual SDL audio/gamepad/events initialized and real pre-exit main-thread SDL_Quit and post-VM zero-mask check: Java audit/native arm/real VM exit hook/one fresh-process exec; rejected/nonzero retain native exit; Xcheck:jni; PS5 LoadExec pending')
if __name__=='__main__':main()
