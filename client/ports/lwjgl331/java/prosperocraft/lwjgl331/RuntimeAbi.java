/* SPDX-License-Identifier: GPL-3.0-or-later */
package prosperocraft.lwjgl331;

/** Validate the real JNI generation before copying any function table. */
final class RuntimeAbi {
 static void validate(String feature, int version, int slots) {
  boolean valid = "17".equals(feature) ? version == 0x000a0000 && slots == 234
      : "21".equals(feature) ? version == 0x00150000 && slots == 235
      : "25".equals(feature) && (version == 0x00180000 || version == 0x00190000) && slots == 236;
  if (!valid) throw new LinkageError("LWJGL331 JNI generation mismatch");
 }
 private RuntimeAbi() { }
}
