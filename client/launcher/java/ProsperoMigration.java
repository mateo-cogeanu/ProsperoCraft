/* SPDX-License-Identifier: GPL-3.0-or-later */
import java.io.IOException;
import java.nio.file.*;
import java.nio.channels.FileChannel;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.Map;

/** A small startup catalog, followed by independently verified storage units. */
final class ProsperoMigration {
    private static final String CATALOG = ".prospero-incremental-v1";
    private static final String VERSION = "incremental-v1\n";
    private static final Map<String, Long> VITALS = Map.of(
            "library.json", 1024L * 1024, "library.json.backup", 1024L * 1024,
            "account/key", 32L, "account/session", 70000L, "offline-account.json", 65536L);

    static boolean hasPublishedCatalog(Path primary)throws IOException {
        return ProsperoStorageRoot.marker(primary.resolve(CATALOG), VERSION);
    }

    static ProsperoStorageRoot.Selection open(Path legacy, Path primary) throws IOException {
        try {
            ProsperoStorageRoot.probe(primary);
            if (ProsperoStorageRoot.nonempty(primary)) {
                if (ProsperoStorageRoot.marker(primary.resolve(CATALOG), VERSION)) {
                    ProsperoLibrary.verifyReadable(primary);
                    return new ProsperoStorageRoot.Selection(primary, "", legacy);
                }
                // A library published by the previous full transfer is already live.
                if (!ProsperoStorageRoot.freshShared(primary)) ProsperoLibrary.verifyReadable(primary);
                if (!ProsperoStorageRoot.marker(primary.resolve(ProsperoStorageRoot.READY), "shared-v1\n")
                        && !ProsperoStorageRoot.marker(primary.resolve(ProsperoStorageRoot.READY), "fresh-v1\n")
                        && ProsperoStorageRoot.nonempty(legacy)) throw new IOException("Conflicting libraries");
                return new ProsperoStorageRoot.Selection(primary, "");
            }
            if (!ProsperoStorageRoot.nonempty(legacy)) return new ProsperoStorageRoot.Selection(primary, "");
            ProsperoStorageRoot.noLinks(legacy);
            ProsperoLibrary.verifyReadable(legacy);
            for (String journal : new String[]{"pending-delete","pending-copy","trash/instances"}) {
                if (ProsperoStorageRoot.nonempty(legacy.resolve(journal)))
                    throw new IOException("Finish recovering the original library before migration");
            }
            Path stage = primary.resolveSibling(".ProsperoCraft-catalog");
            ProsperoStorageRoot.noLinks(stage);
            String ownership="ProsperoCraft catalog v1\n"+legacy+"\n"+primary+"\n";
            Path owner=stage.resolve(ProsperoStorageRoot.OWNER);
            if(ProsperoStorageRoot.directory(stage)){
                if(!ProsperoStorageRoot.marker(owner,ownership))throw new IOException("Unrecognized catalog stage");
            }else{
                Files.createDirectory(stage);
                ProsperoStorageRoot.privateMode(stage, true);
                Files.writeString(owner,ownership,StandardOpenOption.CREATE_NEW);
            }
            var digests = new java.util.TreeMap<String, String>();
            for (var entry : VITALS.entrySet()) {
                Path source = legacy.resolve(entry.getKey());
                Path target = stage.resolve(entry.getKey());
                ProsperoStorageRoot.noLinks(source);
                ProsperoStorageRoot.noLinks(target);
                var attributes = ProsperoStorageRoot.attributes(source);
                if (attributes == null) {
                    Files.deleteIfExists(target);
                    continue;
                }
                if (!attributes.isRegularFile() || attributes.size() > entry.getValue())
                    throw new IOException("Invalid catalog file");
                Files.createDirectories(target.getParent());
                ProsperoStorageRoot.privateMode(target.getParent(), true);
                var progress = new ProsperoStorageRoot.MigrationProgress(ProsperoStorageRoot.SILENT);
                ProsperoStorageRoot.copy(source, target, progress);
                String digest = ProsperoStorageRoot.digest(target, progress, false);
                if (Files.size(target) != attributes.size() ||
                        !ProsperoStorageRoot.digest(source, progress, false).equals(digest))
                    throw new IOException("Catalog copy verification failed");
                force(target,false);
                digests.put(entry.getKey(),digest);
            }
            ProsperoLibrary.verifyReadable(stage);
            Path marker = stage.resolve(CATALOG);
            ProsperoStorageRoot.noLinks(marker);
            Files.writeString(marker, VERSION);
            Path manifest=stage.resolve(".prospero-legacy-catalog");
            ProsperoStorageRoot.noLinks(manifest);
            Files.write(manifest,digests.entrySet().stream().map(e->e.getKey()+" "+e.getValue()).toList());
            ProsperoStorageRoot.privateMode(manifest,false);
            if (ProsperoStorageRoot.directory(primary)) Files.delete(primary);
            force(marker,false);
            force(owner,false);
            force(manifest,false);
            if(ProsperoStorageRoot.directory(stage.resolve("account")))force(stage.resolve("account"),true);
            force(stage,true);
            force(primary.getParent(),true);
            Files.move(stage, primary, StandardCopyOption.ATOMIC_MOVE);
            return new ProsperoStorageRoot.Selection(primary, "", legacy);
        } catch (IOException failure) {
            return ProsperoStorageRoot.fallback(legacy,
                    "Shared storage could not be opened. Using the original library.");
        }
    }

