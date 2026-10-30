#!/usr/bin/env python3
"""Compatibility entrypoint for the now-supported Fabric26.2 policy checks."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('test_launcher_desktop.py')),run_name='__main__')
