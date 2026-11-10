package com.vanellye.codexgen.gitbridge;

import android.content.ContentResolver;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.provider.DocumentsContract;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;

/**
 * Read-only source import for API 19+ Storage Access Framework providers.
 * Existing repository files are never overwritten. The importer first scans
 * the complete selected tree for conflicts, then copies only into new paths.
 */
public final class Api21WorkspaceTreeImporter {
    private final ContentResolver resolver;

    public Api21WorkspaceTreeImporter(Context context) {
        resolver = context.getContentResolver();
    }

    public int copy(Uri treeUri, File repositoryDirectory) throws Exception {
        if (treeUri == null) throw new IllegalArgumentException("Workspace folder URI is missing.");
        if (repositoryDirectory == null || !new File(repositoryDirectory, ".git").isDirectory())
            throw new IllegalStateException("Prepare the local repository before importing a workspace.");

        // Import only reads the selected tree; write permission is not needed.
        resolver.takePersistableUriPermission(treeUri, Intent.FLAG_GRANT_READ_URI_PERMISSION);

        File root = repositoryDirectory.getCanonicalFile();
        String rootPath = root.getPath() + File.separator;
        String treeId = DocumentsContract.getTreeDocumentId(treeUri);

        List<String> conflicts = new ArrayList<String>();
        scanChildren(treeUri, treeId, root, root, rootPath, conflicts);
        if (!conflicts.isEmpty()) {
            throw new IllegalStateException(
                "Import refused; existing paths would be overwritten: " + join(conflicts)
            );
        }
        return copyChildren(treeUri, treeId, root, root, rootPath);
    }

    private void scanChildren(Uri treeUri, String parentId, File destination,
                              File root, String rootPath, List<String> conflicts) throws Exception {
        Uri children = DocumentsContract.buildChildDocumentsUriUsingTree(treeUri, parentId);
        String[] columns = new String[] {
            DocumentsContract.Document.COLUMN_DOCUMENT_ID,
            DocumentsContract.Document.COLUMN_DISPLAY_NAME,
            DocumentsContract.Document.COLUMN_MIME_TYPE
        };
        Cursor cursor = resolver.query(children, columns, null, null, null);
        if (cursor == null) throw new IllegalStateException("Workspace provider returned no directory listing.");
        try {
            while (cursor.moveToNext()) {
                String id = cursor.getString(0);
                String name = cursor.getString(1);
                String mime = cursor.getString(2);
                if (!safeName(name) || skip(name)) continue;

                File target = new File(destination, name).getCanonicalFile();
                if (!target.getPath().startsWith(rootPath))
                    throw new SecurityException("Workspace path escaped repository.");

                boolean directory = DocumentsContract.Document.MIME_TYPE_DIR.equals(mime);
                if (target.exists()) {
                    if (!directory || !target.isDirectory()) {
                        conflicts.add(relativePath(root, target));
                        continue;
                    }
                }
                if (directory) {
                    scanChildren(treeUri, id, target, root, rootPath, conflicts);
                }
            }
        } finally {
            cursor.close();
        }
    }

    private int copyChildren(Uri treeUri, String parentId, File destination,
                             File root, String rootPath) throws Exception {
        if (!destination.exists() && !destination.mkdirs())
            throw new IllegalStateException("Could not create import directory: " + destination);
        if (!destination.isDirectory())
            throw new IllegalStateException("Import destination is not a directory: " + destination);

        Uri children = DocumentsContract.buildChildDocumentsUriUsingTree(treeUri, parentId);
        String[] columns = new String[] {
            DocumentsContract.Document.COLUMN_DOCUMENT_ID,
            DocumentsContract.Document.COLUMN_DISPLAY_NAME,
            DocumentsContract.Document.COLUMN_MIME_TYPE
        };
        Cursor cursor = resolver.query(children, columns, null, null, null);
        if (cursor == null) throw new IllegalStateException("Workspace provider returned no directory listing.");
        int copied = 0;
        try {
            while (cursor.moveToNext()) {
                String id = cursor.getString(0);
                String name = cursor.getString(1);
                String mime = cursor.getString(2);
                if (!safeName(name) || skip(name)) continue;

                File target = new File(destination, name).getCanonicalFile();
                if (!target.getPath().startsWith(rootPath))
                    throw new SecurityException("Workspace path escaped repository.");

                if (DocumentsContract.Document.MIME_TYPE_DIR.equals(mime)) {
                    copied += copyChildren(treeUri, id, target, root, rootPath);
                } else {
                    Uri document = DocumentsContract.buildDocumentUriUsingTree(treeUri, id);
                    InputStream input = resolver.openInputStream(document);
                    if (input == null) continue;

                    File parent = target.getParentFile();
                    if (parent != null && !parent.isDirectory() && !parent.mkdirs()) {
                        input.close();
                        throw new IllegalStateException("Could not create import parent directory.");
                    }
                    // createNewFile is exclusive: it refuses a path that appeared
                    // after the preflight scan instead of truncating existing data.
                    if (!target.createNewFile()) {
                        input.close();
                        throw new IllegalStateException("Import conflict appeared after preflight: " +
                            relativePath(root, target));
                    }

                    OutputStream output = null;
                    boolean complete = false;
                    try {
                        output = new FileOutputStream(target, false);
                        byte[] buffer = new byte[8192];
                        int count;
                        while ((count = input.read(buffer)) != -1) output.write(buffer, 0, count);
                        output.flush();
                        complete = true;
                    } finally {
                        try {
                            input.close();
                        } finally {
                            if (output != null) output.close();
                            if (!complete) target.delete();
                        }
                    }
                    copied++;
                }
            }
        } finally {
            cursor.close();
        }
        return copied;
    }

    private String relativePath(File root, File target) {
        String rootPath = root.getPath() + File.separator;
        String path = target.getPath();
        return path.startsWith(rootPath) ? path.substring(rootPath.length()) : path;
    }

    private String join(List<String> values) {
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < values.size(); i++) {
            if (i > 0) result.append(", ");
            result.append(values.get(i));
        }
        return result.toString();
    }

    private boolean safeName(String name) {
        return name != null && name.length() > 0 && !".".equals(name) &&
            !"..".equals(name) && name.indexOf('/') < 0 && name.indexOf('\\') < 0;
    }

    private boolean skip(String name) {
        return ".git".equals(name) || ".gradle".equals(name) || "build".equals(name) ||
            ".idea".equals(name) || ".kotlin".equals(name) || "local.properties".equals(name);
    }
}
