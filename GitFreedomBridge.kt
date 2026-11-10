package com.vanellye.eria.gitbridge

import android.content.Context
import android.net.Uri
import androidx.documentfile.provider.DocumentFile
import org.eclipse.jgit.api.Git
import org.eclipse.jgit.transport.RefSpec
import org.eclipse.jgit.transport.UsernamePasswordCredentialsProvider
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import org.json.JSONObject

data class GitFileChange(
    val path: String,
    val kind: String,
    val deleted: Boolean
)

/**
 * Local-first Git workflow with explicit feature-branch targeting.
 * The API never force-pushes, merges, or pushes the base branch.
 */
class GitFreedomBridge(context: Context) {
    private val appContext = context.applicationContext
    private val vault = TokenVault(appContext)
    private val repoDir = File(appContext.filesDir, "git-bridge/ERIA")

    fun saveUserToken(token: String) = vault.save(token)
    fun clearUserToken() = vault.clear()
    fun isTokenConfigured(): Boolean = vault.read() != null
    fun localRepositoryPath(): String = repoDir.absolutePath


    /**
     * Imports a user-selected workspace folder into the app-private clone.
     * The .git directory and generated build/cache folders are never copied.
     * Existing files are replaced only inside this app-private clone.
     */
    fun importWorkspaceTree(treeUri: Uri): Int {
        require(repoDir.resolve(".git").isDirectory) {
            "Prepare the feature branch before importing a workspace."
        }
        val root = DocumentFile.fromTreeUri(appContext, treeUri)
            ?: error("Could not open the selected workspace folder.")
        var copied = 0

        fun copyChildren(source: DocumentFile, destination: File, relative: String) {
            destination.mkdirs()
            source.listFiles().forEach { child ->
                val name = child.name ?: return@forEach
                if (name == ".git" || name == ".gradle" || name == "build" ||
                    name == ".idea" || name == ".kotlin" || name == "local.properties"
                ) return@forEach
                val rel = if (relative.isEmpty()) name else "$relative/$name"
                if (child.isDirectory) {
                    copyChildren(child, File(destination, name), rel)
                } else if (child.isFile) {
                    val output = File(destination, name)
                    appContext.contentResolver.openInputStream(child.uri)?.use { input ->
                        output.parentFile?.mkdirs()
                        output.outputStream().use { out -> input.copyTo(out) }
                        copied++
                    }
                }
            }
        }

        copyChildren(root, repoDir, "")
        return copied
    }


    fun prepare(config: GitBridgeConfig): GitBridgeResult = runCatching {
        validate(config)
        val token = vault.read()
            ?: return GitBridgeResult.Failure(
                "No GitHub token is configured.",
                "Create a fine-grained token restricted to Vanellye/CodEXgen with Contents: Read and write and Metadata: Read."
            )
        val credentials = UsernamePasswordCredentialsProvider("x-access-token", token)

        val git = if (File(repoDir, ".git").isDirectory) {
            Git.open(repoDir)
        } else {
            repoDir.parentFile?.mkdirs()
            Git.cloneRepository()
                .setURI(config.repositoryUrl)
                .setDirectory(repoDir)
                .setBranch("refs/heads/${config.baseBranch}")
                .setBranchesToClone(listOf("refs/heads/${config.baseBranch}"))
                .setCredentialsProvider(credentials)
                .call()
        }

        git.use { repository ->
            repository.fetch().setRemote("origin")
                .setCredentialsProvider(credentials).call()

            val remoteBase = "refs/remotes/origin/${config.baseBranch}"
            val localBase = repository.repository.findRef(config.baseBranch)
            if (localBase == null) {
                repository.checkout().setCreateBranch(true)
                    .setName(config.baseBranch).setStartPoint(remoteBase).call()
            } else {
                repository.checkout().setName(config.baseBranch).call()
                repository.pull().setRemote("origin")
                    .setRemoteBranchName(config.baseBranch)
                    .setCredentialsProvider(credentials).call()
            }

            val featureRef = repository.repository.findRef(config.featureBranch)
            if (featureRef == null) {
                repository.checkout().setCreateBranch(true)
                    .setName(config.featureBranch)
                    .setStartPoint(config.baseBranch).call()
            } else {
                repository.checkout().setName(config.featureBranch).call()
            }

            GitBridgeResult.Success(
                GitBridgeStatus(
                    "Local feature branch is ready. Base branch was not modified.",
                    config.featureBranch,
                    changedFiles(repository).size,
                    false
                )
            )
        }
    }.getOrElse {
        GitBridgeResult.Failure(
            it.message ?: "Git operation failed.",
            "Check repository URL, branch names, token permissions, and network. No force-push or merge is performed."
        )
    }

    /** Returns unstaged, staged, and untracked paths for user review. */
    fun reviewChanges(config: GitBridgeConfig): List<GitFileChange> {
        validate(config)
        Git.open(repoDir).use { git ->
            assertFeatureBranch(git, config)
            return changedFiles(git)
        }
    }

