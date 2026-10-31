#!/usr/bin/env python3
"""Audit schema/ZIP corruption gates and every legacy statement's migration/order."""
import ast
import hashlib
import io
import json
from pathlib import Path
import tempfile
import zipfile
import warnings
from app_identity import ROOT, RESOURCE, current_identity, java_resource
from audit_migration import statements_digest
from package_audit import audit_current_identity, checked_zip, load_legacy_manifest


def rejected(action):
    try:
        action()
    except (ValueError, KeyError, zipfile.BadZipFile):
        return
    raise AssertionError('Malformed audit input accepted')


manifest = load_legacy_manifest(ROOT/'tests/audits/legacy-builds.json')
migration = json.loads((ROOT/'tests/audits/migration.json').read_text())
function = next(n for n in ast.parse((ROOT/'tools/legacy_package_audit.py').read_text()).body if isinstance(n,ast.FunctionDef))
for number in manifest['builds']:
    selected=[]
    for node in function.body[1:]:
        if isinstance(node,ast.If) and isinstance(node.test,ast.Compare) and isinstance(node.test.left,ast.Name) and node.test.left.id=='number':
            if number in ast.literal_eval(node.test.comparators[0]):selected.extend(node.body)
        else:selected.append(node)
    digest=statements_digest(selected)
    assert digest==migration['profiles'][str(number)]['normalized_ast_sha256'],number
    assert sum(isinstance(n,ast.Assert)for s in selected for n in ast.walk(s)) > 0
with tempfile.TemporaryDirectory() as temporary:
    work=Path(temporary);path=work/'manifest.json'
    for data in [{}, {'schema':1,'kind':'current','builds':[122]}, {'schema':True,'kind':'legacy-staging','builds':[122]}, {'schema':1,'kind':'legacy-staging','builds':[122,122]}, {'schema':1,'kind':'legacy-staging','builds':['__import__("os")']}, {'schema':1,'kind':'legacy-staging','builds':[151]}, {'schema':1,'kind':'legacy-staging','builds':[]}, {**manifest,'execute':'bad'}]:
        path.write_text(json.dumps(data));rejected(lambda:load_legacy_manifest(path))
    path.write_text('{"schema":1,"schema":1,"kind":"legacy-staging","builds":[122]}');rejected(lambda:load_legacy_manifest(path))
    identity=current_identity();prefix=identity['title_id']+'/'
    jar=io.BytesIO()
    with zipfile.ZipFile(jar,'w')as z:z.writestr(RESOURCE,java_resource(identity))
    rows={prefix+'sce_sys/param.json':json.dumps({'titleId':identity['title_id'],'contentVersion':identity['app_version']}),prefix+'assets/java25/classes/'+RESOURCE:java_resource(identity),prefix+'eboot.bin':('Minecraft Original Client Startup '+identity['app_version']).encode(),prefix+'assets/java25/client-probe.jar':jar.getvalue()}
    package=work/'app.zip'
    def write(data):
        with zipfile.ZipFile(package,'w')as z:
            for key,value in data.items():z.writestr(key,value)
    write(rows);assert audit_current_identity(package)==identity
    for key,value in [(prefix+'sce_sys/param.json','{}'),(prefix+'eboot.bin',b'wrong native version'),(prefix+'assets/java25/client-probe.jar',b'invalid jar')]:
        bad=dict(rows);bad[key]=value;write(bad);rejected(lambda:audit_current_identity(package))
    wrong=io.BytesIO()
    with zipfile.ZipFile(wrong,'w')as z:z.writestr(RESOURCE,b'app_version=01.000.000\ntitle_id=PPSA99874\n')
    bad=dict(rows);bad[prefix+'assets/java25/client-probe.jar']=wrong.getvalue();write(bad);rejected(lambda:audit_current_identity(package))
    for member in ['../bad','/absolute','a\\b']:
        write({member:b'x'});rejected(lambda:checked_zip(package).__enter__())
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',UserWarning)
        with zipfile.ZipFile(package,'w')as archive:
            archive.writestr('same',b'a');archive.writestr('same',b'b')
    rejected(lambda:checked_zip(package).__enter__())
    write(rows);rejected(lambda:checked_zip(package,'0'*64).__enter__())
    # Corrupt stored member bytes while retaining its original CRC.
    write({'payload':b'unique payload bytes'});data=package.read_bytes().replace(b'unique payload bytes',b'broken payload bytes');package.write_bytes(data)
    rejected(lambda:checked_zip(package).__enter__())
print('PASS 29 complete legacy statement/order fingerprints; strict manifests, corruption, native/Java identity mismatch gates')