    static Path stage(Path source, Path destination, Path staging, ProsperoStorageRoot.Progress check)
            throws IOException {
        ProsperoStorageRoot.noLinks(staging);
        Files.createDirectories(staging);
        ProsperoStorageRoot.privateMode(staging, true);
        Path partial = staging.resolve(destination.getFileName());
        ProsperoStorageRoot.verifiedTree(source, destination, partial, null,
                new ProsperoStorageRoot.MigrationProgress(check), true);
        return partial;
    }

    static void publish(Path partial, Path target) throws IOException {
        ProsperoStorageRoot.noLinks(target);
        if (ProsperoStorageRoot.attributes(target) != null) throw new IOException("Migration destination exists");
        Files.createDirectories(target.getParent());
        Files.move(partial, target, StandardCopyOption.ATOMIC_MOVE);
    }

    private static String identity(Path source,Path target){
        return "ProsperoCraft migration v1\n"+source+"\n"+target+"\n";
    }

    static boolean published(Path source,Path target)throws IOException{
        ProsperoStorageRoot.noLinks(target);
        return ProsperoStorageRoot.directory(target)&&
                ProsperoStorageRoot.marker(target.resolve(ProsperoStorageRoot.OWNER),identity(source,target));
    }

    static Path retire(Path source, Path target) throws IOException {
        ProsperoStorageRoot.noLinks(source);
        if(!published(source,target))throw new IOException("Verified destination is unavailable");
        force(target.getParent(),true);
        force(target.getParent().getParent(),true);
        Path journal=retiredPath(source);
        Files.createDirectory(journal);
        ProsperoStorageRoot.privateMode(journal,true);
        Files.writeString(journal.resolve("owner"),identity(source,target),StandardOpenOption.CREATE_NEW);
        force(journal.resolve("owner"),false);
        force(journal,true);
        Files.move(source,journal.resolve("files"),StandardCopyOption.ATOMIC_MOVE);
        return journal;
    }

    private static Path retiredPath(Path source){
        return source.resolveSibling(".prospero-retired-"+source.getFileName());
    }

    static void recoverRetired(Path source,Path target)throws IOException {
        Path journal=retiredPath(source);
        ProsperoStorageRoot.noLinks(journal);
        if(!ProsperoStorageRoot.directory(journal)||
                !ProsperoStorageRoot.marker(journal.resolve("owner"),identity(source,target)))return;
        if(published(source,target)&&ProsperoStorageRoot.attributes(source)==null)finishRetirement(journal);
    }

    static void finishRetirement(Path journal)throws IOException{
        Path files=journal.resolve("files");
        if(ProsperoStorageRoot.attributes(files)!=null)purge(files);
        Files.delete(journal.resolve("owner"));
        Files.delete(journal);
    }

    static void retireCatalog(Path legacy, Path primary) throws IOException {
        ProsperoStorageRoot.noLinks(legacy);
        if (ProsperoStorageRoot.nonempty(legacy.resolve("instances")) ||
                ProsperoStorageRoot.attributes(legacy.resolve("cache")) != null ||
                ProsperoStorageRoot.attributes(retiredPath(legacy.resolve("cache"))) != null) return;
        Path manifest=primary.resolve(".prospero-legacy-catalog");
        ProsperoStorageRoot.noLinks(manifest);
        var attributes=ProsperoStorageRoot.attributes(manifest);
        if(attributes==null||!attributes.isRegularFile()||attributes.size()>4096)return;
        if(ProsperoStorageRoot.nonempty(legacy.resolve("pending-delete"))||
                ProsperoStorageRoot.nonempty(legacy.resolve("pending-copy")))return;
        ProsperoLibrary.verifyReadable(primary);
        force(primary,true);
        force(primary.getParent(),true);
        var progress=new ProsperoStorageRoot.MigrationProgress(ProsperoStorageRoot.SILENT);
        for(String line:Files.readAllLines(manifest)){
            String[] row=line.split(" ",-1);
            if(row.length!=2||!VITALS.containsKey(row[0])||!row[1].matches("[a-f0-9]{64}"))
                throw new IOException("Invalid legacy catalog cleanup manifest");
            Path path=legacy.resolve(row[0]);
            ProsperoStorageRoot.noLinks(path);
            var file=ProsperoStorageRoot.attributes(path);
            if(file!=null&&file.isRegularFile()&&file.size()<=VITALS.get(row[0])&&
                    ProsperoStorageRoot.digest(path,progress,false).equals(row[1]))Files.delete(path);
        }
        for(String name:new String[]{"instances","account","pending-delete","pending-copy"}){
            Path dir=legacy.resolve(name);
            if(ProsperoStorageRoot.directory(dir)&&!ProsperoStorageRoot.nonempty(dir))Files.delete(dir);
        }
        if(!ProsperoStorageRoot.nonempty(legacy))Files.deleteIfExists(legacy);
    }

    static void force(Path path,boolean directory)throws IOException{
        try(var channel=FileChannel.open(path,directory?StandardOpenOption.READ:StandardOpenOption.WRITE,
                LinkOption.NOFOLLOW_LINKS)){
            channel.force(true);
        }
    }

    static void purge(Path root) throws IOException {
        Files.walkFileTree(root, java.util.EnumSet.noneOf(FileVisitOption.class), 64,
                new SimpleFileVisitor<Path>() {
            @Override public FileVisitResult visitFile(Path file, BasicFileAttributes attributes) throws IOException {
                Files.delete(file);
                return FileVisitResult.CONTINUE;
            }
            @Override public FileVisitResult postVisitDirectory(Path dir, IOException error) throws IOException {
                if (error != null) throw error;
                Files.delete(dir);
                return FileVisitResult.CONTINUE;
            }
        });
    }
}
