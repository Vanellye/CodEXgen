package com.vanellye.codexgen.gitbridge;

import java.io.File;
import java.io.IOException;

/** Pure-Java policy helpers for safe workspace import decisions. */
final class WorkspaceImportPolicy {
    private WorkspaceImportPolicy() {}

    static boolean isSafeName(String name) {
        return name != null && name.length() > 0 && !".".equals(name) &&
            !"..".equals(name) && name.indexOf('/') < 0 && name.indexOf((char) 92) < 0;
    }

    static boolean isSkippedName(String name) {
        return ".git".equals(name) || ".gradle".equals(name) || "build".equals(name) ||
            ".idea".equals(name) || ".kotlin".equals(name) || "local.properties".equals(name);
    }

    static boolean isWithinRoot(File candidate, File root) throws IOException {
        String rootPath = root.getCanonicalPath() + File.separator;
        String candidatePath = candidate.getCanonicalPath();
        return candidatePath.startsWith(rootPath);
    }

    static boolean isConflict(File target, boolean sourceIsDirectory) {
        return target.exists() && (!sourceIsDirectory || !target.isDirectory());
    }
}