    /**
     * Stages and commits only the selected paths.
     * JGit CommitCommand.setOnly(path) limits the commit tree to the selected
     * paths rather than sweeping all other staged files into the commit.
     */
    fun commitSelectedAndPush(
        config: GitBridgeConfig,
        selectedPaths: List<String>,
        commitMessage: String
    ): GitBridgeResult = runCatching {
        validate(config)
        require(commitMessage.isNotBlank()) { "Commit message is required." }
        require(selectedPaths.isNotEmpty()) { "Select at least one changed file." }
        require(selectedPaths.distinct().size == selectedPaths.size) {
            "Duplicate paths are not allowed."
        }

        val token = vault.read()
            ?: return GitBridgeResult.Failure(
                "No GitHub token is configured.",
                "Add a user-authorized token in the Git Bridge screen."
            )
        val credentials = UsernamePasswordCredentialsProvider("x-access-token", token)

        Git.open(repoDir).use { git ->
            assertFeatureBranch(git, config)

            val currentChanges = changedFiles(git).associateBy { it.path }
            selectedPaths.forEach { path ->
                require(!path.startsWith("/") && !path.split("/").contains("..")) {
                    "Unsafe repository path rejected: $path"
                }
                require(currentChanges.containsKey(path)) {
                    "Selected path is no longer changed: $path. Refresh the review list."
                }
            }

            selectedPaths.forEach { path ->
                val file = File(repoDir, path)
                if (file.exists()) {
                    git.add().addFilepattern(path).call()
                } else {
                    git.rm().addFilepattern(path).call()
                }
            }

            val commitCommand = git.commit().setMessage(commitMessage)
                .setAuthor(config.authorName, config.authorEmail)
            selectedPaths.forEach(commitCommand::setOnly)
            val commit = commitCommand.call()

            val refspec = RefSpec(
                "refs/heads/${config.featureBranch}:refs/heads/${config.featureBranch}"
            )
            val pushResults = git.push()
                .setRemote("origin")
                .setRefSpecs(refspec)
                .setCredentialsProvider(credentials)
                .call()

            val rejected = pushResults.any { result ->
                result.remoteUpdates.any { update ->
                    update.status != org.eclipse.jgit.transport.RemoteRefUpdate.Status.OK &&
                    update.status != org.eclipse.jgit.transport.RemoteRefUpdate.Status.UP_TO_DATE
                }
            }
            if (rejected) {
                GitBridgeResult.Failure(
                    "Commit ${commit.name.take(8)} created locally, but GitHub rejected the push.",
                    "Your local commit is retained. Check Contents: Read and write, branch protection, and remote conflicts. Do not force-push."
                )
            } else {
                GitBridgeResult.Success(
                    GitBridgeStatus(
                        "Selected files committed and feature branch pushed.",
                        config.featureBranch,
                        changedFiles(git).size,
                        true
                    )
                )
            }
        }
    }.getOrElse {
        GitBridgeResult.Failure(
            it.message ?: "Selected commit/push failed.",
            "Local files are retained. Refresh review, verify branch and token permissions, then retry without force-pushing."
        )
    }


    /**
     * True compare-and-swap force push for the configured feature branch.
     * The fetched remote tip is supplied as RemoteRefUpdate.expectedOldObjectId.
     * The receive-pack server accepts the update only if the remote ref still
     * has exactly that object ID at update time (atomic lease check).
     */
    fun forceWithLeaseFeatureBranch(config: GitBridgeConfig): GitBridgeResult = runCatching {
        validate(config)
        val token = vault.read() ?: error("No GitHub token is configured.")
        Git.open(repoDir).use { git ->
            assertFeatureBranch(git, config)
            val credentials =
                UsernamePasswordCredentialsProvider("x-access-token", token)

            git.fetch().setRemote("origin")
                .setCredentialsProvider(credentials)
                .call()

            val remoteRefName = "refs/remotes/origin/${config.featureBranch}"
            val remoteRef = git.repository.findRef(remoteRefName)
            val expectedOld = remoteRef?.objectId
            require(expectedOld != null) {
                "Remote feature branch does not exist. Use normal push for its first publication."
            }

            val localRefName = "refs/heads/${config.featureBranch}"
            val localRef = git.repository.findRef(localRefName)
                ?: error("Local feature branch not found.")
            require(localRef.objectId != expectedOld) {
                "Local and remote feature branch tips already match."
            }

            // This constructor sends expectedOldObjectId to the remote update
            // protocol; unlike a preflight-only check, it closes the race window.
            val update = org.eclipse.jgit.transport.RemoteRefUpdate(
                git.repository,
                localRefName,
                "refs/heads/${config.featureBranch}",
                true,
                null,
                expectedOld
            )

            val transport = org.eclipse.jgit.transport.Transport.open(
                git.repository, "origin"
            )
            val results = try {
                transport.credentialsProvider = credentials
                transport.push(null, listOf(update))
            } finally {
                transport.close()
            }

            val remoteUpdate = results.flatMap { it.remoteUpdates }
                .firstOrNull { it.remoteName == "refs/heads/${config.featureBranch}" }
                ?: error("Git transport returned no status for the target feature branch.")

            if (remoteUpdate.status !=
                org.eclipse.jgit.transport.RemoteRefUpdate.Status.OK &&
                remoteUpdate.status !=
                org.eclipse.jgit.transport.RemoteRefUpdate.Status.UP_TO_DATE
            ) {
                error(
                    "Lease-protected push rejected: ${remoteUpdate.status} " +
                    (remoteUpdate.message ?: "")
                )
            }

            GitBridgeResult.Success(
                GitBridgeStatus(
                    "Atomic force-with-lease update succeeded for ${config.featureBranch}.",
                    config.featureBranch,
                    changedFiles(git).size,
                    true
                )
            )
        }
    }.getOrElse {
        GitBridgeResult.Failure(
            it.message ?: "Lease-protected feature-branch push failed.",
            "If the lease was rejected, someone updated the remote branch after your fetch. Fetch, review the new commits, and retry. The base branch was not targeted."
        )
    }

