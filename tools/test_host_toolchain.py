#!/usr/bin/env python3
"""Regression checks for discovery precedence and fail-closed dependency handling."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import host_toolchain as h


class Discovery(unittest.TestCase):
    def test_explicit_and_environment_jdk(self):
        actual = h.java_home()
        with patch.dict(os.environ, {'JAVA_HOME': '/missing/jdk'}):
            self.assertEqual(h.java_home(actual), actual)
            with self.assertRaisesRegex(RuntimeError, 'Incomplete JDK'):
                h.java_home()

    def test_missing_and_unsupported(self):
        with patch.dict(os.environ, {'PATH': '', 'LLVM_HOME': '', 'HOMEBREW_PREFIX': ''}, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'Missing javac'):
                h.java_home()
        actual = h.java_home()
        for output in ('javac 21.0.8', 'javac 26-ea'):
            with patch.object(h.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, output, '')):
                with self.assertRaisesRegex(RuntimeError, 'require JDK 25'):
                    h.java_home(actual)

    def test_tool_precedence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('explicit', 'environment', 'llvm/bin/clang', 'path/clang', 'brew/bin/clang'):
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('#!/bin/sh\nexit 0\n')
                p.chmod(0o755)
            with patch.dict(os.environ, {'CC': str(root/'environment'), 'LLVM_HOME': str(root/'llvm'),
                                        'PATH': str(root/'path'), 'HOMEBREW_PREFIX': str(root/'brew')}, clear=True):
                self.assertEqual(h.executable('clang', override=root/'explicit', env='CC'), str(root/'explicit'))
                self.assertEqual(h.executable('clang', env='CC'), str(root/'environment'))
                del os.environ['CC']
                self.assertEqual(h.executable('clang', env='CC'), str(root/'llvm/bin/clang'))
                del os.environ['LLVM_HOME']
                self.assertEqual(h.executable('clang'), str(root/'path/clang'))
                os.environ['PATH'] = ''
                self.assertEqual(h.executable('clang'), str(root/'brew/bin/clang'))
                os.environ['CC'] = '/missing/compiler'
                with self.assertRaisesRegex(RuntimeError, 'unavailable executable'):
                    h.executable('clang', env='CC')

    def test_jni_platform_and_library(self):
        home = h.java_home()
        self.assertTrue(h.jni_flags(home))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('jni.h', 'linux/jni_md.h', 'darwin/jni_md.h'):
                p = root/'include'/name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.touch()
            for system, suffix, flag in [('Linux', '.so', '-shared'), ('Darwin', '.dylib', '-dynamiclib')]:
                with patch.object(h.platform, 'system', return_value=system):
                    self.assertEqual(len(h.jni_flags(root)), 2)
                    self.assertTrue(h.library_name('test').endswith(suffix))
                    self.assertIn(flag, h.shared_flags())
            (root/'include/linux/jni_md.h').unlink()
            with patch.object(h.platform, 'system', return_value='Linux'):
                with self.assertRaisesRegex(RuntimeError, 'Missing JNI header'):
                    h.jni_flags(root)

    def test_private_cache_not_used(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'PROSPERO_HOST_DEPS': directory}):
            with self.assertRaisesRegex(RuntimeError, 'Missing host dependency'):
                h.dependency('gson')
            pin = json.loads((h.ROOT/'tests/host-dependencies.json').read_text())['gson']
            (Path(directory)/pin['file']).write_bytes(b'corrupt')
            with self.assertRaisesRegex(RuntimeError, 'checksum/size mismatch'):
                h.dependency('gson')


if __name__ == '__main__':
    unittest.main()
