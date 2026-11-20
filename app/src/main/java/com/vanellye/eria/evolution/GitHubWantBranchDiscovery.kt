package com.vanellye.eria.evolution

import org.json.JSONArray
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.net.HttpURLConnection
import java.net.URL

/** Read-only GitHub API contract. Only branch and tree reads are exposed. */
interface GitHubReadOnlyApi {
    fun listBranches(repository: String, page: Int, perPage: Int): List<GitHubBranchRef>
    fun treeForCommit(repository: String, commitSha: String): GitHubTreeSnapshot
}

data class GitHubBranchRef(val name: String, val headSha: String)
data class GitHubTreeEntry(val path: String, val blobSha: String, val type: String)
data class GitHubTreeSnapshot(val entries: List<GitHubTreeEntry>, val truncated: Boolean)

data class WantBranchDiscovery(
    val matches: List<WantBranchMatch>,
    val candidates: List<WantBranchCandidate>,
    val sourceRecords: List<KnowledgeNode>,
    val truncatedBranches: Set<String>
) {
    fun toNexusIndex(): NexusIndex = NexusIndex(sourceRecords, emptyList())
}

/**
 * Enumerates branch heads and source-tree metadata without checkout or mutation.
 * Candidate files remain UNKNOWN until their content is separately inspected.
 */
class GitHubWantBranchDiscovery(
    private val api: GitHubReadOnlyApi,
    private val detector: WantBranchDetector = WantBranchDetector(),
    private val maxBranches: Int = 200,
    private val perPage: Int = 100,
    private val maxArtifactsPerBranch: Int = 40
) {
    init {
        require(maxBranches in 1..1000)
        require(perPage in 1..100)
        require(maxArtifactsPerBranch in 1..200)
    }

    fun discover(repository: String, wantStatement: String): WantBranchDiscovery {
        require(REPOSITORY.matches(repository)) { "Repository must be owner/name." }
        require(wantStatement.isNotBlank()) { "A stated WANT is required for branch discovery." }

        val branches = mutableListOf<GitHubBranchRef>()
        var page = 1
        while (branches.size < maxBranches) {
            val requested = minOf(perPage, maxBranches - branches.size)
            val batch = api.listBranches(repository, page, requested)
            if (batch.isEmpty()) break
            branches += batch
            if (batch.size < requested) break
            page++
        }

        val wantTerms = tokens(wantStatement)
        val candidates = mutableListOf<WantBranchCandidate>()
        val allRecords = mutableListOf<KnowledgeNode>()
        val truncated = linkedSetOf<String>()

        branches.distinctBy { it.name }.forEach { branch ->
            require(SHA.matches(branch.headSha)) {
                "GitHub returned an invalid head SHA for branch ${branch.name}."
            }
            val tree = api.treeForCommit(repository, branch.headSha)
            if (tree.truncated) truncated += branch.name

            val matchingFiles = tree.entries.asSequence()
                .filter { it.type == "blob" && tokens(it.path).any { term -> term in wantTerms } }
                .take(maxArtifactsPerBranch)
                .toList()

            val records = matchingFiles.mapIndexed { index, entry ->
                KnowledgeNode(
                    id = "github:${branch.headSha.take(12)}:${entry.blobSha.take(12)}:$index",
                    title = entry.path,
                    claim = "Candidate source artifact; content has not yet been fetched or validated.",
                    kind = KnowledgeKind.OPEN_QUESTION,
                    evidence = listOf(
                        KnowledgeEvidence(
                            sourceRef = blobUrl(repository, branch.headSha, entry.path),
                            sourceRevision = branch.headSha,
                            contentDigest = entry.blobSha,
                            method = "GitHub read-only branch and recursive tree metadata; file content not fetched",
                            observedAt = null,
                            evidenceStatus = EvidenceStatus.UNKNOWN
                        )
                    ),
                    limitations = listOf(
                        "Path relevance is a discovery hint only.",
                        "Inspect content, tests, license, dependencies, and current branch head before relying on it."
                    ),
                    tags = tokens(entry.path)
                ).also(allRecords::add)
            }

            val pathSummary = matchingFiles.joinToString(" ") { it.path }
            candidates += WantBranchCandidate(
                branch = branch.name,
                repository = repository,
                headRevision = branch.headSha,
                summary = if (pathSummary.isBlank()) {
                    "Remote branch head; no source paths matched the WANT terms."
                } else {
                    "Candidate source paths: $pathSummary"
                },
                topics = tokens(branch.name),
                knowledge = records
            )
        }

        return WantBranchDiscovery(
            matches = detector.detect(wantStatement, candidates),
            candidates = candidates,
            sourceRecords = allRecords,
            truncatedBranches = truncated
        )
    }

    private fun blobUrl(repository: String, commitSha: String, path: String): String =
        "https://github.com/$repository/blob/$commitSha/" +
            path.split("/").joinToString("/") { encodeSegment(it) }

    private fun encodeSegment(value: String): String =
        java.net.URLEncoder.encode(value, Charsets.UTF_8.name()).replace("+", "%20")

    private fun tokens(value: String): Set<String> =
        Regex("[A-Za-z0-9][A-Za-z0-9._-]{1,}")
            .findAll(value.lowercase())
            .map { it.value.trim('.', '-', '_') }
            .filter { it.length >= 2 }
            .toSet()

    companion object {
        private val REPOSITORY = Regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
        private val SHA = Regex("^[0-9a-fA-F]{40}$")
    }
}

