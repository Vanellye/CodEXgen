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

/** Loaded reflectively only on API 19+, so API 11 does not resolve DocumentsContract. */
public final class Api21WorkspaceTreeImporter {
    private final ContentResolver resolver;
    public Api21WorkspaceTreeImporter(Context context) {
        resolver = context.getContentResolver();
    }
    public int copy(Uri treeUri, File repositoryDirectory) throws Exception {
        if (treeUri == null) throw new IllegalArgumentException("Workspace folder URI is missing.");
        if (repositoryDirectory == null || !new File(repositoryDirectory, ".git").isDirectory())
            throw new IllegalStateException("Prepare the local repository before importing a workspace.");
        resolver.takePersistableUriPermission(treeUri,
            Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
        File root = repositoryDirectory.getCanonicalFile();
        String rootPath = root.getPath() + File.separator;
        String treeId = DocumentsContract.getTreeDocumentId(treeUri);
        return copyChildren(treeUri, treeId, root, root, rootPath);
    }
    private int copyChildren(Uri treeUri, String parentId, File destination,
                             File root, String rootPath) throws Exception {
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
                    target.mkdirs();
                    copied += copyChildren(treeUri, id, target, root, rootPath);
                } else {
                    Uri document = DocumentsContract.buildDocumentUriUsingTree(treeUri, id);
                    InputStream input = resolver.openInputStream(document);
                    if (input == null) continue;
                    File parent = target.getParentFile();
                    if (parent != null) parent.mkdirs();
                    OutputStream output = new FileOutputStream(target);
                    try {
                        byte[] buffer = new byte[8192];
                        int count;
                        while ((count = input.read(buffer)) != -1) output.write(buffer, 0, count);
                        output.flush();
                    } finally {
                        try { input.close(); } finally { output.close(); }
                    }
                    copied++;
                }
            }
        } finally { cursor.close(); }
        return copied;
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
