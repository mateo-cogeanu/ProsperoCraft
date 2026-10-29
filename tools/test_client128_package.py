#!/usr/bin/env python3
"""Audit actual128GLFW/TinyFD native exports, routing and packaged source."""
from pathlib import Path
import zipfile,json,hashlib,subprocess,re
ROOT=Path(__file__).resolve().parents[1]
elf=ROOT/'build/client-startup-probe/bootstrap-01.000.128-symbols.elf'
exports=set(line.split()[-1]for line in subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','--defined-only',str(elf)],text=True).splitlines()if line.split())
functions=subprocess.check_output(['/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home/bin/javap','-classpath',str(ROOT/'build/version122-research/lwjgl-glfw-3.4.1.jar'),'-c','-p','org.lwjgl.glfw.GLFW$Functions'],text=True)
required=[name for name,kind in re.findall(r'// String (glfw\w+)\n\s+\d+: invokestatic[^\n]+// Method org/lwjgl/system/APIUtil\.(apiGetFunctionAddress\w*)',functions)if kind=='apiGetFunctionAddress']
assert len(required)==118 and set(required)<=exports
for name in ['glfwCreateWindowSurface','glfwVulkanSupported','glfwInitVulkanLoader','glfwGetRequiredInstanceExtensions','glfwSetPreeditCallback','glfwSetIMEStatusCallback','glfwSetPreeditCursorRectangle','ps5_builtin_load_ps5glfw','ps5_builtin_load_lwjgl_tinyfd','Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1getGlobalChar']:assert name in exports,name
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 assert package.testzip()is None;prefix='PPSA99874/assets/java25/';audit=json.loads(package.read(prefix+'glfw-audit.json'))
 for name,digest in audit['local_source_sha256'].items():assert hashlib.sha256(package.read(prefix+'glfw-source/'+name)).hexdigest()==digest==hashlib.sha256((ROOT/'client/ports/glfw'/name).read_bytes()).hexdigest()
 scratch=json.loads(package.read(prefix+'core-scratch-runtime-audit.json'));runtime=ROOT.parents[2]
 assert scratch['runtime']==json.loads((ROOT/'client/ports/core-scratch-runtime.json').read_text())
 assert hashlib.sha256(package.read(prefix+'lib/libjava.so')).hexdigest()==scratch['libjava_sha256']
 for name,digest in scratch['objects_sha256'].items():assert hashlib.sha256((runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/native/java.base/libjava'/name).read_bytes()).hexdigest()==digest
 assert hashlib.sha256(package.read(prefix+'lib/libverify.so')).hexdigest()==scratch['libverify_sha256']
 assert hashlib.sha256((runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/native/java.base/libverify/check_code.o').read_bytes()).hexdigest()==scratch['verifier_object_sha256']
 assert 'JNU_PS5SetVerifierSmallReserveEnabled' in exports
 assert 'JNU_PS5SetDirectScratchEnabled' in exports
 assert package.read(prefix+'tinyfd-source/ps5_dialogs.c')==(ROOT/'client/ports/tinyfd/ps5_dialogs.c').read_bytes()
 binding=prefix+'ports/lwjgl-glfw-3.4.1-ps5-callback343.jar';binding_audit=json.loads(package.read(prefix+'glfw-binding-audit.json'))
 assert hashlib.sha256(package.read(binding)).hexdigest()==binding_audit['output_sha256']
 assert len(binding_audit['changed_source_units'])==26
 assert package.read(binding)==(ROOT/'build/client-ports/glfw/lwjgl-glfw-3.4.1-ps5-callback343.jar').read_bytes()
 assert b'ps5glfw'in package.read(prefix+'classes/ClientStartup25.class') and b'selectedGlfw'in package.read(prefix+'classes/ClientStartup25.class')
sdl=ROOT/'build/sdl3-native/resident-sdl.o'
undefined={line.split()[-1] for line in subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-u',str(sdl)],text=True).splitlines() if line.split()}
assert not any(name.startswith('pthread_rwlock_') for name in undefined),undefined
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip') as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/sdl-audit.json'))
 for name in ['SDL_ps5rwlock.c','0002-ps5-rwlock.patch']:
  assert audit['port_sha256'][name]==hashlib.sha256((ROOT/'client/ports/sdl'/name).read_bytes()).hexdigest()
print('PASS actual128 rebuilt runtime127+129 libjava/libverify/object hashes and explicit enablement; all118GLFW exports, callbacks/TinyFD/source/CRC preserved; PS5 SDL allocation-free RWLock source/pin and no pthread_rwlock imports; Fabric validation pending')
