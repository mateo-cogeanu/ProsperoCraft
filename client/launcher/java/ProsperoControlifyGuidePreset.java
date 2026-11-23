import com.google.gson.*;
import java.io.IOException;
import java.nio.file.*;
import java.util.zip.*;

/** Default screen guides off on the Minecraft versions with flickering labels. */
final class ProsperoControlifyGuidePreset {
 static final String PACK = "prosperocraft-controlify-screen-guide.zip";
 private static final String DEFAULTS = "assets/controlify/controllers/default_config/default.json";
 private static final String GUIDE = "show_screen_guides";

 static boolean applies(String version, String loader) {
  return "fabric".equals(loader) && ("1.21".equals(version) || "1.21.1".equals(version));
 }

 static void prepare(Path game) throws IOException {
  Path pack = game.resolve("resourcepacks").resolve(PACK);
  Path marker = game.resolve("config/.prosperocraft-screen-guide-preset");
  ProsperoDownloads.noLinks(pack);
  ProsperoDownloads.noLinks(marker);
  if (Files.exists(marker)) return;
  // Validate the selection before touching any existing configuration.
  ProsperoControlifyKeyboard.selections(game);
  if (Files.exists(pack)) {
   // Only select a pack created by this preset, including after a partial write.
   try (ZipFile zip = new ZipFile(pack.toFile())) {
    if (zip.getEntry("prosperocraft-guide-preset-v1") == null) return;
   } catch (ZipException invalid) { return; }
  } else {
   Files.createDirectories(pack.getParent());
   Path temporary = Files.createTempFile(pack.getParent(), ".guide-preset-", ".tmp");
   try {
    try (ZipOutputStream zip = new ZipOutputStream(Files.newOutputStream(temporary))) {
     add(zip, "prosperocraft-guide-preset-v1", "");
     add(zip, "pack.mcmeta", "{\"pack\":{\"pack_format\":34,\"description\":\"ProsperoCraft Controlify screen guide preset\"}}");
     add(zip, DEFAULTS, "{\"generic\":{\"guide\":{\"show_screen_guides\":false}}}");
    }
    Files.move(temporary, pack);
   } finally { Files.deleteIfExists(temporary); }
  }
  ProsperoControlifyKeyboard.select(game, "file/" + PACK, true, "options.before-controlify-screen-guide.txt");
  Path config = game.resolve("config/controlify.json");
  ProsperoDownloads.noLinks(config);
  if (Files.isRegularFile(config) && Files.size(config) <= 2 * 1024 * 1024) {
   migrateProfiles(config);
  }
  Files.createDirectories(marker.getParent());
  Files.writeString(marker, "version=1\n", StandardOpenOption.CREATE_NEW);
 }

 private static void migrateProfiles(Path config) throws IOException {
  JsonElement document;
  try { document = JsonParser.parseString(Files.readString(config)); }
  catch (JsonParseException malformed) { return; }
  JsonElement profiles = child(document, "profiles");
  if (profiles == null || !profiles.isJsonArray()) return;
  boolean changed = false;
  for (JsonElement profile : profiles.getAsJsonArray()) {
   JsonElement guide = child(child(profile, "generic"), "guide");
   JsonElement enabled = child(guide, GUIDE);
   if (enabled != null && enabled.isJsonPrimitive() && enabled.getAsJsonPrimitive().isBoolean()
       && enabled.getAsBoolean()) {
    guide.getAsJsonObject().addProperty(GUIDE, false);
    changed = true;
   }
  }
  if (!changed) return;
  Path backup = config.resolveSibling("controlify.before-prosperocraft-screen-guide.json");
  ProsperoDownloads.noLinks(backup);
  if (!Files.exists(backup)) Files.copy(config, backup);
  ProsperoDownloads.noLinks(config.resolveSibling("controlify.json.tmp"));
  ProsperoInstall.save(config, new GsonBuilder().serializeNulls().setPrettyPrinting().create().toJson(document) + "\n");
 }

 private static JsonElement child(JsonElement parent, String key) {
  return parent != null && parent.isJsonObject() ? parent.getAsJsonObject().get(key) : null;
 }

 private static void add(ZipOutputStream zip, String path, String contents) throws IOException {
  zip.putNextEntry(new ZipEntry(path));
  zip.write(contents.getBytes(java.nio.charset.StandardCharsets.UTF_8));
  zip.closeEntry();
 }
}
