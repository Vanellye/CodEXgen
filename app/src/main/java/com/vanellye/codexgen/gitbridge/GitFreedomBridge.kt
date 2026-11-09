package com.vanellye.codexgen.gitbridge

import android.content.Context
import android.net.Uri
import androidx.documentfile.provider.DocumentFile
import org.eclipse.jgit.api.Git
import org.eclipse.jgit.api.MergeCommand
import org.eclipse.jgit.transport.RefSpec
import org.eclipse.jgit.transport.UsernamePasswordCredentialsProvider
import java.io.File

/**
 * Local-first Git workflow. All mutations target the configured feature branch.
 * Pull is fast-forward-only and refuses to run with uncommitted working-tree changes.
 */
class GitFreedomBridge(context: Context) {
    private val appContext = context.applicationContext
    private val vault = TokenVault(appContext)
    private val repoDir = File(appContext.filesDir, "git-bridge/CodEXgen")

    fun saveUserToken(token: String) = vault.save(token)
    fun clearUserToken() = vault.clear()
    fun localRepositoryPath(): String = repoDir.absolutePath

    fun importWorkspaceTree(treeUri: Uri): Int {
        require(repoDir.resolve(".git").isDirectory) {
            "Prepare the feature branch before importing a workspace."
        }
        val root = DocumentFile.fromTreeUri(appContext, treeUri)
            ?: error("Could not open the selected workspace folder.")
        var copied = 0

        fun copyChildren(source: DocumentFile, destination: File) {
            destination.mkdirs()
            source.listFiles().forEach { child ->
                val name = child.name ?: return@forEach
                if (name in setOf(".git", ".gradle", "build", ".idea", ".kotlin") ||
                    name == "local.properties"
                ) return@forEach
                if (child.isDirectory) {
                    copyChildren(child, File(destination, name))
                } else if (child.isFile) {
                    appContext.contentResolver.openInputStream(child.uri)?.use { input ->
                        val output = File(destination, name)
                        output.parentFile?.mkdirs()
                        output.outputStream().use { input.copyTo(it) }
                        copied++
                    }
                }
            }
        }
        copyChildren(root, repoDir)
        return copied
    }

    fun prepare(config: GitBridgeConfig): GitBridgeResult = runCatching {
        validate(config)
        val credentials = credentials()
        val git = if (repoDir.resolve(".git").isDirectory) {
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
            requireClean(repository) 
            repository.fetch()
                .setRemote("origin")
                .setRefSpecs(RefSpec("+refs/heads/*:refs/remotes/origin/*"))
                .setCredentialsProvider(credentials)
                .call()

            val remoteBase = "refs/remotes/origin/${config.baseBranch}"
            if (repository.repository.findRef(config.baseBranch) == null) {
                repository.checkout().setCreateBranch(true)
                    .setName(config.baseBranch).setStartPoint(remoteBase).call()
            } else {
                repository.checkout().setName(config.baseBranch).call()
            }

            val localFeature = repository.repository.findRef(config.featureBranch)
            val remoteFeature = repository.repository.findRef(
                "refs/remotes/origin/${config.featureBranch}"
            )
            when {
                localFeature != null -> repository.checkout().setName(config.featureBranch).call()
                remoteFeature != null -> repository.checkout().setCreateBranch(true)
                    .setName(config.featureBranch).setStartPoint(remoteFeature.name).call()
                else -> repository.checkout().setCreateBranch(true)
                    .setName(config.featureBranch).setStartPoint(config.baseBranch).call()
            }

            GitBridgeResult.Success(
                GitBridgeStatus(
                    "Feature branch ready. No base-branch merge or push was performed.",
                    config.featureBranch,
                    changedFiles(repository).size,
                    false
                )
            )
        }
    }.getOrElse {
        GitBridgeResult.Failure(
            it.message ?: "Git preparation failed.",
            "Check branch names, repository access, and network. Existing local changes are not discarded."
        )
    }

    fun fetchFeatureBranch(config: GitBridgeConfig): GitBridgeResult = runCatching {
        validate(config)
        Git.open(repoDir).use { git ->
            assertFeatureBranch(git, config)
            git.fetch()
                .setRemote("origin")
                .setRefSpecs(RefSpec("+refs/heads/*:refs/remotes/origin/*"))
                .setCredentialsProvider(credentials())
                .call()
            val remote = git.repository.findRef("refs/remotes/origin/${config.featureBranch}")
            GitBridgeResult.Success(
                GitBridgeStatus(
                    if (remote == null) "Fetch complete. Remote feature branch does not exist yet."
                    else "Fetch complete. Remote feature branch is available for review.",
                    config.featureBranch,
                    changedFiles(git).size,
                    false
                )
            )
        }
    }.getOrElse {
        GitBridgeResult.Failure(
            it.message ?: "Fetch failed.",
            "Verify the saved GitHub token and repository permissions. No local files were changed."
        )
    }

