package com.vanellye.eria

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.Button
import androidx.compose.material.Card
import androidx.compose.material.CircularProgressIndicator
import androidx.compose.material.MaterialTheme
import androidx.compose.material.OutlinedTextField
import androidx.compose.material.Surface
import androidx.compose.material.Text
import androidx.compose.material.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

private const val ERIA_API = "http://127.0.0.1:8765"

private data class RepositoryFile(val path: String, val size: Int)

@Composable
fun RepositoryDashboardScreen() {
    var tab by remember { mutableStateOf("Overview") }
    var connected by remember { mutableStateOf(false) }
    var loading by remember { mutableStateOf(false) }
    var fileCount by remember { mutableStateOf("—") }
    var root by remember { mutableStateOf("Start the ERIA Termux server") }
    var database by remember { mutableStateOf("—") }
    var indexedAt by remember { mutableStateOf("—") }
    var ponsPolicy by remember { mutableStateOf("PONS status unavailable") }
    var query by remember { mutableStateOf("") }
    var files by remember { mutableStateOf<List<RepositoryFile>>(emptyList()) }
    var message by remember { mutableStateOf("Connect to the local ERIA server to inspect repository metadata.") }
    val scope = rememberCoroutineScope()

    suspend fun refresh() {
        loading = true
        try {
            val status = withContext(Dispatchers.IO) { getJson("/api/status") }
            val index = status.getJSONObject("index")
            fileCount = index.optInt("files", 0).toString()
            root = status.optString("repository", "Unknown")
            database = status.optString("database", "Unknown")
            indexedAt = index.optString("indexed_at", "Not indexed")
            connected = true
            message = "Repository metadata connected."
            val pons = withContext(Dispatchers.IO) { getJson("/api/pons/status") }
            ponsPolicy = pons.optString("capability_policy", "Policy unavailable")
        } catch (error: Exception) {
            connected = false
            message = "Connection unavailable. Start the ERIA server in Termux. (" + error.javaClass.simpleName + ")"
        } finally {
            loading = false
        }
    }

    LaunchedEffect(Unit) { refresh() }

    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize(), color = Color(0xFF0B1020)) {
            Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Column {
                        Text("ERIA Repository", color = Color(0xFFE9EEF7), style = MaterialTheme.typography.h5, fontWeight = FontWeight.Bold)
                        Text("Repository intelligence · PONS governance", color = Color(0xFF9AABC3), style = MaterialTheme.typography.caption)
                    }
                    Text(if (connected) "CONNECTED" else "OFFLINE", color = if (connected) Color(0xFF83D6C2) else Color(0xFFFFB0A7), style = MaterialTheme.typography.caption)
                }
                Spacer(Modifier.height(16.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    listOf("Overview", "Files", "PONS").forEach { name ->
                        TextButton(onClick = { tab = name }) {
                            Text(name, color = if (tab == name) Color(0xFF83D6C2) else Color(0xFF9AABC3), fontWeight = if (tab == name) FontWeight.Bold else FontWeight.Normal)
                        }
                    }
                }
                Spacer(Modifier.height(8.dp))
                when (tab) {
                    "Files" -> {
                        OutlinedTextField(
                            value = query, onValueChange = { query = it },
                            modifier = Modifier.fillMaxWidth(), label = { Text("Search indexed paths") },
                            singleLine = true
                        )
                        Button(onClick = {
                            scope.launch {
                                loading = true
                                try {
                                    val encoded = java.net.URLEncoder.encode(query, "UTF-8")
                                    val result = withContext(Dispatchers.IO) { getJson("/api/files?q=$encoded") }
                                    val array = result.getJSONArray("files")
                                    files = (0 until array.length()).map { i ->
                                        val item = array.getJSONObject(i)
                                        RepositoryFile(item.optString("path"), item.optInt("size_bytes"))
                                    }
                                    message = "${files.size} matching paths."
                                } catch (error: Exception) {
                                    message = "Search failed: ${error.javaClass.simpleName}"
                                } finally { loading = false }
                            }
                        }, enabled = connected && query.isNotBlank()) { Text("Search") }
                        Text(message, color = Color(0xFF9AABC3), style = MaterialTheme.typography.caption)
                        LazyColumn {
                            items(files) { file ->
                                Card(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), backgroundColor = Color(0xFF141D31), shape = RoundedCornerShape(12.dp)) {
                                    Column(Modifier.padding(12.dp)) {
                                        Text(file.path, color = Color(0xFFE9EEF7))
                                        Text("${file.size} bytes", color = Color(0xFF9AABC3), style = MaterialTheme.typography.caption)
                                    }
                                }
                            }
                        }
                    }
                    "PONS" -> {
                        InfoCard("PONS ethics & authorization", "FAIL-CLOSED")
                        InfoCard("Decision policy", ponsPolicy)
                        InfoCard("Execution", "Disabled")
                        InfoCard("Git mutation", "Disabled")
                        InfoCard("Outbound transmission", "Disabled")
                        InfoCard("Human oversight", "No implicit consent. Missing, expired, or unverified grants remain on HOLD.")
                        InfoCard("Provenance", "Original source and derived records retain separate identities and hashes.")
                        Text("Inspection only: this screen does not create grants or execute protected actions.", color = Color(0xFFF2C879), style = MaterialTheme.typography.caption)
                    }
                    else -> {
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            MetricCard("Files", fileCount, Modifier.weight(1f))
                            MetricCard("Engine", if (connected) "Online" else "Offline", Modifier.weight(1f))
                            MetricCard("Mode", "Read-only", Modifier.weight(1f))
                        }
                        Spacer(Modifier.height(10.dp))
                        InfoCard("Repository root", root)
                        InfoCard("SQLite database", database)
                        InfoCard("Index timestamp", indexedAt)
                        InfoCard("Safeguards", "No Git history rewriting, automatic transmission, or source replacement.")
                        InfoCard("Status", message)
                        Button(onClick = { scope.launch { refresh() } }, enabled = !loading) {
                            Text("Refresh connection")
                        }
                        Button(onClick = {
                            scope.launch {
                                loading = true
                                try {
                                    withContext(Dispatchers.IO) { postJson("/api/index", "{}") }
                                    refresh()
                                    message = "Repository metadata index refreshed."
                                } catch (error: Exception) {
                                    message = "Index refresh failed: ${error.javaClass.simpleName}"
                                } finally { loading = false }
                            }
                        }, enabled = connected && !loading) { Text("Refresh repository index") }
                    }
                }
                if (loading) {
                    Spacer(Modifier.height(8.dp))
                    CircularProgressIndicator(color = Color(0xFF83D6C2))
                }
                Spacer(Modifier.height(8.dp))
                Text("Local Termux API · 127.0.0.1:8765 · No automatic repository mutation", color = Color(0xFF71829D), style = MaterialTheme.typography.caption)
            }
        }
    }
}

