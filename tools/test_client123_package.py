#!/usr/bin/env python3
"""Audit actual123GLFW/TinyFD native exports, routing and packaged source."""
from pathlib import Path
import zipfile,json,hashlib,subprocess,re
ROOT=Path(__file__).resolve().parents[1]
elf=ROOT/'build/client-startup-probe/bootstrap-01.000.123-symbols.elf'
exports=set(line.split()[-1]for line in subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','--defined-only',str(elf)],text=True).splitlines()if line.split())
functions=subprocess.check_output(['/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home/bin/javap','-classpath',str(ROOT/'build/version122-research/lwjgl-glfw-3.4.1.jar'),'-c','-p','org.lwjgl.glfw.GLFW$Functions'],text=True)
required=[name for name,kind in re.findall(r'// String (glfw\w+)\n\s+\d+: invokestatic[^\n]+// Method org/lwjgl/system/APIUtil\.(apiGetFunctionAddress\w*)',functions)if kind=='apiGetFunctionAddress']
assert len(required)==118 and set(required)<=exports
for name in ['glfwCreateWindowSurface','glfwVulkanSupported','glfwInitVulkanLoader','glfwGetRequiredInstanceExtensions','glfwSetPreeditCallback','glfwSetIMEStatusCallback','glfwSetPreeditCursorRectangle','ps5_builtin_load_ps5glfw','ps5_builtin_load_lwjgl_tinyfd','Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1getGlobalChar']:assert name in exports,name
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 assert package.testzip()is None;prefix='PPSA99874/assets/java25/';audit=json.loads(package.read(prefix+'glfw-audit.json'))
 for name,digest in audit['local_source_sha256'].items():assert hashlib.sha256(package.read(prefix+'glfw-source/'+name)).hexdigest()==digest==hashlib.sha256((ROOT/'client/ports/glfw'/name).read_bytes()).hexdigest()
 assert package.read(prefix+'tinyfd-source/ps5_dialogs.c')==(ROOT/'client/ports/tinyfd/ps5_dialogs.c').read_bytes()
 binding=prefix+'ports/lwjgl-glfw-3.4.1-ps5-callback343.jar';binding_audit=json.loads(package.read(prefix+'glfw-binding-audit.json'))
 assert hashlib.sha256(package.read(binding)).hexdigest()==binding_audit['output_sha256']
 assert len(binding_audit['changed_source_units'])==26
 assert package.read(binding)==(ROOT/'build/client-ports/glfw/lwjgl-glfw-3.4.1-ps5-callback343.jar').read_bytes()
 assert b'ps5glfw'in package.read(prefix+'classes/ClientStartup25.class') and b'selectedGlfw'in package.read(prefix+'classes/ClientStartup25.class')
print('PASS actual123 all118required GLFW APIs, Vulkan/IME bridge and TinyFD JNI groups linked; exact sources/CRC/launch routing; no PS5 pass inferred')
