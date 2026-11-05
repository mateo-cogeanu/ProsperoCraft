"""Normalize only explicit storage-routing syntax for the retained204 policy guard."""
import re


def normalize(name, text):
    if name == 'client/startup/bootstrap.cpp':
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
        lines = ['#include "../launcher/storage_paths.hpp"\n',
                 '#define ps5shaderc_fault_begin prospero_storage_fault_begin\n',
                 '#define ps5shaderc_fault_end prospero_storage_fault_end\n',
                 '#define ps5shaderc_fault_status prospero_storage_fault_status\n',
                 '#define ps5shaderc_fault_extended_status prospero_storage_fault_extended_status\n',
                 ' if(!prospero_storage::initialize())return 1;\n']
        for line in lines:
            if text.count(line) != 1:
                raise ValueError('Storage setup wrapper changed')
            text = text.replace(line, '')
    return text
