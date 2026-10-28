#!/usr/bin/env python3
"""Consumer integration for the runtime-owned genuine JNA dispatch builder."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
def build(runtime,offline=False):
 spec=importlib.util.spec_from_file_location('java25_jna',runtime/'tools/java25_jna.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 obj=module.build(ROOT/'build/libffi-ps5/target/include',offline=offline)
 return obj,json.loads((obj.parent/'audit.json').read_text()),obj.parent/'source'
