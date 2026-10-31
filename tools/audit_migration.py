"""Stable AST fingerprinting across supported Python versions (no code evaluation)."""
import ast
import hashlib
import json


def statement_key(node):
    def encode(value):
        if isinstance(value, ast.AST):
            return [type(value).__name__, [[name, encode(getattr(value,name))] for name in value._fields]]
        if isinstance(value, list):
            return [encode(item) for item in value]
        if isinstance(value, bytes):
            return {'bytes': value.hex()}
        return value
    return json.dumps(encode(node), ensure_ascii=True, separators=(',', ':'))


def statements_digest(nodes):
    return hashlib.sha256('\n'.join(statement_key(node) for node in nodes).encode()).hexdigest()
