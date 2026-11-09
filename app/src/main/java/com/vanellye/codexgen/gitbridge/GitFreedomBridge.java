package com.vanellye.codexgen.gitbridge;

import android.content.Context;
import android.os.Build;
import java.io.File;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.MergeResult;
import org.eclipse.jgit.lib.Ref;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.transport.RefSpec;
import org.eclipse.jgit.transport.RemoteRefUpdate;
import org.eclipse.jgit.transport.UsernamePasswordCredentialsProvider;

/**
 * Local-first Git bridge for the API 11 profile.
 * Local init/status/commit remain available on API 11. HTTPS remote transport is gated
 * below API 16 because the stock legacy TLS provider cannot be assumed to negotiate
 * GitHub's modern TLS requirements.
 */
public final class GitFreedomBridge {
    public static final class Config {
        public String repositoryUrl = "https://github.com/Vanellye/CodEXgen.git";
        public String baseBranch = "main-11-of-38";
        public String featureBranch = "olpirt/stride-next";
        public String authorName = "CodEXgen Contributor";
        public String authorEmail = "";
    }
    private final File repoDir;
    private final TokenVault vault;
    private String sessionToken;

    public GitFreedomBridge(Context context) {
        Context app = context.getApplicationContext();
        repoDir = new File(app.getFilesDir(), "git-bridge/CodEXgen");
        vault = new TokenVault(app);
    }
    public String localPath() { return repoDir.getAbsolutePath(); }
    public void saveToken(String token, char[] passphrase) throws Exception {
        vault.save(token, passphrase);
        sessionToken = token;
    }
    public void unlockToken(char[] passphrase) throws Exception {
        sessionToken = vault.read(passphrase);
        if (sessionToken == null) throw new IllegalStateException("No encrypted token is saved.");
    }
    public void clearToken() { vault.clear(); sessionToken = null; }

