package com.vanellye.eria.filesystem

import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileInputStream
import java.security.MessageDigest

/**
 * Read-only, bounded inventory of a directory explicitly supplied by the caller.
 *
 * This class does not request permissions, persist results, follow symbolic links,
 * execute files, or modify the inspected tree. Android callers should pass only a
 * directory they obtained through an explicit user-granted Storage Access Framework
 * flow or an app-private directory.
 */
class FileSystemUnderstanding(
    private val limits: Limits = Limits()
) {
    data class Limits(
        val maxDepth: Int = 8,
        val maxFiles: Int = 500,
        val maxBytesPerFile: Int = 256 * 1024,
        val maxTotalBytes: Long = 8L * 1024 * 1024,
        val maxPreviewChars: Int = 4_000
    ) {
        init {
            require(maxDepth >= 0)
            require(maxFiles > 0)
            require(maxBytesPerFile > 0)
            require(maxTotalBytes > 0)
            require(maxPreviewChars > 0)
        }
    }

    data class FileRecord(
        val relativePath: String,
        val extension: String,
        val sizeBytes: Long,
        val sha256: String?,
        val contentKind: ContentKind,
        val preview: String? = null,
        val note: String? = null
    )

    enum class ContentKind { TEXT, BINARY, NOT_READ }

    data class ScanReport(
        val rootName: String,
        val files: List<FileRecord>,
        val directoriesVisited: Int,
        val bytesRead: Long,
        val truncated: Boolean,
        val notes: List<String>
    )

    fun scan(root: File): ScanReport {
        require(root.exists() && root.isDirectory) { "Root must be an existing directory" }
        require(root.canonicalFile == root.absoluteFile) {
            "Symbolic-link or non-canonical roots are not accepted"
        }

        val canonicalRoot = root.canonicalFile
        val queue = ArrayDeque<Pair<File, Int>>()
        queue.add(canonicalRoot to 0)
        val records = mutableListOf<FileRecord>()
        val notes = mutableListOf<String>()
        var directoriesVisited = 0
        var bytesRead = 0L
        var truncated = false

        while (queue.isNotEmpty()) {
            if (records.size >= limits.maxFiles) {
                truncated = true
                notes += "File-count limit reached"
                break
            }

            val (directory, depth) = queue.removeFirst()
            directoriesVisited++
            val children = directory.listFiles()?.sortedBy { it.name }
            if (children == null) {
                notes += "Directory could not be listed: ${relative(canonicalRoot, directory)}"
                continue
            }

            for (child in children) {
                if (isExcludedName(child.name)) continue
                if (child.canonicalFile != child.absoluteFile) {
                    notes += "Symbolic link skipped: ${relative(canonicalRoot, child)}"
                    continue
                }
                if (!child.canonicalFile.toPath().startsWith(canonicalRoot.toPath())) {
                    notes += "Path outside root skipped: ${child.name}"
                    continue
                }

                if (child.isDirectory) {
                    if (depth < limits.maxDepth) queue.add(child to depth + 1)
                    else {
                        truncated = true
                        notes += "Depth limit reached at: ${relative(canonicalRoot, child)}"
                    }
                    continue
                }
                if (!child.isFile) continue

                val path = relative(canonicalRoot, child)
                val extension = child.extension.lowercase()
                if (isSensitiveFile(child.name)) {
                    records += FileRecord(path, extension, child.length(), null, ContentKind.NOT_READ,
                        note = "Sensitive filename excluded")
                    continue
                }

                val size = child.length()
                if (size > limits.maxBytesPerFile) {
                    records += FileRecord(path, extension, size, null, ContentKind.NOT_READ,
                        note = "Per-file byte limit exceeded")
                    continue
                }
                if (bytesRead + size > limits.maxTotalBytes) {
                    truncated = true
                    notes += "Total byte limit reached"
                    break
                }

                val bytes = readBounded(child, limits.maxBytesPerFile)
                bytesRead += bytes.size
                val digest = sha256(bytes)
                if (!isTextCandidate(extension) || bytes.any { it == 0.toByte() }) {
                    records += FileRecord(path, extension, size, digest, ContentKind.BINARY)
                    continue
                }

                val decoded = bytes.toString(Charsets.UTF_8)
                val preview = redact(decoded).take(limits.maxPreviewChars)
                records += FileRecord(path, extension, size, digest, ContentKind.TEXT, preview)
            }
            if (truncated && bytesRead >= limits.maxTotalBytes) break
        }

        return ScanReport(
            rootName = canonicalRoot.name.ifBlank { canonicalRoot.path },
            files = records,
            directoriesVisited = directoriesVisited,
            bytesRead = bytesRead,
            truncated = truncated,
            notes = notes.distinct()
        )
    }

    private fun relative(root: File, file: File): String =
        file.relativeTo(root).invariantSeparatorsPath.ifBlank { "." }

    private fun readBounded(file: File, maxBytes: Int): ByteArray {
        val output = ByteArrayOutputStream()
        FileInputStream(file).use { input ->
            val buffer = ByteArray(8 * 1024)
            while (output.size() <= maxBytes) {
                val remaining = maxBytes + 1 - output.size()
                if (remaining <= 0) break
                val count = input.read(buffer, 0, minOf(buffer.size, remaining))
                if (count < 0) break
                output.write(buffer, 0, count)
            }
        }
        return output.toByteArray().take(maxBytes).toByteArray()
    }

    private fun sha256(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes)
            .joinToString("") { "%02x".format(it) }

    private fun isTextCandidate(extension: String): Boolean = extension in setOf(
        "md", "txt", "kt", "kts", "java", "py", "js", "ts", "json", "yaml", "yml",
        "xml", "html", "css", "sh", "c", "cc", "cpp", "h", "hpp", "gradle", "properties",
        "toml", "sql"
    )

    private fun isExcludedName(name: String): Boolean = name.lowercase() in setOf(
        ".git", ".gradle", ".idea", "build", "node_modules", ".ssh", ".aws",
        ".secrets", "secrets", "credentials", "__pycache__", ".venv", "venv"
    )

    private fun isSensitiveFile(name: String): Boolean {
        val lower = name.lowercase()
        return lower == ".env" || lower.startsWith(".env.") ||
            lower in setOf("id_rsa", "id_ed25519", "credentials", "secrets.json") ||
            lower.endsWith(".pem") || lower.endsWith(".key") ||
            lower.endsWith(".p12") || lower.endsWith(".pfx") ||
            lower.endsWith(".jks") || lower.endsWith(".keystore")
    }

    private fun redact(text: String): String {
        val assignments = Regex(
            """(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password)\s*[:=]\s*["']?[^\s"'\u0060,;]+"""
        )
        val bearer = Regex("""(?i)Bearer\s+[A-Za-z0-9._~+/=-]+""")
        val privateKey = Regex("""-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----""")
        return text.replace(privateKey, "[REDACTED PRIVATE KEY]")
            .replace(assignments) { "${it.groupValues[1]}=[REDACTED]" }
            .replace(bearer, "Bearer [REDACTED]")
    }
}
