#!/usr/bin/env python3
"""Offline failure controls for 26.1 publisher preparation and linkage parsing."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from host_toolchain import ROOT, java_home
from prepare_client_261 import allowed, artifact_path, publisher_url, validate_metadata, verified
from audit_client_261 import class_info, jni_mangle


def rejects(action, error=ValueError):
    try:
        action()
    except error:
        return
    raise AssertionError('Expected rejection')


def main():
    with tempfile.TemporaryDirectory(prefix='prospero-261-inputs-') as temporary:
        directory = Path(temporary)
        content = b'publisher fixture'
        pin = {'url': 'https://piston-data.mojang.com/fixture',
               'sha1': hashlib.sha1(content).hexdigest(), 'size': len(content)}
        path = directory / 'verified.jar'
        def no_network(url):
            raise AssertionError('Unexpected network request')
        rejects(lambda: verified(pin, path, offline=True, transport=no_network), FileNotFoundError)
        rejects(lambda: verified(pin, path, transport=lambda url: b'corrupt'))
        assert not path.exists() and not list(directory.glob('*.part'))
        assert verified(pin, path, transport=lambda url: content) == content
        assert verified(pin, path, offline=True, transport=no_network) == content
        path.write_bytes(b'corrupt cached input')
        rejects(lambda: verified(pin, path, transport=no_network))
        assert path.read_bytes() == b'corrupt cached input'
        rejects(lambda: verified({**pin, 'size': True}, path, transport=no_network))
        for url in ('http://piston-data.mojang.com/a', 'https://example.com/a',
                    'https://piston-data.mojang.com.evil.invalid/a',
                    'https://user@piston-data.mojang.com/a',
                    'https://piston-data.mojang.com:443/a'):
            rejects(lambda: publisher_url(url))
        for name in ('../escape.jar', '/absolute.jar', 'a\\b.jar', 'a/../../b', 'a\0b', 'C:/file'):
            rejects(lambda: artifact_path(name))
        assert artifact_path('org/lwjgl/test.jar') == Path('org/lwjgl/test.jar')
        assert allowed({})
        assert not allowed({'rules': [{'action': 'allow', 'os': {'name': 'osx'}}]})
        assert not allowed({'rules': [{'action': 'allow'}, {'action': 'disallow', 'os': {'name': 'linux'}}]})
        assert allowed({'rules': [{'action': 'disallow'}, {'action': 'allow', 'os': {'name': 'linux'}}]})
        assert not allowed({'rules': [{'action': 'allow', 'features': {'demo': True}}]})
        # Real javac fixture, covering long/double two-slot constants, method
        # and field references, array descriptors and static/instance JNI ABI.
        package = directory / 'org/lwjgl'
        package.mkdir(parents=True)
        source = package / 'Fixture.java'
        source.write_text('''package org.lwjgl;
public class Fixture {
 public static final long LONG=123456789012345L;
 public static final double DOUBLE=123.456;
 public static int value;
 public native long instanceNative(int[] values);
 public static native void staticNative(long value);
 public static int call(){staticNative(LONG);return value;}
}
''')
        jdk = java_home()
        subprocess.run([str(jdk / 'bin/javac'), '--release', '25', '-d', str(directory), str(source)], check=True, timeout=60)
        refs, natives = class_info((package / 'Fixture.class').read_bytes())
        assert ('10', 'org.lwjgl.Fixture', 'staticNative', '(J)V') in refs
        assert ('9', 'org.lwjgl.Fixture', 'value', 'I') in refs
        assert natives == {('org/lwjgl/Fixture', 'instanceNative', '([I)J', False),
                           ('org/lwjgl/Fixture', 'staticNative', '(J)V', True)}
        assert jni_mangle('org/lwjgl/Test_name') == 'org_lwjgl_Test_1name'
        assert jni_mangle('[Ljava/lang/String;') == '_3Ljava_lang_String_2'
        rejects(lambda: class_info(b'not a class'))
        # Validate the actual draft inventory without fetching publisher inputs.
        rows = json.loads((ROOT / 'client/26.1.lock.json').read_text())['versions']
        assert len(rows) == len({row['id'] for row in rows})
        for row in rows:
            meta = {'id': row['id'], 'type': 'release', 'javaVersion': {'majorVersion': 25},
                    'mainClass': 'net.minecraft.client.main.Main', 'assetIndex': {'id': row['assetIndex']},
                    'downloads': {'client': row['client']}, 'libraries': [{'name': n} for n in row['lwjgl']]}
            validate_metadata(row, json.dumps(meta))
            meta['javaVersion']['majorVersion'] = 26
            rejects(lambda: validate_metadata(row, json.dumps(meta)))
    print('PASS offline 26.1 input integrity, failure preservation, publisher rules and actual class/JNI parsing')


if __name__ == '__main__':
    main()
