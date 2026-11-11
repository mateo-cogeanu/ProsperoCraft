# ProsperoCraft maintainer handoff

Snapshot recorded 2026-11-11. Start with the open Java 17 investigation below. Use the [maintainer instructions](../AGENTS.md) for publication and validation rules, and the [README](../README.md) for the supported version matrix and player controls.

## What we are building

ProsperoCraft runs Minecraft Java Edition on homebrew-enabled PS5 consoles. The launcher handles Microsoft sign-in, downloads and verifies the original game and assets, and keeps worlds, mods, resource packs and settings per instance. The released support table includes Vanilla and Fabric across 1.21 through 1.21.11 and supported 26.x versions. The client integrates a native OpenJDK runtime with resident graphics, audio and input libraries. The released client uses Java 25. Java 17 and 21 have separate native startup milestones. The active goal is to get the original **Minecraft 1.20 Vanilla client running on Java 17**, first through the title screen, then through gameplay, save/reload and a clean quit. Java 21 for 1.21.x is follow-on work. The maintainer put NeoForge after 1.20.x.

| Repository | Owns |
| --- | --- |
| [ProsperoCraft](https://github.com/mateo-cogeanu/ProsperoCraft) | Launcher, game and loader integration, publisher pins, probe harnesses, game validation, app packages and release records. On the original Mac the checkout is `PS5_Homebrew/.tools/github-publish/ps5-minecraft-java`. |
| [PS5 Java runtime](https://github.com/mateo-cogeanu/ps5-java25-homebrew) | OpenJDK ports and patches, native runtime and SDK integration, class image tools, resident library and packaging tools. The original Mac workspace is `Documents/ChatGPT/PS5_Homebrew`. Public active files are under `Development/`. |
| [Frozen history](https://github.com/mateo-cogeanu/ps5-homebrew-history) | Accepted source snapshots with provenance. Keep existing tags, checksums and original release assets. |
| [ProsperoStore catalog](https://github.com/darkxex/ps5-homebrew-catalog) | Existing `apps/PPSA99874.json` listing. Public app binaries are hosted on ProsperoCraft's GitHub Releases. |

Keep Minecraft-specific changes in ProsperoCraft. Reusable runtime changes go through `python3 tools/sync_github.py --message "Describe the runtime change"` from the runtime workspace. Check, commit and push the matching ProsperoCraft integration and validation to its `main`. Source publication is authorized while physical testing is pending. Publish only reviewed source and sanitized findings. Keep raw reports, credentials, account files, SDK and dependency caches, game downloads and generated packages out of source commits. Keep original game JARs intact and implement compatibility in the runtime or harness. See [source organization](source-organization.md).

## Current work and next console test

| Title ID | Version or role | Evidence |
| --- | --- | --- |
| `PPSA99874` | Released ProsperoCraft client, `01.000.279` | The maintainer accepted this exact build and confirmed shaders. The GitHub release is published, and catalog PR 1201 was submitted. The client and separate server packages share this title ID. |
| `PPSA99876` | Standalone Java 17 startup, `01.000.002` | Four basic startup, interpreter, JNI, thread and shutdown checks passed on PS5. |
| `PPSA99877` | Standalone Java 21 startup, `01.000.001` | Four basic startup checks passed on PS5. |
| `PPSA99878` | Java 17 Minecraft 1.20 demo probe, `01.000.036` | Tests checked Parker synchronization ownership on the host. The PS5 run should check whether row 3 gets past worker teardown and reaches the title screen. |

Build 033 failed in `Inflater.inflateBytesBytes` while reading a JAR manifest. Build 034 added inflater scratch storage and reached a native SIGBUS after original Main initialized. Build 035 reproduced the fault and captured a worker stack pointing to Parker teardown inside the JavaThread destructor. Build 036 uses checked leases for Parker synchronization objects. The exact native failure and the title screen remain unverified. [035 console evidence](validation/client-java17-bootstrap-035-build.md) · [036 build and checksums](validation/client-java17-bootstrap-036-build.md)

1. Test 036 through row 3. If it faults, reopen the same PS5 probe and leave it at its menu so another run cannot mix or replace the retained evidence.
2. Find the newest `bootstrap036` section in the bootstrap log. Compare the append-only trace and fault reports with `reports035` if available. The Java stages file describes one invocation and can be overwritten. Record the last successful boundary, the exception or fault, and what the evidence leaves open.
3. In the UI, row 3 is **Launch Minecraft 1.20 demo**. In the log it is `CHECK 2` because numbering starts at zero. A displayed `-1708` means a Java exception escaped the probe's `run()`; use the exception class, frames and native trace to diagnose it. A process crash may end before any check result is written. Check the fault log and resolve native addresses against the **matching build's** symbol ELF and load anchor.
4. Repair a concrete cause in its owning repository. Verify the affected behavior on the host, cross-build and package under a new version, audit the signed archive, and record the exact SHA-256. Request a physical test of the new version. Watch for the title screen while row 3 is running, then quit normally to test return and automatic VM shutdown. Record title screen, gameplay, saving and shaders as separate observations.

### Reproducing the Java 17 probe

- Harness and metadata are in [`client/java17_bootstrap`](../client/java17_bootstrap). The native harness initializes graphics reserves and Java 17, runs JNI and LWJGL 3.3.1 checks, and launches the original 1.20 Main in demo mode without account sign-in. It uses `-Xint` and a 192 MiB maximum heap for this test. The Java 17 runtime and classes are generation-matched. The probe title has its own data.
- From the runtime workspace, use `tools/java_lts.py --major 17 --build` with the matching Java 17 boot JDK, LLVM home and an explicit output directory. Run `python3 tools/test_java_lts.py` for patch replay and input checks. The build needs the pinned OpenJDK checkout and prepared PS5 toolchain. See the [LTS build guide](https://github.com/mateo-cogeanu/ps5-java25-homebrew/blob/main/Development/docs/java-lts-runtimes.md).
- The consumer entry point is [`tools/package_java17_bootstrap.py`](../tools/package_java17_bootstrap.py). It takes the runtime workspace, verified publisher cache and game assets, matching class image, LWJGL 3.3.1 build, libffi and explicit GPU, GLFW, Zink, SDL and OpenAL inputs. On the original Mac, `build/java-lts/mc17-bootstrap/build036.sh` records the exact invocation, `image008/boot-image` is the matching class image, and `final036/package/` contains the build audit and symbol ELF. These directories are local. Check the script's inputs before reusing it and choose a fresh work directory and version.
- The original Mac has the full signed 036 archive at `dist/PPSA99878.zip` and the incremental ZIP at `dist/PPSA99878-036-update-from-035.zip`. Use the latter only over a verified 035 installation and merge its files into the same app folder. Use the full ZIP for an uncertain baseline. Preserve prior packages and symbols before moving the active output path. The full demo probe contains local publisher inputs and stays local. If retained files are missing, use the [artifact recovery guide](local-artifact-recovery.md) and verify the archived hashes before reuse.

## Launcher design and code map

The released app has a controller-first native launcher. It presents a library of instance cards and a create card. Opening an instance reveals Play, settings and content for that instance. The launcher verifies or repairs the shared version cache before starting Minecraft. A per-instance game directory keeps worlds and installed content together. Quick refresh repairs cache metadata where possible, and Full repair can fetch missing or damaged files. The released workflow preserves `/download0/ProsperoCraft` on updates. Shared storage and migration code exists for development and must be checked against the candidate's actual policy before use. [Player workflow](../README.md) · [Storage guide](local-storage.md)

| Area | Start here |
| --- | --- |
| Native screens, layout and game handoff | [`native_menu.hpp`](../client/launcher/native_menu.hpp), [`client/startup`](../client/startup), [shared bootstrap](../client/bootstrap). |
| Focus, animation and rendering | [`navigation.hpp`](../client/launcher/navigation.hpp), [`page_motion.hpp`](../client/launcher/page_motion.hpp), [toolkit](../client/launcher/toolkit/README.md), [motion guide](client-launcher-motion-209.md). |
| Themes, icons, DualSense and desktop input | [`theme-tokens.json`](../client/launcher/theme-tokens.json), [`palette.hpp`](../client/launcher/palette.hpp), [`instance_icons.hpp`](../client/launcher/instance_icons.hpp), [`haptics.hpp`](../client/launcher/haptics.hpp), [`desktop_input.hpp`](../client/launcher/desktop_input.hpp). |
| Java launcher and version policy | [`ProsperoLauncher.java`](../client/launcher/java/ProsperoLauncher.java), [`ProsperoVersions.java`](../client/launcher/java/ProsperoVersions.java), [`ProsperoInstall.java`](../client/launcher/java/ProsperoInstall.java), [`ProsperoLibrary.java`](../client/launcher/java/ProsperoLibrary.java). |
| Accounts, downloads and content | [`ProsperoAuth.java`](../client/launcher/java/ProsperoAuth.java), [`ProsperoDownloads.java`](../client/launcher/java/ProsperoDownloads.java), [`ProsperoDependencies.java`](../client/launcher/java/ProsperoDependencies.java), [`ProsperoWeb.java`](../client/launcher/java/ProsperoWeb.java). |

For UI changes, preserve the horizontal page turns, L1/R1 transitions and L2/R2 page navigation with the detent at the activation point. Up/down moves within the current page. Selectors open over the current screen, scroll continuously and size themselves to their content. The theme selector previews immediately on focus, and the icon selector is a grid. Keep instance opening and closing tied to its card and return from instance settings to the instance. Keep the startup notice independent of page animation and automatic account refresh. Honor the user's selected resolution on Zink. Use the theme’s tuned DualSense light-bar color and keep Delete confirmation focused until it closes. The 120 Hz launcher is a presentation target and needs a real console check when changed. Use clear headings and keep the phone sign-in guidance. [High refresh](client-launcher-120-211.md) · [Instance transitions](client-launcher-refinements-210.md) · [Selectors and themes](client-launcher-selectors-212.md)

For launcher changes, run `python3 tools/run_host_tests.py` from ProsperoCraft, with `--fetch-deps` for the initial verified host dependencies, and `--lane native` for affected scoped native code. Use the console to check focus, edges and safe area, animations, controller/mouse/keyboard handoff, chosen resolution, Play, save and quit as applicable. Match the exact Minecraft version, loader, graphics path and shader pack to the change. [Host testing and prerequisites](host-testing.md)

## Making a ProsperoStore release

The last documented release is `01.000.279`. It is a useful worked example for the exact package, shader confirmation, relink materials, checksums and catalog record. [Release notes](releases/client-chunks-menus-279.md) · [Console acceptance](validation/client279-console-acceptance-2026-11-08.json) · [Publication record](validation/client279-store-publication-2026-11-08.json)

1. Build a new `PPSA99874` app candidate with the active package tooling for the change. For the current launcher line, start with [`tools/package_client_121.py`](../tools/package_client_121.py) and the matching build record. Check the artifact version and title ID inside the ZIP, its source/runtime/dependency provenance, and its hash. The public ZIP is an installable app folder with `eboot.bin` and `sce_sys/`. It provisions verified original game files on the console. Exclude official game JARs and asset objects from public packages.
2. Get the maintainer's physical PS5 confirmation for those exact package bytes and the shader rendering check. Record the validated scope, title ID, version and digest. Get explicit release and Store authorization for the exact build. Tie that authorization to the confirmed package and version. Preserve the accepted archive byte for byte.
3. Prepare release notes, build and console validation records, `SHA256SUMS`, and the matching OpenAL corresponding source and relink kit. Keep the project GPL notices, upstream licenses and credits. Use the kit and source inputs for the exact ELF, following the [279 publication record](validation/client279-store-publication-2026-11-08.json) and the matching build audit, native link response and SDK inputs. The checked-in [212 exporter](../tools/export_client212_relink.py) is a version-specific reference for assembling a relocatable kit. Use the new build’s own audited link inputs, pinned source snapshots and symbol ELF hash. Include the kit’s manifest, relink instructions and replacement-build tooling. Verify normal relinking and a compatible OpenAL replacement relink against the tested native ELF as the repository requires.
4. Create the authorized ProsperoCraft GitHub release with the version tag and matching provenance. Upload the verified `PPSA99874.zip`, source/relink kit, validation records and checksums. Independently download the uploaded assets, compare hashes, and verify the downloaded relink kit. Record the final GitHub release and asset URLs.
5. Read the current upstream catalog submission and artifact rules. In the maintainer's fork, start from current upstream `main`. Update only the existing `apps/PPSA99874.json` version, artifact URL, SHA-256 and changelog. Keep description, credits and icon unless the maintainer requests changes. Point to the direct GitHub release asset. From the catalog checkout run the following checks and inspect the resulting diff. [Upstream catalog instructions](https://github.com/darkxex/ps5-homebrew-catalog#run-the-checks-locally)

   ```sh
   python3 -m catalog check
   python3 -m catalog verify PPSA99874
   python3 -m unittest discover -s tests
   git diff --check
   ```

6. Push the authorized catalog branch and submit the PR. Give the maintainer the release and PR links and record the submission in ProsperoCraft. Stop after submission unless the maintainer asks for follow-up. A Record GitHub publication and catalog submission separately. Claim live Store availability only after a separately requested deployment check.

## Cyberduck operations

The PS5 and Mac must be on the same reachable network, and the console FTP service must be running. Use the existing Cyberduck PS5 bookmark or select **Open Connection → FTP**, enter the console's current LAN address and port **2121** for this setup, and connect with the configured credentials if required. Keep the address in the local bookmark and logs out of public documentation.

### Download retained reports

1. After a crash, reopen the **same** probe on the PS5 and leave it at its menu without rerunning the checks. This makes the probe's `download0` available again.
2. In Cyberduck use **Go → Go to Folder…** and enter `/mnt/sandbox/PPSA99878_000/download0`. Click **Refresh**. Confirm the modification times and sizes changed since the previous run. Use the build marker inside the log to confirm identity after transfer. If only `download0.dat` is visible, check that the correct probe is open and its sandbox is mounted.
3. Select the probe reports and use **File → Download To…** for a fresh local run folder, or **File → Download** after moving prior same-name files out of Downloads. Verify **Download complete** and check the local files. On the original Mac, save raw reports under `build/java-lts/mc17-bootstrap/reports036/`, or a separate timestamped directory for a second retrieval.
4. Collect `mc120-java17-bootstrap.log` for build and check results, `mc120-java17-stages.log` for Java exceptions and frames, `java17-vm-trace.log` for runtime checkpoints, `mc120-java17-fault.log` for native faults and `mc120-java17-game.log` for game output. A zero-byte game log can be useful evidence that the game logger did not start. Normal ProsperoCraft uses the production title and its configured report location. Read the installed build's [report and storage code](../client/launcher/storage_paths.hpp) before using the probe path for another title.
5. If the Transfers window stalls, reopen Cyberduck and bring the main FTP browser forward. Reopen the connection from the bookmark if necessary, navigate to the folder again and refresh. Check both the PS5 FTP service and the title mount if the listing still fails. On the original Mac, direct command-line FTP repeatedly failed while Cyberduck could connect, so use the native FTP browser first. If automation stalls but the browser responds manually, download the files manually into Downloads and check their timestamps before comparing.

### Transfer a new local probe

Close the probe before replacing its app files. For this console's homebrew setup the app folder is `/data/homebrew/PPSA99878`. Extract the archive locally and upload the `PPSA99878` folder into `/data/homebrew`, merging the update files if using a verified incremental ZIP. Check that the resulting layout contains `/data/homebrew/PPSA99878/eboot.bin` and `sce_sys/param.json` directly, and that Transfers shows completion. Leave the separate sandbox and its retained logs intact. Launch and read the version on the probe screen before testing. Use the production title path only when intentionally installing the production package. Installation and successful transfer are separate from a console pass.
