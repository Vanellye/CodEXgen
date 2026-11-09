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
        if (Build.VERSION.SDK_INT < 16) {
            throw new IllegalStateException("Remote HTTPS Git is disabled below Android API 16. Local repository operations remain available.");
        }
    }
    private Git open() throws Exception {
        if (!new File(repoDir, ".git").isDirectory()) throw new IllegalStateException("No local repository. Initialize or clone one first.");
        return Git.open(repoDir);
    }
    private void validate(Config c) {
        if (c == null || c.baseBranch == null || c.featureBranch == null ||
            c.baseBranch.length() == 0 || c.featureBranch.length() == 0 ||
            c.baseBranch.equals(c.featureBranch)) throw new IllegalArgumentException("Distinct base and feature branches are required.");
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