@Composable
private fun MetricCard(label: String, value: String, modifier: Modifier = Modifier) {
    Card(modifier = modifier, backgroundColor = Color(0xFF141D31), shape = RoundedCornerShape(12.dp)) {
        Column(Modifier.padding(12.dp)) {
            Text(value, color = Color(0xFFE9EEF7), fontWeight = FontWeight.Bold)
            Text(label, color = Color(0xFF9AABC3), style = MaterialTheme.typography.caption)
        }
    }
}

@Composable
private fun InfoCard(title: String, body: String) {
    Card(modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp), backgroundColor = Color(0xFF141D31), shape = RoundedCornerShape(12.dp)) {
        Column(Modifier.padding(12.dp)) {
            Text(title, color = Color(0xFF83D6C2), fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(4.dp))
            Text(body, color = Color(0xFFE9EEF7), style = MaterialTheme.typography.body2)
        }
    }
}

private fun getJson(path: String): JSONObject {
    val connection = (URL(ERIA_API + path).openConnection() as HttpURLConnection)
    connection.requestMethod = "GET"
    connection.connectTimeout = 2500
    connection.readTimeout = 3500
    return try {
        JSONObject(connection.inputStream.bufferedReader().use { it.readText() })
    } finally { connection.disconnect() }
}

private fun postJson(path: String, body: String): JSONObject {
    val connection = (URL(ERIA_API + path).openConnection() as HttpURLConnection)
    connection.requestMethod = "POST"
    connection.doOutput = true
    connection.connectTimeout = 2500
    connection.readTimeout = 5000
    connection.setRequestProperty("Content-Type", "application/json")
    return try {
        connection.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
        JSONObject(connection.inputStream.bufferedReader().use { it.readText() })
    } finally { connection.disconnect() }
}
