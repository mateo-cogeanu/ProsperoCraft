#!/usr/bin/env python3
"""Compatibility entry point for legacy 139 staging assertions (not current acceptance)."""
from package_audit import run_legacy
if __name__ == '__main__':
    run_legacy(139)
