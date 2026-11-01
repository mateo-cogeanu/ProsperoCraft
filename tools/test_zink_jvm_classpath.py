#!/usr/bin/env python3
"""Exercise actual packaged classpath with old184 negative and corrected ordering."""
import argparse,tempfile
from pathlib import Path
from host_toolchain import ROOT,java_home
from zink_jvm_classpath import parse_header,fix_header,verify_app_classpath,GLFW,PREFIX

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--app',type=Path,required=True);p.add_argument('--header',type=Path,required=True);p.add_argument('--java-home',type=Path);a=p.parse_args();jdk=java_home(a.java_home)
 old=a.header.read_text();paths=parse_header(old);assert PREFIX+GLFW not in paths,'Negative control must use original184header'
 with tempfile.TemporaryDirectory(prefix='zink-classpath-')as directory:
  work=Path(directory)
  try:verify_app_classpath(a.app,old,jdk,work/'old')
  except ValueError as error:assert 'org.lwjgl.glfw.GLFW'in str(error)
  else:raise AssertionError('Missing GLFW from effective184classpath was accepted')
  fixed=fix_header(old);assert parse_header(fixed)[0]==PREFIX+GLFW
  assert fix_header(fixed)==fixed
  record=verify_app_classpath(a.app,fixed,jdk,work/'fixed');assert record['required_classes']['org.lwjgl.glfw.GLFW']==GLFW
 print('PASS actual package JAR/effective classpath; original184missingGLFW rejected; corrected adaptedGLFW precedence + real JDK25 resolution; idempotent header; no GL/PS5 execution')
if __name__=='__main__':main()
