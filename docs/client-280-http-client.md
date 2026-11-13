# Java HTTP client for Fabric mods

In ProsperoCraft 01.000.279 on Minecraft 26.3 Fabric, OpSec 1.1.7.4
failed in the Fabric client entrypoint. `SessionAccount.<clinit>` calls
`HttpClient.newBuilder()` and the Java 25 image lacked `java.net.http`. The
reported cause was `NoClassDefFoundError: java/net/http/HttpClient`.

Local test build PPSA99874/01.000.280 adds the OpenJDK module to the Java 25
image. The module uses the existing `java.base` networking and TLS services.
The original mod is installed separately in the instance. The candidate keeps
the publisher JARs and the existing console trust configuration.

## Build and audit

Use the pinned Java 25 target build and its
`tools/java25_boot_image.py` image builder. Take the module list from the
accepted client's packaged `assets/java25/management-image-audit.json`
(`requested_target_modules`), append `java.net.http`, and pass the resulting
comma-separated list to `java25_boot_image.py --modules`. Pass its
`boot-image/lib/modules` to the usual
[client packager](../tools/package_client_121.py) as `--http-module-image`
with `--app-version 01.000.280`. The
[package auditor](../tools/audit_client_121.py) checks the same version and
reads the image back from the signed package.

The module adds 363 image entries. Comparing decompressed images against
build 279 found only the added module and the regenerated
`java.base/jdk/internal/module/SystemModules$all.class`. Tests on a host JDK
built an HTTP client with the same target-built module classes and received
the expected response over loopback. The original OpSec class also initialized
with those module classes on the host and reproduced the console’s
`NoClassDefFoundError` when the HTTP module was omitted. The patched JIMAGE
reader also passed its host
resource-identity and allocation-failure tests with the expanded image.

The Java 25 build derives from current ProsperoCraft source, which includes
later shared shaderc fault-reporting source used by the Java 17 probe. Its
Java 17-only options are disabled for this client. The package comparison
against 279 found build identity changes, the image and its metadata, and
the recompiled native executable and associated diagnostic audit/source.
See the [exact candidate record](validation/client280-http-client-2026-11-13.json).

## PS5 validation pending

Install 01.000.280 over the existing PPSA99874 app and start the same 26.3
Fabric instance with OpSec 1.1.7.4 and its installed dependencies. Verify that
it reaches the title screen, then test the OpSec feature that uses HTTP.
World entry, save/reload, shutdown and shader rendering remain pending on
this exact package.
