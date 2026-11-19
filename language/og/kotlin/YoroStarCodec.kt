package org.eria.yoro

import java.io.File

/** Ɣơ/2 byte codec. This is a reversible text encoding, not a replacement for binary storage. */
object YoroStarCodec {
    private const val PREFIX = "Ɣơ/2:"
    fun encode(bytes: ByteArray): String = PREFIX + bytes.joinToString(".") { byte ->
        (7 downTo 0).joinToString("") { bit ->
            if ((((byte.toInt() and 0xff) ushr bit) and 1) == 1) "k" else "☆"
        }
    }

    fun decode(text: String): ByteArray {
        require(text.startsWith(PREFIX)) { "Unsupported Ɣơ profile" }
        val body = text.removePrefix(PREFIX)
        if (body.isEmpty()) return byteArrayOf()
        val groups = body.split(".")
        require(groups.all { it.length == 8 && it.all { c -> c == '☆' || c == 'k' } }) {
            "Each byte must contain exactly eight ☆/k symbols"
        }
        return groups.map { group ->
            var value = 0
            group.forEach { c -> value = (value shl 1) or if (c == 'k') 1 else 0 }
            value.toByte()
        }.toByteArray()
    }

    /** Reads the repository's language-neutral TSV vectors and checks exact parity. */
    fun validateVectors(file: File): Int {
        var count = 0
        file.readLines().filter { it.isNotBlank() && !it.startsWith("#") }.forEach { line ->
            val fields = line.split("|")
            require(fields.size == 3) { "Malformed vector: $line" }
            val expected = fields[1].chunked(2).filter { it.isNotEmpty() }
                .map { it.toInt(16).toByte() }.toByteArray()
            require(encode(expected) == fields[2]) { "Encode mismatch: ${fields[0]}" }
            require(decode(fields[2]).contentEquals(expected)) { "Decode mismatch: ${fields[0]}" }
            count++
        }
        return count
    }
}

fun main(args: Array<String>) {
    require(args.size == 1) { "Usage: YoroStarCodec <path-to-yoro-star-v2.tsv>" }
    println("Kotlin Ɣơ/2 vectors passed: ${YoroStarCodec.validateVectors(File(args[0]))}")
}