    private UsernamePasswordCredentialsProvider credentials() {
        if (sessionToken == null || sessionToken.length() == 0) throw new IllegalStateException("Unlock the saved token first.");
        return new UsernamePasswordCredentialsProvider("x-access-token", sessionToken);
    }
    private void requireRemoteTls() {
        if (Build.VERSION.SDK_INT < 21) {
            throw new IllegalStateException("Remote HTTPS Git is disabled below Android API 21. Local repository operations remain available.");
        }
    }
    private Git open() throws Exception {
        if (!new File(repoDir, ".git").isDirectory()) throw new IllegalStateException("No local repository. Initialize or clone one first.");
        Git git = Git.open(repoDir);
        // Prevent JGit from materializing repository symlinks during checkout.
        // This is a defense for the legacy JGit line on filesystems with case-folding behavior.
        org.eclipse.jgit.lib.StoredConfig stored = git.getRepository().getConfig();
        stored.setBoolean("core", null, "symlinks", false);
        stored.save();
        return git;
    }
    private void validate(Config c) {
        if (c == null || c.baseBranch == null || c.featureBranch == null ||
            c.baseBranch.length() == 0 || c.featureBranch.length() == 0 ||
            c.baseBranch.equals(c.featureBranch)) throw new IllegalArgumentException("Distinct base and feature branches are required.");
        if (c.repositoryUrl == null || !c.repositoryUrl.startsWith("https://github.com/"))
            throw new IllegalArgumentException("Only HTTPS GitHub repository URLs are supported.");
        if (c.authorName == null || c.authorName.trim().length() == 0 ||
            c.authorEmail == null || c.authorEmail.indexOf('@') < 1) throw new IllegalArgumentException("Commit author and email are required.");
    }
    public String initializeLocal(Config c) throws Exception {
        validate(c);
        if (!new File(repoDir, ".git").isDirectory()) {
            File parent = repoDir.getParentFile();
            if (parent != null) parent.mkdirs();
            Git.init().setDirectory(repoDir).call().close();
        }
        Git git = open();
        try {
            requireClean(git);
            Repository r = git.getRepository();
            Ref local = r.findRef(c.featureBranch);
            if (local == null) {
                git.checkout().setCreateBranch(true).setName(c.featureBranch).call();
            } else {
                git.checkout().setName(c.featureBranch).call();
            }
            return "Local repository ready on " + c.featureBranch + ". No network operation performed.";
        } finally { git.close(); }
    }
    public String cloneOrPrepare(Config c) throws Exception {
        validate(c);
        requireRemoteTls();
        if (!new File(repoDir, ".git").isDirectory()) {
            File parent = repoDir.getParentFile();
            if (parent != null) parent.mkdirs();
            Git.cloneRepository().setURI(c.repositoryUrl).setDirectory(repoDir)
                .setBranch("refs/heads/" + c.baseBranch)
                .setNoCheckout(true)
                .setCredentialsProvider(credentials()).call().close();
        }
        Git git = open();
        try {
            requireClean(git);
            git.fetch().setRemote("origin")
                .setRefSpecs(new RefSpec("+refs/heads/*:refs/remotes/origin/*"))
                .setCredentialsProvider(credentials()).call();
            String remoteFeature = "refs/remotes/origin/" + c.featureBranch;
            if (git.getRepository().findRef(c.featureBranch) != null) {
                git.checkout().setName(c.featureBranch).call();
            } else if (git.getRepository().findRef(remoteFeature) != null) {
                git.checkout().setCreateBranch(true).setName(c.featureBranch).setStartPoint(remoteFeature).call();
            } else {
                String remoteBase = "refs/remotes/origin/" + c.baseBranch;
                git.checkout().setCreateBranch(true).setName(c.featureBranch).setStartPoint(remoteBase).call();
            }
            return "Feature branch ready: " + c.featureBranch + ". Base branch was not changed.";
        } finally { git.close(); }
    }
    public String fetch(Config c) throws Exception {
        validate(c); requireRemoteTls();
        Git git = open();
        try {
            requireFeature(git, c);
            git.fetch().setRemote("origin")
                .setRefSpecs(new RefSpec("+refs/heads/*:refs/remotes/origin/*"))
                .setCredentialsProvider(credentials()).call();
            return "Fetch complete for " + c.featureBranch + ".";
        } finally { git.close(); }
    }
    public String pullFastForward(Config c) throws Exception {
        validate(c); requireRemoteTls();
        Git git = open();
        try {
            requireFeature(git, c); requireClean(git);
            git.fetch().setRemote("origin")
                .setRefSpecs(new RefSpec("+refs/heads/*:refs/remotes/origin/*"))
                .setCredentialsProvider(credentials()).call();
            Ref remote = git.getRepository().findRef("refs/remotes/origin/" + c.featureBranch);
            if (remote == null) throw new IllegalStateException("Remote feature branch does not exist.");
            MergeResult result = git.merge().include(remote.getObjectId())
                .setFastForward(org.eclipse.jgit.api.MergeCommand.FastForwardMode.FF_ONLY).call();
            if (result.getMergeStatus() != MergeResult.MergeStatus.FAST_FORWARD &&
                result.getMergeStatus() != MergeResult.MergeStatus.ALREADY_UP_TO_DATE) {
                throw new IllegalStateException("Pull was not a fast-forward: " + result.getMergeStatus());
            }
            return "Fast-forward pull completed on " + c.featureBranch + ".";
        } finally { git.close(); }
    }
    public List<String> review(Config c) throws Exception {
        validate(c);
        Git git = open();
        try {
            requireFeature(git, c);
            org.eclipse.jgit.api.Status s = git.status().call();
            List<String> paths = new ArrayList<String>();
            paths.addAll(s.getUntracked()); paths.addAll(s.getAdded());
            paths.addAll(s.getChanged()); paths.addAll(s.getModified());
            paths.addAll(s.getMissing()); paths.addAll(s.getRemoved());
            Collections.sort(paths);
            return paths;
        } finally { git.close(); }
    }
    public String commitSelected(Config c, List<String> paths, String message) throws Exception {
        validate(c);
        if (paths == null || paths.size() == 0) throw new IllegalArgumentException("Select changed files first.");
        if (message == null || message.trim().length() == 0) throw new IllegalArgumentException("Commit message is required.");
        Git git = open();
        try {
            requireFeature(git, c);
            List<String> current = review(c);
            for (String path : paths) {
                if (path.startsWith("/") || path.indexOf("..") >= 0 || !current.contains(path))
                    throw new IllegalArgumentException("Unsafe or stale selected path: " + path);
                File f = new File(repoDir, path);
                if (f.exists()) git.add().addFilepattern(path).call();
                else git.rm().addFilepattern(path).call();
            }
            org.eclipse.jgit.api.CommitCommand cmd = git.commit().setMessage(message)
                .setAuthor(c.authorName, c.authorEmail);
            for (String path : paths) cmd.setOnly(path);
            return "Local commit created: " + cmd.call().getName();
        } finally { git.close(); }
    }
    public String writeLocalFile(String relativePath, String contents) throws Exception {
        if (relativePath == null || relativePath.trim().length() == 0)
            throw new IllegalArgumentException("Repository-relative file path is required.");
        String path = relativePath.trim();
        if (path.startsWith("/") || path.indexOf('\\\\') >= 0)
            throw new IllegalArgumentException("Absolute paths and backslashes are not allowed.");
        String[] parts = path.split("/");
        for (int i = 0; i < parts.length; i++) {
            if (parts[i].length() == 0 || ".".equals(parts[i]) || "..".equals(parts[i]) || ".git".equals(parts[i]))
                throw new IllegalArgumentException("Unsafe repository path rejected.");
        }
        if (!new File(repoDir, ".git").isDirectory())
            throw new IllegalStateException("Initialize or clone the local repository first.");
        File root = repoDir.getCanonicalFile();
        File target = new File(root, path).getCanonicalFile();
        String rootPath = root.getPath() + File.separator;
        if (!target.getPath().startsWith(rootPath))
            throw new IllegalArgumentException("File path escapes the repository.");
        File parent = target.getParentFile();
        if (parent != null) parent.mkdirs();
        java.io.FileOutputStream output = new java.io.FileOutputStream(target);
        try {
            output.write((contents == null ? "" : contents).getBytes("UTF-8"));
            output.flush();
        } finally { output.close(); }
        return "Saved " + path + " inside the local repository.";
    }

