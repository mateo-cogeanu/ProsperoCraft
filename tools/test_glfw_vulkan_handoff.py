#!/usr/bin/env python3
"""Original26.2Vulkan bootstrap succeeds after direct native GLFW loader setup."""
from pathlib import Path
import json,subprocess,tempfile,os
ROOT=Path(__file__).resolve().parents[1];JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
source=r'''
import org.lwjgl.system.*;import org.lwjgl.glfw.*;import org.lwjgl.vulkan.*;
public class LoaderCheck {
 public static void main(String[] args)throws Exception{
  System.load(args[0]);System.load(args[3]);Configuration.MEMORY_ALLOCATOR.set("system");Configuration.VULKAN_EXPLICIT_INIT.set(true);Configuration.GLFW_LIBRARY_NAME.set(args[1]);Configuration.VULKAN_LIBRARY_NAME.set(args[2]);
  // Match original26.2 explicit loader ownership. The direct native GLFW
  // entry avoids GLFWVulkan Java initialization on every platform.
  try(SharedLibrary nativeLoader=Library.loadNative(LoaderCheck.class,"test-vulkan",args[2])){
   long address=nativeLoader.getFunctionAddress("vkGetInstanceProcAddr");if(address==0)throw new AssertionError("Missing real Vulkan entry");
   JNI.invokePV(address,GLFW.getLibrary().getFunctionAddress("glfwInitVulkanLoader"));
   var field=VK.class.getDeclaredField("functionProvider");field.setAccessible(true);if(field.get(null)!=null)throw new AssertionError("GLFW setup initialized VK");
   Class<?> original=Class.forName("com.mojang.blaze3d.platform.NativeLibrariesBootstrap");var method=original.getDeclaredMethod("tryLoadingVulkan");method.setAccessible(true);
   if(!Boolean.TRUE.equals(method.invoke(null)))throw new AssertionError("Original26.2Vulkan bootstrap failed");
   if(VK.getInstanceVersionSupported()==0)throw new AssertionError("No actual Vulkan global capabilities");
   try{VK.create();throw new AssertionError("Expected duplicate-create guard");}catch(IllegalStateException expected){if(!expected.getMessage().contains("already"))throw expected;}
   VK.destroy();
  }
  System.out.println("PASS direct native GLFW loader setup leaves VK uninitialized; actual original26.2tryLoadingVulkan succeeds with real lavapipe loader; duplicate-create reproducer and cleanup verified. Host only.");
 }
}'''
with tempfile.TemporaryDirectory()as d:
 w=Path(d);(w/'LoaderCheck.java').write_text(source);(w/'loader.c').write_text('extern void* vk_icdGetInstanceProcAddr(void*,const char*);void* vkGetInstanceProcAddr(void*i,const char*n){return vk_icdGetInstanceProcAddr(i,n);}\n')
 dynamic=w/'libhost-dl.dylib';subprocess.run(['clang','-dynamiclib','-DLWJGL_MACOS','-I'+str(ROOT/'.tools/lwjgl-native-src'),'-I'+str(JDK/'include'),'-I'+str(JDK/'include/darwin'),str(ROOT/'.tools/lwjgl-native-src/org_lwjgl_system_macosx_DynamicLinkLoader.c'),'-o',str(dynamic)],check=True)
 lib=w/'libvulkan-test.dylib';subprocess.run(['clang','-dynamiclib',str(w/'loader.c'),'/opt/homebrew/lib/libvulkan_lvp.dylib','-o',str(lib)],check=True)
 receipt=json.loads((ROOT/'build/version122-test/cache/versions/26.2/receipt.json').read_text());parent=[ROOT/'.tools/client'/a['file']for a in json.loads((ROOT/'client/26.3.lock.json').read_text())['artifacts']if a['id'].startswith(('org.lwjgl:','com.google.code.gson:'))]
 cp=':'.join(map(str,[w,*parent,ROOT/'build/client-ports/glfw/lwjgl-glfw-3.4.1-ps5-callback343.jar',*[ROOT/'build/version122-test/cache'/p for p in receipt['classpath']]]))
 subprocess.run([str(JDK/'bin/javac'),'-cp',cp,str(w/'LoaderCheck.java')],check=True)
 subprocess.run([str(JDK/'bin/java'),'--enable-native-access=ALL-UNNAMED','-Dorg.lwjgl.librarypath='+str(ROOT/'build/client-ports/lwjgl-native/host'),'-cp',cp,'LoaderCheck',str(ROOT/'build/libffi-host/liblwjglffi.dylib'),str(ROOT/'build/glfw-native/host/libps5glfw.dylib'),str(lib),str(dynamic)],check=True,timeout=45,env=dict(os.environ,UBSAN_OPTIONS='handle_segv=0:handle_sigbus=0:handle_sigfpe=0:halt_on_error=1',ASAN_OPTIONS='detect_leaks=0:handle_segv=0:handle_sigbus=0:handle_sigfpe=0',DYLD_INSERT_LIBRARIES=subprocess.check_output(['clang','-print-file-name=libclang_rt.asan_osx_dynamic.dylib'],text=True).strip()))
# Guard production setup against reintroducing the exact early init call.
text=(ROOT/'client/startup/ClientStartup25.java').read_text();setup=text.split('if(ProsperoLauncher.selectedGlfw()){',1)[1].split('stage("Menu inactivity',1)[0];assert 'PS5Library' in setup and 'org.lwjgl.vulkan.VK.'not in setup and 'getFunctionAddress("vkGetInstanceProcAddr")' in setup
