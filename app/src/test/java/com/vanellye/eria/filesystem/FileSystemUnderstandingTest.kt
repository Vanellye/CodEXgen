package com.vanellye.eria.filesystem

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

class FileSystemUnderstandingTest {
    @get:Rule
    val temporaryFolder = TemporaryFolder()

    @Test
    fun inventoriesTextAndHashesWithoutChangingSourceFiles() {
        val root = temporaryFolder.newFolder("workspace")
        val source = root.resolve("notes.md").apply {
            writeText("# ERIA\nThis is a local note.")
        }
        val before = source.readBytes()

        val report = FileSystemUnderstanding().scan(root)

        assertEquals(1, report.files.size)
        val record = report.files.single()
        assertEquals("notes.md", record.relativePath)
        assertEquals(FileSystemUnderstanding.ContentKind.TEXT, record.contentKind)
        assertNotNull(record.sha256)
        assertTrue(record.preview!!.contains("This is a local note"))
        assertTrue(before.contentEquals(source.readBytes()))
        assertFalse(report.truncated)
    }

    @Test
    fun excludesSensitiveFilesAndBuildDirectories() {
        val root = temporaryFolder.newFolder("workspace")
        root.resolve(".env").writeText("API_KEY=do-not-read")
        root.resolve("build").apply { mkdirs() }.resolve("generated.kt").writeText("secret = false")
        root.resolve("safe.kt").writeText("fun main() = Unit")

        val report = FileSystemUnderstanding().scan(root)

        assertEquals(listOf("safe.kt"), report.files.map { it.relativePath })
    }

    @Test
    fun redactsCredentialLikeAssignmentsFromPreviews() {
        val root = temporaryFolder.newFolder("workspace")
        root.resolve("config.kt").writeText(
            """val apiKey = "abc123"\nval password = 'dont-show'\nval mode = "safe""""
        )

        val preview = FileSystemUnderstanding().scan(root).files.single().preview!!

        assertTrue(preview.contains("apiKey=[REDACTED]"))
        assertTrue(preview.contains("password=[REDACTED]"))
        assertFalse(preview.contains("abc123"))
        assertFalse(preview.contains("dont-show"))
    }

    @Test
    fun enforcesDepthAndPerFileSizeLimits() {
        val root = temporaryFolder.newFolder("workspace")
        val deep = root.resolve("one/two").apply { mkdirs() }
        deep.resolve("deep.md").writeText("too deep")
        root.resolve("large.md").writeText("0123456789")

        val report = FileSystemUnderstanding(
            FileSystemUnderstanding.Limits(maxDepth = 0, maxBytesPerFile = 4)
        ).scan(root)

        assertTrue(report.truncated)
        assertEquals(1, report.files.size)
        assertEquals(FileSystemUnderstanding.ContentKind.NOT_READ, report.files.single().contentKind)
        assertNull(report.files.single().sha256)
    }
}
