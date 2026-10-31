#!/usr/bin/env python3
"""Actual Java resource loading/User-Agent identity, including host fallback/refusal."""
from pathlib import Path
import json
import subprocess
import tempfile
from app_identity import ROOT, RESOURCE, current_identity, java_resource, write_probe_jar, build_status
from host_toolchain import java_home

jdk=java_home()
with tempfile.TemporaryDirectory(prefix='prospero-identity-') as temporary:
    work=Path(temporary)
    (work/'IdentityCheck.java').write_text('public class IdentityCheck { public static void main(String[] a) { System.out.println(ProsperoBuild.VERSION); System.out.println(ProsperoBuild.USER_AGENT); } }')
    subprocess.run([str(jdk/'bin/javac'),'--release','25','-d',str(work),str(ROOT/'client/launcher/java/ProsperoBuild.java'),str(work/'IdentityCheck.java')],check=True)
    command=[str(jdk/'bin/java'),'-cp',str(work),'IdentityCheck']
    def run():return subprocess.run(command,text=True,capture_output=True)
    result=run();assert result.returncode==0 and result.stdout.splitlines()[0]=='development'
    identity=current_identity();(work/RESOURCE).write_bytes(java_resource(identity));result=run()
    assert result.returncode==0 and result.stdout.splitlines()==[identity['app_version'],'mateo-cogeanu/ProsperoCraft/'+identity['app_version']+' (github.com/mateo-cogeanu/ProsperoCraft)']
    jar=work/'probe.jar';write_probe_jar(jar,work,identity=identity,channel='temp_gametest');before=jar.read_bytes()
    write_probe_jar(jar,work,identity=identity,channel='temp_gametest');assert before==jar.read_bytes()
    import zipfile
    with zipfile.ZipFile(jar)as archive:
        assert archive.read(RESOURCE)==(work/RESOURCE).read_bytes()==java_resource(identity)
        assert archive.read('ProsperoBuild.class')==(work/'ProsperoBuild.class').read_bytes()
    status=build_status(jar);assert status['app_version']==identity['app_version'] and status['console']=='pending' and status['compilation']=='passed'
    for bad in [b'',b'app_version=ALL PASS\ntitle_id=PPSA99874\n',b'app_version=01.000.167\n']:
        (work/RESOURCE).write_bytes(bad);result=run();assert result.returncode!=0 and 'Invalid packaged ProsperoCraft identity' in result.stderr
print('PASS canonical package identity, real Java resource/User-Agent, explicit development fallback, malformed resource refusal')