    fun pullFeatureBranch(config: GitBridgeConfig): GitBridgeResult = runCatching {
        validate(config)
        Git.open(repoDir).use { git ->
            assertFeatureBranch(git, config)
            requireClean(git)
            git.fetch()
                .setRemote("origin")
                .setRefSpecs(RefSpec("+refs/heads/*:refs/remotes/origin/*"))
                .setCredentialsProvider(credentials())
                .call()
            val remote = git.repository.findRef("refs/remotes/origin/${config.featureBranch}")
                ?: error("Remote feature branch does not exist. Push it first.")
            val result = git.merge()
                .include(remote.objectId)
                .setFastForward(MergeCommand.FastForwardMode.FF_ONLY)
                .call()
            require(!result.conflicts.isNullOrEmpty().not()) {
                "Pull did not complete as a fast-forward. Review divergence manually; no reset was performed."
            }
            GitBridgeResult.Success(
                GitBridgeStatus(
                    "Fast-forward pull completed for ${config.featureBranch}.",
                    config.featureBranch,
                    changedFiles(git).size,
                    false
                )
            )
        }
    }.getOrElse {
        GitBridgeResult.Failure(
            it.message ?: "Pull failed.",
            "Pull requires a clean working tree and a fast-forwardable remote. Commit or back up local edits, then inspect divergent history manually."
        )
    }

    fun pushFeatureBranch(config: GitBridgeConfig): GitBridgeResult = runCatching {
        validate(config)
        Git.open(repoDir).use { git ->
            assertFeatureBranch(git, config)
            val results = git.push()
                .setRemote("origin")
                .setRefSpecs(RefSpec(
                    "refs/heads/${config.featureBranch}:refs/heads/${config.featureBranch}"
                ))
                .setCredentialsProvider(credentials())
                .call()
            val updates = results.flatMap { it.remoteUpdates }
            val rejected = updates.filter {
                it.status != org.eclipse.jgit.transport.RemoteRefUpdate.Status.OK &&
                    it.status != org.eclipse.jgit.transport.RemoteRefUpdate.Status.UP_TO_DATE
            }
            require(rejected.isEmpty()) {
                "Normal push rejected: ${rejected.joinToString { it.status.toString() }}. No force push was attempted."
            }
            GitBridgeResult.Success(
                GitBridgeStatus(
                    "Normal push completed for ${config.featureBranch}.",
                    config.featureBranch,
                    changedFiles(git).size,
                    true
                )
            )
        }
    }.getOrElse {
        GitBridgeResult.Failure(
            it.message ?: "Push failed.",
            "Normal fast-forward push only. Fetch and review remote changes; force-push is not automatic."
        )
    }

    fun reviewChanges(config: GitBridgeConfig): List<GitFileChange> {
        validate(config)
        Git.open(repoDir).use { git ->
            assertFeatureBranch(git, config)
            return changedFiles(git)
        }
    }

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
        Git.open(repoDir).use { git ->
            assertFeatureBranch(git, config)
            val current = changedFiles(git).associateBy { it.path }
            selectedPaths.forEach { path ->
                require(!path.startsWith("/") && ".." !in path.split("/")) {
                    "Unsafe repository path rejected: $path"
                }
                require(path in current) { "Refresh review; path is no longer changed: $path" }
            }
            selectedPaths.forEach { path ->
                if (File(repoDir, path).exists()) git.add().addFilepattern(path).call()
                else git.rm().addFilepattern(path).call()
            }
            val command = git.commit().setMessage(commitMessage)
                .setAuthor(config.authorName, config.authorEmail)
            selectedPaths.forEach(command::setOnly)
            val commit = command.call()
            val result = pushFeatureBranch(config)
            when (result) {
                is GitBridgeResult.Success -> result.copy(
                    status = result.status.copy(message = "Commit ${commit.name.take(8)} created. ${result.status.message}")
                )
                is GitBridgeResult.Failure -> result.copy(
                    message = "Commit ${commit.name.take(8)} is local; push was rejected: ${result.message}"
                )
            }
        }
    }.getOrElse {
        GitBridgeResult.Failure(
            it.message ?: "Selected commit failed.",
            "Local files and any created commit are retained. Refresh review before retrying."
        )
    }

    private fun credentials(): UsernamePasswordCredentialsProvider {
        val token = vault.read() ?: error("Save a fine-grained GitHub token first.")
        return UsernamePasswordCredentialsProvider("x-access-token", token)
    }

    private fun requireClean(git: Git) {
        val status = git.status().call()
        require(status.isClean) {
            "Working tree has local edits. Review or commit them before switching branches or pulling."
        }
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
        require(git.repository.branch == config.featureBranch) {
            "Safety check: current branch is '${git.repository.branch}', expected '${config.featureBranch}'."
        }
    }

    private fun validate(config: GitBridgeConfig) {
        require(config.repositoryUrl.startsWith("https://github.com/")) {
            "Only HTTPS GitHub repository URLs are supported."
        }
        require(config.baseBranch.isNotBlank() && config.featureBranch.isNotBlank())
        require(config.baseBranch != config.featureBranch)
        require(!config.featureBranch.startsWith("-") && !config.featureBranch.contains(".."))
        require(config.authorName.isNotBlank() && config.authorEmail.contains("@")) {
            "Enter a commit author name and valid email."
        }
    }
}
