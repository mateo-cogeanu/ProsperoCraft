#!/usr/bin/env python3
"""Read-only publisher/binding audit; not GL execution or a supported host lane.

Requires prepare_client_261.py inputs, explicitly selected parent cache, rebuilt
GLFW callback binding and existing target OpenGL JNI object. Writes research
reports only. Never initializes LWJGL, rewrites JARs or changes launcher support.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import zipfile

from host_toolchain import ROOT, executable, java_home
from prepare_client_261 import allowed, artifact_path, validate_metadata, verified


def class_info(data):
    """Constant-pool linkage references and declared native method descriptors."""
    if data[:4] != b'\xca\xfe\xba\xbe':
        raise ValueError('Not a Java class')
    pos = 8
    def u2():
        nonlocal pos
        value = struct.unpack_from('>H', data, pos)[0]
        pos += 2
        return value
    count = u2()
    cp = [None] * count
    index = 1
    while index < count:
        tag = data[pos]
        pos += 1
        if tag == 1:
            size = u2()
            cp[index] = data[pos:pos + size].decode('utf-8', 'replace')
            pos += size
        elif tag in (3, 4):
            pos += 4
        elif tag in (5, 6):
            pos += 8
            index += 1
        elif tag in (7, 8, 16, 19, 20):
            cp[index] = (tag, u2())
        elif tag in (9, 10, 11, 12, 17, 18):
            cp[index] = (tag, u2(), u2())
        elif tag == 15:
            pos += 3
        else:
            raise ValueError('Unknown constant tag: ' + str(tag))
        index += 1
    references = set()
    for item in cp:
        if isinstance(item, tuple) and item[0] in (9, 10, 11):
            owner = cp[cp[item[1]][1]]
            name = cp[item[2]]
            if owner.startswith('org/lwjgl/'):
                references.add((str(item[0]), owner.replace('/', '.'), cp[name[1]], cp[name[2]]))
    u2()  # access
    owner = cp[cp[u2()][1]]
    u2()  # super
    for _ in range(u2()):
        u2()
    def member():
        nonlocal pos
        access, name, desc = u2(), cp[u2()], cp[u2()]
        for _ in range(u2()):
            u2()
            length = struct.unpack_from('>I', data, pos)[0]
            pos += 4 + length
        return access, name, desc
    for _ in range(u2()):
        member()
    natives = set()
    for _ in range(u2()):
        access, name, desc = member()
        if access & 0x100:
            natives.add((owner, name, desc, bool(access & 8)))
    return references, natives


def jar_info(path):
    refs, natives = set(), set()
    with zipfile.ZipFile(path) as jar:
        for name in jar.namelist():
            if name.endswith('.class') and not name.startswith('META-INF/'):
                r, n = class_info(jar.read(name))
                refs.update(r)
                natives.update(n)
    return refs, natives


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jni_mangle(value):
    out = ''
    for char in value:
        if char.isascii() and char.isalnum():
            out += char
        elif char == '/':
            out += '_'
        elif char in '_;[':
            out += {'_': '_1', ';': '_2', '[': '_3'}[char]
        else:
            out += '_0' + format(ord(char), '04x')
    return out


RESOLVE_JAVA = r'''
import java.lang.invoke.*;
import java.lang.reflect.*;
import java.nio.file.*;
public class Resolve261 {
 static Method method(Class<?> owner,String name,Class<?>[] params) throws NoSuchMethodException {
  for(Class<?> type=owner;type!=null;type=type.getSuperclass()) {
   try{return type.getDeclaredMethod(name,params);}catch(NoSuchMethodException inherited){}
  }
  return owner.getMethod(name,params);
 }
 static Field field(Class<?> owner,String name) throws NoSuchFieldException {
  for(Class<?> type=owner;type!=null;type=type.getSuperclass()) {
   try{return type.getDeclaredField(name);}catch(NoSuchFieldException inherited){}
  }
  return owner.getField(name);
 }
 public static void main(String[] args) throws Exception {
  int methods=0,fields=0;
  for(String line:Files.readAllLines(Path.of(args[0]))) {
   String[] r=line.split("\t");
   Class<?> owner=Class.forName(r[1],false,Resolve261.class.getClassLoader());
   if(r[0].equals("9")) {
    Field f=field(owner,r[2]);
    Class<?> type=MethodType.fromMethodDescriptorString("()"+r[3],owner.getClassLoader()).returnType();
    if(f.getType()!=type)throw new AssertionError("Field ABI: "+r[1]+" "+r[2]); fields++;
   } else {
    MethodType type=MethodType.fromMethodDescriptorString(r[3],owner.getClassLoader());
    if(r[2].equals("<init>")) owner.getDeclaredConstructor(type.parameterArray());
    else {
     Method m=method(owner,r[2],type.parameterArray());
     if(m.getReturnType()!=type.returnType())throw new AssertionError("Return ABI: "+r[1]+" "+r[2]);
    } methods++;
   }
  }
  System.out.println("Resolved "+methods+" method and "+fields+" field descriptors; no native initialization");
 }
}
'''


def audit(args):
    jdk = java_home(args.java_home)
    cache, parent_dir = args.cache_dir.resolve(), args.parent_dir.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    rows = json.loads((ROOT / 'client/26.1.lock.json').read_text())['versions']
    # Verify original parent inputs, then use the same parent-first module
    # ownership as the actual launcher. Platform/GL overlays are not initialized.
    parents = []
    parent_opengl = None
    parent_pins = []
    for row in json.loads((ROOT / 'client/26.3.lock.json').read_text())['artifacts']:
        if row['id'].startswith(('org.lwjgl:', 'org.jspecify:')) and ':natives-' not in row['id']:
            path = parent_dir / row['file']
            verified(row, path, offline=True)
            if digest(path) != row['sha256']:
                raise ValueError('Parent SHA-256 mismatch: ' + row['file'])
            parents.append(path)
            parent_pins.append({'id': row['id'], 'sha256': digest(path)})
            if row['id'].startswith('org.lwjgl:lwjgl-opengl:'):
                parent_opengl = path
    if parent_opengl is None:
        raise ValueError('Missing pinned parent OpenGL module')
    binding = args.glfw_binding.resolve()
    binding_audit = json.loads(binding.with_name('audit.json').read_text())
    source_pin = json.loads((ROOT / 'client/ports/glfw/binding.json').read_text())
    if (binding_audit['source'] != source_pin or binding_audit['output_sha256'] != digest(binding)):
        raise ValueError('GLFW callback binding audit mismatch; rebuild binding')
    native_object = args.opengl_object.resolve()
    object_audit = json.loads(native_object.with_name('audit.json').read_text())
    if (object_audit['object_sha256'] != digest(native_object) or
            object_audit['sources'] != json.loads((ROOT / 'client/ports/opengl/native-sources.json').read_text())):
        raise ValueError('OpenGL object/source audit mismatch; rebuild JNI')
    nm = executable('llvm-nm', override=args.nm)
    exports = {line.split()[-1] for line in subprocess.check_output(
        [nm, '--defined-only', '--extern-only', str(native_object)], text=True).splitlines() if line.split()}
    parent_natives = jar_info(parent_opengl)[1]
    def core(native):
        return not native[0].split('/')[-1].startswith(('GLX', 'WGL'))
    for owner, name, desc, static in filter(core, parent_natives):
        short = 'Java_' + jni_mangle(owner) + '_' + jni_mangle(name)
        long = short + '__' + jni_mangle(desc[1:desc.index(')')])
        if short not in exports and long not in exports:
            raise ValueError('Missing actual JNI export: ' + long)
    source = out / 'Resolve261.java'
    source.write_text(RESOLVE_JAVA)
    subprocess.run([str(jdk / 'bin/javac'), '--release', '25', '-d', str(out), str(source)], check=True, timeout=60)
    cp = os.pathsep.join(map(str, [out, *parents, binding]))
    report = {'scope': 'Host read-only linkage audit; no GL/context/PS5 execution',
              'parent_inputs': parent_pins, 'glfw_binding_sha256': digest(binding),
              'opengl_object_sha256': digest(native_object),
              'parent_opengl_core_native_methods': len(list(filter(core, parent_natives))),
              'versions': []}
    for row in rows:
        metadata = cache / (row['id'] + '.json')
        meta = validate_metadata(row, verified(row['metadata'], metadata, offline=True))
        game = cache / (row['id'] + '-client.jar')
        verified(row['client'], game, offline=True)
        refs = jar_info(game)[0]
        game_refs = len(refs)
        child_paths = []
        original_gl = None
        for lib in meta['libraries']:
            if (':natives-' in lib['name'] or not allowed(lib) or
                    (lib['name'].startswith('io.netty:netty-transport-native-') and
                     len(lib['name'].split(':')) > 3)):
                continue
            artifact = lib.get('downloads', {}).get('artifact')
            if not artifact:
                continue
            path = cache / 'libraries' / artifact_path(artifact['path'])
            verified(artifact, path, offline=True)
            child_paths.append(path)
            if lib['name'].startswith('org.lwjgl:lwjgl-opengl:'):
                original_gl = path
        # Include internals of the adapted GLFW binding so the 123 callback
        # constructor omission cannot hide behind only auditing game call sites.
        refs.update(jar_info(binding)[0])
        references = out / (row['id'] + '-references.tsv')
        references.write_text(''.join('\t'.join(ref) + '\n' for ref in sorted(refs)))
        result = subprocess.run([str(jdk / 'bin/java'), '-Xverify:all', '-cp',
                                 cp + os.pathsep + os.pathsep.join(map(str, [game, *child_paths])),
                                 'Resolve261', str(references)], text=True, capture_output=True, timeout=90)
        if result.returncode:
            raise RuntimeError('Linkage failed for ' + row['id'] + ':\n' + result.stdout + result.stderr)
        original_natives = set(filter(core, jar_info(original_gl)[1]))
        missing = original_natives - parent_natives
        if missing:
            raise ValueError('Original OpenGL native descriptors differ; rebuild/review binding before integration: ' + row['id'])
        gl_classes = {}
        with zipfile.ZipFile(game) as jar:
            for name in jar.namelist():
                if not name.startswith('com/mojang/blaze3d/') or not name.endswith('.class'):
                    continue
                blob = jar.read(name)
                if any(needle in blob for needle in (b'org/lwjgl/opengl/', b'glfwWindowHint',
                       b'glfwCreateWindow', b'glfwMakeContextCurrent', b'glfwSwapInterval')):
                    gl_classes[name] = hashlib.sha256(blob).hexdigest()
        review_classes = ['com.mojang.blaze3d.' + name for name in (
            'opengl.GlBackend', 'opengl.GlDevice', 'opengl.BufferStorage',
            'opengl.BufferStorage$Immutable', 'opengl.BufferStorage$Mutable',
            'opengl.GlDebug', 'platform.Window', 'systems.RenderSystem')]
        disassembly = subprocess.check_output([str(jdk / 'bin/javap'), '-classpath', str(game),
                            '-c', '-p', '-constants', *review_classes], text=True, timeout=60)
        (out / (row['id'] + '-gl.javap.txt')).write_text(disassembly)
        # Record differences honestly; the actual parent-first path executes
        # parent GL Java+JNI, not the original child's OpenGL Java module.
        report['versions'].append({'id': row['id'], 'client_sha256': digest(game),
            'game_lwjgl_references': game_refs, 'game_and_adapted_glfw_references': len(refs),
            'resolution': result.stdout.strip(), 'original_opengl_core_native_methods': len(original_natives),
            'original_native_descriptors_missing_from_parent': sorted(missing),
            'game_capability_fields': sorted(ref[2] for ref in refs if ref[1] == 'org.lwjgl.opengl.GLCapabilities'),
            'gl_class_sha256': gl_classes})
        print(row['id'] + ': ' + result.stdout.strip() + '; original native ABI differences=' + str(len(missing)))
    (out / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--cache-dir', type=Path, default=ROOT / 'build/261-research')
    parser.add_argument('--parent-dir', type=Path, required=True)
    parser.add_argument('--glfw-binding', type=Path, required=True)
    parser.add_argument('--opengl-object', type=Path, required=True)
    parser.add_argument('--nm', help='llvm-nm executable; otherwise use portable discovery')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'build/261-audit')
    audit(parser.parse_args())


if __name__ == '__main__':
    main()
