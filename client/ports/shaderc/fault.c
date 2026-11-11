/* SPDX-License-Identifier: GPL-3.0-or-later
 * Scoped diagnostics for the serial compiler acceptance workload. Never recover
 * a fault or rewrite its context: forward to the pre-existing signal handler.
 */
#include <signal.h>
#include <errno.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>

#ifndef PS5_SHADERC_FAULT_LOG
#define PS5_SHADERC_FAULT_LOG "/download0/java25-vm-trace.log"
#endif
#ifndef PS5_SHADERC_CONTEXT_WORDS
#define PS5_SHADERC_CONTEXT_WORDS 96
#endif
#ifndef PS5_SHADERC_MAX_REPORTS
#define PS5_SHADERC_MAX_REPORTS 0
#endif
static unsigned report_count;
/* First four positions preserve the existing scope/status ABI. */
static const int signals[] = {SIGSEGV,SIGBUS,SIGILL,SIGABRT,SIGFPE,SIGTRAP,SIGSYS};
enum { signal_count=sizeof(signals)/sizeof(signals[0]) };
static struct sigaction previous[signal_count];
static int installed[signal_count];
static volatile sig_atomic_t report_fd=-1;
static unsigned lock_word;
static void guard_lock(void){while(__atomic_exchange_n(&lock_word,1,__ATOMIC_ACQUIRE)){
#if defined(__x86_64__)
 __asm__ volatile("pause");
#elif defined(__aarch64__)
 __asm__ volatile("yield");
#endif
}}
static void guard_unlock(void){__atomic_store_n(&lock_word,0,__ATOMIC_RELEASE);}
static unsigned users;
static void value(const char *label,uint64_t number){
 char line[128];unsigned n=0;
 while(*label && n<100)line[n++]=*label++;
 line[n++]='0';line[n++]='x';
 const char hex[]="0123456789abcdef";
 for(int shift=60;shift>=0;shift-=4)line[n++]=hex[(number>>shift)&15];
 line[n++]='\n';(void)write(report_fd,line,n);
}
#ifdef PS5_SHADERC_PROBE_STACK
/* The caller initializes these once, before installing any handlers. */
static uintptr_t probe_stack_low, probe_stack_high;
static uintptr_t probe_text_low, probe_text_high;

void ps5shaderc_fault_set_probe_stack(uintptr_t low, uintptr_t high,
                                    uintptr_t text_low, uintptr_t text_high) {
 probe_stack_low = low;
 probe_stack_high = high;
 probe_text_low = text_low;
 probe_text_high = text_high;
}

static void report_probe_stack(const volatile uint64_t *context_words) {
 /* Same target x86-64 RSP slot as the Java 17 PS5 signal context. */
 const uintptr_t sp = context_words[31];
 if (probe_stack_high <= probe_stack_low ||
     probe_stack_high - probe_stack_low < sizeof(uint64_t) ||
     sp < probe_stack_low || sp > probe_stack_high - sizeof(uint64_t) ||
     (sp & (sizeof(uint64_t) - 1)) != 0) return;

 const size_t available = (probe_stack_high - sp) / sizeof(uint64_t);
 const size_t count = available < 64 ? available : 64;
 const volatile uint64_t *stack_words = (const volatile uint64_t *)sp;
 for (size_t i = 0; i < count; ++i) {
  const uint64_t address = stack_words[i];
  if (address >= probe_text_low && address < probe_text_high) {
   value("PROBE STACK slot=", i);
   value("PROBE STACK image offset=", address - probe_text_low);
  }
 }
}
#endif
static void handler(int sig,siginfo_t *info,void *context){
 if(report_fd>=0 && (PS5_SHADERC_MAX_REPORTS==0 ||
       __atomic_fetch_add(&report_count,1u,__ATOMIC_RELAXED)<PS5_SHADERC_MAX_REPORTS)){
  value("SHADERC FAULT signal=",(unsigned)sig);
  value("SHADERC FAULT code=",info?(unsigned)info->si_code:0);
  value("SHADERC FAULT address=",info?(uintptr_t)info->si_addr:0);
  /* PS5's context layout is not assumed to match desktop FreeBSD. Preserve
   * the same bounded96-word region inspected by the pinned SDK signal probe. */
  if(context){
   const volatile uint64_t *words=(const volatile uint64_t*)context;
#ifdef PS5_SHADERC_PROBE_STACK
   report_probe_stack(words);
#endif
   for(unsigned i=0;i<PS5_SHADERC_CONTEXT_WORDS;i++){
    value("SHADERC FAULT context-index=",i);
    value("SHADERC FAULT context-word=",words[i]);
   }
  }
 }
 for(unsigned i=0;i<signal_count;i++)if(signals[i]==sig){
  if(previous[i].sa_handler==SIG_IGN)return;
  if(previous[i].sa_handler==SIG_DFL){
   (void)sigaction(sig,&previous[i],0);(void)raise(sig);return;
  }
  if(previous[i].sa_flags&SA_SIGINFO)previous[i].sa_sigaction(sig,info,context);
  else previous[i].sa_handler(sig);
  return;
 }
}
int ps5shaderc_fault_begin(void){
 guard_lock();
 if(users++==0){
  report_count=0;
  const char* root=getenv("PROSPERO_DIAGNOSTIC_ROOT");char path[640];
  int n=root&&root[0]?snprintf(path,sizeof(path),"%s/java25-vm-trace.log",root):0;
  report_fd=root&&root[0]?(n>0&&(unsigned)n<sizeof(path)?open(path,O_WRONLY|O_CREAT|O_APPEND,0600):-1):open(PS5_SHADERC_FAULT_LOG,O_WRONLY|O_CREAT|O_APPEND,0600);
  for(unsigned i=0;i<signal_count;i++){
   installed[i]=0;
   if(sigaction(signals[i],0,&previous[i])!=0)continue;
   struct sigaction action=previous[i];
   action.sa_sigaction=handler;action.sa_flags|=SA_SIGINFO;
   installed[i]=sigaction(signals[i],&action,0)==0;
  }
 }
 int count=0;for(unsigned i=0;i<4;i++)count+=installed[i];
 guard_unlock();return report_fd>=0?count:-1;
}
void ps5shaderc_fault_end(void){
 guard_lock();
 if(users && --users==0){
  for(unsigned i=0;i<signal_count;i++)if(installed[i]){
   struct sigaction current;
   if(sigaction(signals[i],0,&current)==0 && current.sa_sigaction==handler)
    (void)sigaction(signals[i],&previous[i],0);
   installed[i]=0;
  }
  if(report_fd>=0)(void)close(report_fd);
  report_fd=-1;
 }
 guard_unlock();
}

/* Read-only ownership observation; never reinstall a displaced handler. */
static unsigned fault_status(unsigned *query_errors,unsigned count){
 int saved_errno=errno;unsigned owned=0,errors=0;
 guard_lock();
 for(unsigned i=0;i<count;i++){
  struct sigaction current;
  if(sigaction(signals[i],0,&current)!=0)errors|=1u<<i;
  else if(installed[i]&&(current.sa_flags&SA_SIGINFO)&&current.sa_sigaction==handler)owned|=1u<<i;
 }
 guard_unlock();
 if(query_errors)*query_errors=errors;
 errno=saved_errno;return owned;
}

unsigned ps5shaderc_fault_status(unsigned *errors){return fault_status(errors,4);}
unsigned ps5shaderc_fault_extended_status(unsigned *errors){return fault_status(errors,signal_count);}