    /** Opens a pull request; it never merges the PR or changes the base branch. */
    fun createPullRequest(
        config: GitBridgeConfig,
        title: String,
        body: String
    ): GitBridgeResult = runCatching {
        validate(config)
        require(title.isNotBlank()) { "Pull request title is required." }
        val token = vault.read() ?: error("No GitHub token is configured.")
        val match = Regex("""github\.com/([^/]+)/([^/.]+)""")
            .find(config.repositoryUrl) ?: error("Could not parse GitHub repository URL.")
        val owner = match.groupValues[1]
        val repo = match.groupValues[2]
        val payload = JSONObject()
            .put("title", title)
            .put("head", config.featureBranch)
            .put("base", config.baseBranch)
            .put("body", body)
        val connection = (URL("https://api.github.com/repos/$owner/$repo/pulls")
            .openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = 15000
            readTimeout = 20000
            doOutput = true
            setRequestProperty("Accept", "application/vnd.github+json")
            setRequestProperty("Authorization", "Bearer $token")
            setRequestProperty("X-GitHub-Api-Version", "2022-11-28")
            setRequestProperty("Content-Type", "application/json; charset=utf-8")
        }
        val bytes = payload.toString().toByteArray(Charsets.UTF_8)
        connection.outputStream.use { it.write(bytes) }
        val code = connection.responseCode
        val stream = if (code in 200..299) connection.inputStream else connection.errorStream
        val response = stream?.bufferedReader()?.use { it.readText() }.orEmpty()
        connection.disconnect()
        if (code !in 200..299) {
            val detail = runCatching { JSONObject(response).optString("message") }.getOrDefault("HTTP $code")
            error("GitHub PR request failed ($code): $detail. Ensure Pull requests: Read and write permission.")
        }
        val json = JSONObject(response)
        GitBridgeResult.Success(
            GitBridgeStatus(
                "Pull request opened: ${json.optString("html_url")}. It has not been merged.",
                config.featureBranch, 0, true
            )
        )
    }.getOrElse {
        GitBridgeResult.Failure(
            it.message ?: "Could not open pull request.",
            "Push the feature branch first and grant the token Pull requests: Read and write."
        )
    }

    private fun changedFiles(git: Git): List<GitFileChange> {
        val status = git.status().call()
        val map = linkedMapOf<String, GitFileChange>()
        status.untracked.forEach { map[it] = GitFileChange(it, "Untracked", false) }
        status.added.forEach { map[it] = GitFileChange(it, "Staged add", false) }
        status.changed.forEach { map[it] = GitFileChange(it, "Modified", false) }
        status.modified.forEach { map[it] = GitFileChange(it, "Staged/modified", false) }
        status.missing.forEach { map[it] = GitFileChange(it, "Missing", true) }
        status.removed.forEach { map[it] = GitFileChange(it, "Staged delete", true) }
        status.conflicting.forEach { map[it] = GitFileChange(it, "Conflict", false) }
        return map.values.sortedBy { it.path }
    }

    private fun assertFeatureBranch(git: Git, config: GitBridgeConfig) {
        val current = git.repository.branch
        require(current == config.featureBranch) {
            "Safety check stopped operation: current branch is '$current', expected '${config.featureBranch}'."
        }
    }

    private fun validate(config: GitBridgeConfig) {
        require(config.repositoryUrl.startsWith("https://github.com/")) {
            "Only HTTPS GitHub URLs are accepted."
        }
        require(config.baseBranch.isNotBlank() && config.featureBranch.isNotBlank())
        require(config.baseBranch != config.featureBranch) {
            "Feature branch must differ from the base branch."
        }
        require(!config.featureBranch.startsWith("-") &&
            !config.featureBranch.contains("..")) {
            "Invalid feature branch name."
        }
        require(config.authorName.isNotBlank() && config.authorEmail.contains("@")) {
            "Set a valid commit author name and email."
        }
    }
}
