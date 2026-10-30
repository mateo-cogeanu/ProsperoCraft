#!/usr/bin/env python3
"""Build the current client from source, including native graphics prerequisites.

Outputs are local build checks. This does not increment versions or publish a
release. Dependencies are provisioned by the existing pinned preparation tools.
Use a separate checkout/runtime workspace to preserve tested build outputs.
"""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-workspace', type=Path, required=True)
    parser.add_argument('--java-home', type=Path, required=True)
    args = parser.parse_args()
    runtime = args.runtime_workspace.resolve()
    common = ['--runtime-workspace', str(runtime)]
    # The current consumer linker uses the generated recipe, import declarations
    # and complete upstream notices from the native graphics build. A prior
    # frozen source folder or a prior developer build must not supply them.
    for script, options in [
        ('prepare_client_graphics.py', common),
        ('package_client_graphics.py', common),
        ('package_client_vulkan.py', [*common, '--java-home', str(args.java_home.resolve()),
                                      '--startup', '--launcher-channel', 'temp_gametest']),
    ]:
        subprocess.run([sys.executable, str(ROOT / 'tools' / script), *options], check=True)
    print('Current client build check complete; PS5 acceptance remains pending. No release published.')


if __name__ == '__main__':
    main()