/** HTTPS GitHub implementation. This class issues GET requests only. */
class HttpGitHubReadOnlyApi(
    private val tokenProvider: () -> String?,
    private val apiBaseUrl: String = "https://api.github.com"
) : GitHubReadOnlyApi {
    init {
        require(apiBaseUrl.startsWith("https://")) { "GitHub API must use HTTPS." }
    }

    override fun listBranches(repository: String, page: Int, perPage: Int): List<GitHubBranchRef> {
        val json = JSONArray(get("/repos/$repository/branches?per_page=$perPage&page=$page"))
        return (0 until json.length()).map { index ->
            val item = json.getJSONObject(index)
            GitHubBranchRef(item.getString("name"), item.getJSONObject("commit").getString("sha"))
        }
    }

    override fun treeForCommit(repository: String, commitSha: String): GitHubTreeSnapshot {
        val commit = JSONObject(get("/repos/$repository/commits/$commitSha"))
        val treeSha = commit.getJSONObject("commit").getJSONObject("tree").getString("sha")
        val tree = JSONObject(get("/repos/$repository/git/trees/$treeSha?recursive=1"))
        val entries = tree.getJSONArray("tree")
        val parsed = (0 until entries.length()).map { index ->
            val item = entries.getJSONObject(index)
            GitHubTreeEntry(item.getString("path"), item.getString("sha"), item.getString("type"))
        }
        return GitHubTreeSnapshot(parsed, tree.optBoolean("truncated", false))
    }

    private fun get(path: String): String {
        val connection = URL(apiBaseUrl.trimEnd('/') + path).openConnection() as HttpURLConnection
        connection.requestMethod = "GET"
        connection.connectTimeout = 10_000
        connection.readTimeout = 20_000
        connection.instanceFollowRedirects = false
        connection.setRequestProperty("Accept", "application/vnd.github+json")
        connection.setRequestProperty("X-GitHub-Api-Version", "2022-11-28")
        tokenProvider()?.takeIf { it.isNotBlank() }?.let {
            connection.setRequestProperty("Authorization", "Bearer $it")
        }
        try {
            val code = connection.responseCode
            val stream = if (code in 200..299) connection.inputStream else connection.errorStream
            val buffer = ByteArrayOutputStream()
            stream?.use { input ->
                val chunk = ByteArray(8192)
                var total = 0
                while (true) {
                    val count = input.read(chunk)
                    if (count < 0) break
                    total += count
                    require(total <= MAX_RESPONSE_BYTES) { "GitHub response exceeds the 8 MB safety limit." }
                    buffer.write(chunk, 0, count)
                }
            }
            val body = buffer.toString(Charsets.UTF_8.name())
            if (code !in 200..299) {
                throw IllegalStateException("Read-only GitHub request failed ($code): $body")
            }
            return body
        } finally {
            connection.disconnect()
        }
    }

    companion object {
        private const val MAX_RESPONSE_BYTES = 8 * 1024 * 1024
    }
}
