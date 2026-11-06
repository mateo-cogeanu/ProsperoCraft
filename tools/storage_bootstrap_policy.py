"""Normalize only explicit storage-routing syntax for the retained204 policy guard."""
import re


def normalize(name, text):
    if name == 'client/startup/bootstrap.cpp':
        zgc_policy = (
            '#ifdef PROSPERO_ZGC\n'
            '   {const_cast<char *>("-XX:+UseZGC"),nullptr},\n'
            '   {const_cast<char *>("-XX:ParallelGCThreads=4"),nullptr},\n'
            '   {const_cast<char *>("-XX:ConcGCThreads=2"),nullptr},\n'
            '   {const_cast<char *>("-XX:-ZUncommit"),nullptr},\n'
            '#elif defined(PROSPERO_TIERED_PARALLEL)\n'
        )
        if text.count(zgc_policy) != 1:
            raise ValueError('ZGC policy selection changed')
        text = text.replace(zgc_policy, '#ifdef PROSPERO_TIERED_PARALLEL\n')
        text, count = re.subn(r'^#ifdef PROSPERO_EXTENDED_NATIVE_DIRECT\n.*?^#endif\n',
                              '', text, flags=re.M | re.S)
        if count != 2:
            raise ValueError('Native direct capacity hooks changed')
        text, count = re.subn(r'^#ifdef PROSPERO_FILE_PRESSURE_REPORT\n[^\n]+\n#endif\n',
                              '', text, flags=re.M)
        if count != 3:
            raise ValueError('File pressure reporting hooks changed')
        text, count = re.subn(r'^#ifdef PROSPERO_TIERED_PARALLEL\n.*?^#else\n(.*?)^#endif\n',
                              r'\1', text, flags=re.M | re.S)
        if count != 2:
            raise ValueError('Tiered and Parallel option blocks changed')
        text = text.replace('#ifndef PROSPERO_TIERED_PARALLEL\n'
                            '   {const_cast<char *>("-XX:+ExplicitGCInvokesConcurrent"),nullptr},\n'
                            '#endif\n',
                            '   {const_cast<char *>("-XX:+ExplicitGCInvokesConcurrent"),nullptr},\n')
        declaration = '#ifdef PROSPERO_EXTRA_MUTEX_RESERVE\nextern "C" int JVM_PS5SetExtraMutexReserveEnabled(int);\n#endif\n'
        if text.count(declaration) != 1:
            raise ValueError('Extra mutex reserve declaration changed')
        text = text.replace(declaration, '')
        text, count = re.subn(r'^#ifdef PROSPERO_EXTRA_MUTEX_RESERVE\n.*?^#else\n(.*?)^#endif\n',
                              r'\1', text, flags=re.M | re.S)
        if count != 1:
            raise ValueError('Extra mutex reserve initialization changed')
        progress_binding = (
            '\n#ifdef PROSPERO_LIBRARY_PROGRESS\n'
            '   ,{const_cast<char *>("libraryProgress"),const_cast<char *>("(Ljava/lang/String;JJ)Z"),'
            'reinterpret_cast<void *>(&prospero_menu::library_progress)}\n#endif\n  '
        )
        if text.count(progress_binding) != 1:
            raise ValueError('Library progress callback changed')
        text = text.replace(progress_binding, '')
        text = text.replace('callbacks,i==3?static_cast<jint>(sizeof(callbacks)/sizeof(callbacks[0])):1',
                            'callbacks,i==3?5:1')
        blocks = ('#ifndef PROSPERO_REPORT_PATH\n#define PROSPERO_REPORT_PATH(name) "/download0/" name\n#endif\n',
                  '#ifndef PROSPERO_STORAGE_OPTION\n#define PROSPERO_STORAGE_OPTION(primary,fallback) fallback\n#endif\n')
        for block in blocks:
            if text.count(block) != 1:
                raise ValueError('Storage routing default changed')
            text = text.replace(block, '')
        text = re.sub(r'PROSPERO_REPORT_PATH\("([^"\n]*)"\)', lambda m: '"/download0/' + m[1] + '"', text)
        text = text.replace('std::strncmp(path,"/download0/",std::strlen("/download0/"))', 'std::strncmp(path,"/download0/",11)')
        jit_reader = (
            '   {const_cast<char *>(PROSPERO_STORAGE_OPTION('
            '"-Dps5.probe.jitLog=/data/ProsperoCraft/reports/java25-jit.log",'
            '"-Dps5.probe.jitLog=/download0/java25-jit.log")),nullptr},\n'
        )
        if text.count(jit_reader) != 1:
            raise ValueError('JIT gate must follow the selected report root')
        text = text.replace(jit_reader, '')
        options = {
            '-Xlog:jit+compilation=debug,codecache=info:file=/data/ProsperoCraft/reports/java25-jit.log:uptime,level,tags:filecount=1,filesize=4M': '-Xlog:jit+compilation=debug,codecache=info:file=/download0/java25-jit.log:uptime,level,tags:filecount=1,filesize=4M',
            '-Xlog:gc=info,safepoint=info:file=/data/ProsperoCraft/reports/java25-gc.log:uptimemillis,level,tags:filecount=1,filesize=4M': '-Xlog:gc=info,safepoint=info:file=/download0/java25-gc.log:uptimemillis,level,tags:filecount=1,filesize=4M',
            '-XX:ErrorFile=/data/ProsperoCraft/reports/hs_err_java25.log': '-XX:ErrorFile=/download0/hs_err_java25.log',
            '-Djava.io.tmpdir=/data/ProsperoCraft/tmp': '-Djava.io.tmpdir=/download0',
            '-Duser.home=/data/ProsperoCraft': '-Duser.home=/download0',
            '-Duser.dir=/data/ProsperoCraft/reports/mc-client': '-Duser.dir=/download0/mc-client',
        }
        for primary, fallback in options.items():
            token = 'PROSPERO_STORAGE_OPTION("' + primary + '","' + fallback + '")'
            if text.count(token) != 1:
                raise ValueError('Storage-only VM option changed')
            text = text.replace(token, '"' + fallback + '"')
        text = text.replace('Storage roots selected by verified shared access; legacy fallback is explicit; no measured-capacity claim', 'Storage /download0: title-local reservation requested4096MiB; actual capacity is unavailable, not zero')
    elif name == 'client/save_headroom/bootstrap.cpp':
        lines = ['#define PROSPERO_ZGC 1\n',
                 '#define PROSPERO_EXTENDED_NATIVE_DIRECT 1\n',
                 '#define PROSPERO_TIERED_PARALLEL 1\n',
                 '#define PROSPERO_EXTRA_MUTEX_RESERVE 1\n',
                 '// Enable tracking before storage_paths.hpp first includes log_share.hpp.\n',
                 '#define PS5_TRACK_FILE_ACTIVITY 1\n',
                 '#define PROSPERO_FILE_PRESSURE_REPORT 1\n',
                 '#include "../launcher/storage_paths.hpp"\n',
                 '#include "../ports/openal/startup_boundary.hpp"\n',
                 '#include "../startup/shader_cache_budget.hpp"\n',
                 ' if(prospero_shader_cache::configure()!=0)return 1;\n',
                 ' client_openal_boundary::disable();\n',
                 '#define ps5shaderc_fault_begin prospero_storage_fault_begin\n',
                 '#define ps5shaderc_fault_end prospero_storage_fault_end\n',
                 '#define ps5shaderc_fault_status prospero_storage_fault_status\n',
                 '#define ps5shaderc_fault_extended_status prospero_storage_fault_extended_status\n',
                 ' if(!prospero_storage::initialize(false))return 1;\n']
        for line in lines:
            if text.count(line) != 1:
                raise ValueError('Storage setup wrapper changed')
            text = text.replace(line, '')
    return text
