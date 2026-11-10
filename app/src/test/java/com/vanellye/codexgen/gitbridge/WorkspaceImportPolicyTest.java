package com.vanellye.codexgen.gitbridge;

import org.junit.Test;
import java.io.File;
import static org.junit.Assert.*;

public class WorkspaceImportPolicyTest {
    @Test public void acceptsOnlySingleSafePathSegments() {
        assertTrue(WorkspaceImportPolicy.isSafeName("module.py"));
        assertFalse(WorkspaceImportPolicy.isSafeName("../outside"));
        assertFalse(WorkspaceImportPolicy.isSafeName("nested/file.py"));
        assertFalse(WorkspaceImportPolicy.isSafeName("nested" + ((char) 92) + "file.py"));
        assertFalse(WorkspaceImportPolicy.isSafeName("."));
        assertFalse(WorkspaceImportPolicy.isSafeName(".."));
        assertFalse(WorkspaceImportPolicy.isSafeName(null));
    }

    @Test public void skipsRepositoryAndBuildMetadata() {
        assertTrue(WorkspaceImportPolicy.isSkippedName(".git"));
        assertTrue(WorkspaceImportPolicy.isSkippedName("build"));
        assertFalse(WorkspaceImportPolicy.isSkippedName("src"));
    }

    @Test public void existingFilesConflictButExistingDirectoriesCanBeMerged() throws Exception {
        File root = new File(System.getProperty("java.io.tmpdir"), "workspace-import-policy-test");
        root.mkdirs();
        File file = new File(root, "README.md");
        File directory = new File(root, "src");
        file.createNewFile();
        directory.mkdir();
        try {
            assertFalse(WorkspaceImportPolicy.isConflict(new File(root, "new.py"), false));
            assertTrue(WorkspaceImportPolicy.isConflict(file, false));
            assertTrue(WorkspaceImportPolicy.isConflict(file, true));
            assertFalse(WorkspaceImportPolicy.isConflict(directory, true));
        } finally {
            file.delete();
            directory.delete();
            root.delete();
        }
    }

    @Test public void rejectsPathsOutsideRoot() throws Exception {
        File root = new File("build/import-root");
        assertTrue(WorkspaceImportPolicy.isWithinRoot(new File(root, "new.py"), root));
        assertFalse(WorkspaceImportPolicy.isWithinRoot(new File(root, "../escape.py"), root));
    }
}
