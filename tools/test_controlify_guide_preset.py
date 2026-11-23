#!/usr/bin/env python3
"""Exercise first launch and migration of Controlify profile settings."""
import subprocess
import tempfile
from pathlib import Path
from host_toolchain import ROOT, java_home, launcher_classpath

source = r'''
import java.nio.file.*;
import java.util.zip.ZipFile;

class GuidePresetCheck {
 static void check(boolean ok) { if (!ok) throw new AssertionError(); }

 public static void main(String[] args) throws Exception {
  Path game = Path.of(args[0]);
  check(ProsperoControlifyGuidePreset.applies("1.21", "fabric"));
  check(ProsperoControlifyGuidePreset.applies("1.21.1", "fabric"));
  check(!ProsperoControlifyGuidePreset.applies("1.21.2", "fabric"));
  check(!ProsperoControlifyGuidePreset.applies("1.21", "vanilla"));

  Files.createDirectories(game.resolve("config"));
  Path config = game.resolve("config/controlify.json");
  String original = """
  {"profiles":[{"generic":{"guide":{"show_screen_guides":true,"show_ingame_guide":true}}}],"devices":{"pad":"keep","nullable":null}}
  """;
  Files.writeString(config, original);
  Files.writeString(game.resolve("options.txt"), "renderDistance:9\nresourcePacks:[\"file/custom.zip\"]\n");
  ProsperoControlifyGuidePreset.prepare(game);
  String migrated = Files.readString(config);
  check(migrated.contains("\"show_screen_guides\": false"));
  check(migrated.contains("\"show_ingame_guide\": true") && migrated.contains("\"pad\": \"keep\""));
  check(migrated.contains("\"nullable\": null"));
  check(Files.readString(game.resolve("config/controlify.before-prosperocraft-screen-guide.json")).equals(original));
  check(ProsperoControlifyKeyboard.selections(game).get(0).getAsString().equals("file/custom.zip"));
  Files.writeString(config, original);
  ProsperoControlifyGuidePreset.prepare(game);
  check(Files.readString(config).equals(original));
  check(ProsperoControlifyKeyboard.selections(game).size() == 2);

  Path fresh = game.resolve("fresh");
  ProsperoControlifyGuidePreset.prepare(fresh);
  check(!Files.exists(fresh.resolve("config/controlify.json")));
  check(ProsperoControlifyKeyboard.selections(fresh).size() == 1);
  try (ZipFile zip = new ZipFile(fresh.resolve("resourcepacks").resolve(ProsperoControlifyGuidePreset.PACK).toFile())) {
   var entry = zip.getEntry("assets/controlify/controllers/default_config/default.json");
   check(new String(zip.getInputStream(entry).readAllBytes()).equals("{\"generic\":{\"guide\":{\"show_screen_guides\":false}}}"));
  }
  System.out.println("PASS affected versions, profile migration and backup, fresh preset and player override");
 }
}
'''
with tempfile.TemporaryDirectory() as temporary:
    work = Path(temporary).resolve()
    fixture = work / 'GuidePresetCheck.java'
    fixture.write_text(source)
    jdk, cp = java_home(), launcher_classpath()
    launcher = sorted((ROOT / 'client/launcher/java').glob('*.java'))
    subprocess.run([str(jdk/'bin/javac'), '-cp', cp, '-d', str(work), *map(str, launcher), str(fixture)], check=True)
    subprocess.run([str(jdk/'bin/java'), '-cp', str(work)+':'+cp, 'GuidePresetCheck', str(work/'game')], check=True)