    public String pushNormal(Config c) throws Exception {
        validate(c); requireRemoteTls();
        Git git = open();
        try {
            requireFeature(git, c);
            Iterable<org.eclipse.jgit.transport.PushResult> results = git.push().setRemote("origin")
                .setRefSpecs(new RefSpec("refs/heads/" + c.featureBranch + ":refs/heads/" + c.featureBranch))
                .setCredentialsProvider(credentials()).call();
            for (org.eclipse.jgit.transport.PushResult result : results) {
                for (RemoteRefUpdate update : result.getRemoteUpdates()) {
                    RemoteRefUpdate.Status status = update.getStatus();
                    if (status != RemoteRefUpdate.Status.OK && status != RemoteRefUpdate.Status.UP_TO_DATE)
                        throw new IllegalStateException("Normal push rejected: " + status + ". No force push attempted.");
                }
            }
            return "Normal push completed for " + c.featureBranch + ".";
        } finally { git.close(); }
    }
    public String createDraftPullRequest(Config c, String title, String body) throws Exception {
        validate(c);
        requireRemoteTls();
        if (title == null || title.trim().length() == 0) throw new IllegalArgumentException("Pull request title is required.");
        Git current = open();
        try { requireFeature(current, c); } finally { current.close(); }
        if (sessionToken == null || sessionToken.length() == 0) throw new IllegalStateException("Unlock the saved token first.");
        String repoPath = c.repositoryUrl.replace("https://github.com/", "").replace(".git", "");
        String[] ownerRepo = repoPath.split("/");
        if (ownerRepo.length != 2) throw new IllegalArgumentException("Repository URL must be https://github.com/owner/repository.git");
        String baseUrl = "https://api.github.com/repos/" + repoPath + "/pulls";
        String query = "?head=" + java.net.URLEncoder.encode(ownerRepo[0] + ":" + c.featureBranch, "UTF-8")
            + "&base=" + java.net.URLEncoder.encode(c.baseBranch, "UTF-8") + "&state=open";
        String existing = requestGithub(baseUrl + query, "GET", null);
        org.json.JSONArray open = new org.json.JSONArray(existing);
        if (open.length() > 0) {
            org.json.JSONObject first = open.optJSONObject(0);
            if (first != null) return "Existing pull request: " + first.optString("html_url", "");
        }
        org.json.JSONObject payload = new org.json.JSONObject();
        payload.put("title", title.trim());
        payload.put("body", body == null ? "" : body);
        payload.put("head", c.featureBranch);
        payload.put("base", c.baseBranch);
        payload.put("draft", true);
        org.json.JSONObject created = new org.json.JSONObject(requestGithub(baseUrl, "POST", payload));
        String url = created.optString("html_url", "");
        if (!url.startsWith("https://github.com/")) throw new IllegalStateException("GitHub did not return a valid pull request URL.");
        return "Draft pull request created: " + url;
    }

    private String requestGithub(String address, String method, org.json.JSONObject payload) throws Exception {
        java.net.HttpURLConnection connection = (java.net.HttpURLConnection)new java.net.URL(address).openConnection();
        try {
            connection.setRequestMethod(method);
            connection.setConnectTimeout(15000);
            connection.setReadTimeout(20000);
            connection.setRequestProperty("Accept", "application/vnd.github+json");
            connection.setRequestProperty("Authorization", "Bearer " + sessionToken);
            connection.setRequestProperty("X-GitHub-Api-Version", "2022-11-28");
            if (payload != null) {
                connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
                byte[] bytes = payload.toString().getBytes("UTF-8");
                java.io.OutputStream output = connection.getOutputStream();
                try { output.write(bytes); output.flush(); } finally { output.close(); }
            }
            int code = connection.getResponseCode();
            java.io.InputStream input = (code >= 200 && code < 300) ? connection.getInputStream() : connection.getErrorStream();
            java.io.ByteArrayOutputStream bytes = new java.io.ByteArrayOutputStream();
            if (input != null) {
                try {
                    byte[] buffer = new byte[4096];
                    int count;
                    while ((count = input.read(buffer)) != -1) bytes.write(buffer, 0, count);
                } finally { input.close(); }
            }
            String response = new String(bytes.toByteArray(), "UTF-8");
            if (code < 200 || code >= 300) throw new IllegalStateException("GitHub API request failed (" + code + "): " + response);
            return response;
        } finally { connection.disconnect(); }
    }

    private void requireFeature(Git git, Config c) throws Exception {
        String branch = git.getRepository().getBranch();
        if (!c.featureBranch.equals(branch))
            throw new IllegalStateException("Safety check: current branch is " + branch + ", expected " + c.featureBranch + ".");
    }
    private void requireClean(Git git) throws Exception {
        if (!git.status().call().isClean())
            throw new IllegalStateException("Working tree has edits. Review or commit them before switching or pulling.");
    }
}
