package com.vanellye.eria

import androidx.compose.foundation.clickable
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
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

private const val ERIA_API = "http://127.0.0.1:8765"
private val ERIA_BACKGROUND = Color(0xFF0B1020)
private val ERIA_PANEL = Color(0xFF141D31)
private val ERIA_TEXT = Color(0xFFE9EEF7)
private val ERIA_MUTED = Color(0xFF9AABC3)
private val ERIA_MINT = Color(0xFF83D6C2)
private val ERIA_AMBER = Color(0xFFF2C879)

private data class RepositoryFile(
    val path: String,
    val size: Long,
    val sha256: String = "",
    val extension: String = ""
)

private data class AuditEvent(
    val id: Long,
    val event: String,
    val status: String,
    val detail: String,
    val createdAt: String
)

private data class AuthorizationRequest(
    val id: String,
    val capability: String,
    val scope: String,
    val reason: String,
    val status: String,
    val createdAt: String
)

@Composable
fun RepositoryDashboardScreen() {
    var tab by remember { mutableStateOf("Overview") }
    var connected by remember { mutableStateOf(false) }
    var loading by remember { mutableStateOf(false) }
    var fileCount by remember { mutableStateOf("—") }
    var root by remember { mutableStateOf("Start the ERIA Termux server") }
    var database by remember { mutableStateOf("—") }
    var indexedAt by remember { mutableStateOf("—") }
    var engineMode by remember { mutableStateOf("Offline") }
    var ponsPolicy by remember { mutableStateOf("PONS status unavailable") }
    var executionEnabled by remember { mutableStateOf(false) }
    var gitMutationEnabled by remember { mutableStateOf(false) }
    var transmissionEnabled by remember { mutableStateOf(false) }
    var approvalSupported by remember { mutableStateOf(false) }
    var query by remember { mutableStateOf("") }
    var files by remember { mutableStateOf<List<RepositoryFile>>(emptyList()) }
    var provenance by remember { mutableStateOf<List<RepositoryFile>>(emptyList()) }
    var audit by remember { mutableStateOf<List<AuditEvent>>(emptyList()) }
    var requests by remember { mutableStateOf<List<AuthorizationRequest>>(emptyList()) }
    var selectedPath by remember { mutableStateOf("") }
    var selectedPreview by remember { mutableStateOf("") }
    var selectedHash by remember { mutableStateOf("") }
    var capability by remember { mutableStateOf("repository.read") }
    var scope by remember { mutableStateOf("") }
    var reason by remember { mutableStateOf("") }
    var message by remember { mutableStateOf("Connect to the local ERIA server to inspect repository metadata.") }
    val scopeCoroutine = rememberCoroutineScope()

    suspend fun loadStatus() {
        try {
            val status = withContext(Dispatchers.IO) { getJson("/api/status") }
            val index = status.optJSONObject("index") ?: JSONObject()
            fileCount = index.optInt("files", 0).toString()
            root = status.optString("repository", "Unknown")
            database = status.optString("database", "Unknown")
            indexedAt = index.optString("indexed_at", "Not indexed")
            engineMode = status.optString("mode", "Read-only")
            connected = true
            message = "Repository metadata connected."
        } catch (error: Exception) {
            connected = false
            engineMode = "Offline"
            message = "Repository API unavailable. Start the Termux server. (" + error.javaClass.simpleName + ")"
        }
    }

    suspend fun loadPons() {
        try {
            val pons = withContext(Dispatchers.IO) { getJson("/api/pons/status") }
            ponsPolicy = pons.optString("capability_policy", "Policy unavailable")
            executionEnabled = pons.optBoolean("execution_enabled", false)
            gitMutationEnabled = pons.optBoolean("git_mutation_enabled", false)
            transmissionEnabled = pons.optBoolean("transmission_enabled", false)
        } catch (error: Exception) {
            ponsPolicy = "PONS API unavailable: " + error.javaClass.simpleName
        }
        try {
            val response = withContext(Dispatchers.IO) { getJson("/api/pons/requests") }
            approvalSupported = response.optBoolean("approval_supported", false)
            requests = response.optJSONArray("requests").toRequestList()
        } catch (_: Exception) {
            approvalSupported = false
        }
    }

    suspend fun loadAudit() {
        try {
            val response = withContext(Dispatchers.IO) { getJson("/api/audit") }
            audit = response.optJSONArray("events").toAuditList()
        } catch (error: Exception) {
            message = "Audit history unavailable: " + error.javaClass.simpleName
        }
    }

    suspend fun loadProvenance(term: String = "") {
        try {
            val encoded = URLEncoder.encode(term, "UTF-8")
            val response = withContext(Dispatchers.IO) { getJson("/api/provenance?q=" + encoded) }
            provenance = response.optJSONArray("records").toFileList()
        } catch (error: Exception) {
            message = "Provenance unavailable: " + error.javaClass.simpleName
        }
    }

    suspend fun refreshAll(showSpinner: Boolean = true) {
        if (showSpinner) loading = true
        try {
            loadStatus()
            if (connected) {
                loadPons()
                loadAudit()
                loadProvenance()
            }
        } finally {
            if (showSpinner) loading = false
        }
    }

    LaunchedEffect(Unit) { refreshAll() }

    // Poll only while this dashboard remains composed; all network I/O stays off the UI thread.
    LaunchedEffect(Unit) {
        while (true) {
            delay(15000)
            if (!loading) refreshAll(showSpinner = false)
        }
    }

    LaunchedEffect(query, tab, connected) {
        if (tab == "Files" && connected && query.trim().length >= 2) {
            delay(350)
            try {
                val encoded = URLEncoder.encode(query.trim(), "UTF-8")
                val result = withContext(Dispatchers.IO) { getJson("/api/files?q=" + encoded) }
                files = result.optJSONArray("files").toFileList()
            } catch (error: Exception) {
                message = "File search failed: " + error.javaClass.simpleName
            }
        } else if (tab == "Files" && query.isBlank()) {
            files = emptyList()
        }
    }

    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize(), color = ERIA_BACKGROUND) {
            Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Column {
                        Text("ERIA Repository", color = ERIA_TEXT, style = MaterialTheme.typography.h5, fontWeight = FontWeight.Bold)
                        Text("Repository intelligence · PONS governance", color = ERIA_MUTED, style = MaterialTheme.typography.caption)
                    }
                    Text(if (connected) "CONNECTED" else "OFFLINE", color = if (connected) ERIA_MINT else Color(0xFFFFB0A7), style = MaterialTheme.typography.caption)
                }
                Spacer(Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(2.dp)) {
                    listOf("Overview", "Files", "Provenance", "Audit", "PONS").forEach { name ->
                        TextButton(onClick = { tab = name }) {
                            Text(name, color = if (tab == name) ERIA_MINT else ERIA_MUTED, fontWeight = if (tab == name) FontWeight.Bold else FontWeight.Normal)
                        }
                    }
                }

                when (tab) {
                    "Files" -> {
                        OutlinedTextField(
                            value = query, onValueChange = { query = it },
                            modifier = Modifier.fillMaxWidth(), label = { Text("Search repository paths") },
                            singleLine = true
                        )
                        Text(
                            if (query.length < 2) "Type at least two characters. Results are indexed paths."
                            else files.size.toString() + " matching paths",
                            color = ERIA_MUTED, style = MaterialTheme.typography.caption
                        )
                        LazyColumn(modifier = Modifier.weight(1f)) {
                            items(files, key = { it.path }) { file ->
                                Card(
                                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp).clickable {
                                        scopeCoroutine.launch {
                                            try {
                                                val encoded = URLEncoder.encode(file.path, "UTF-8")
                                                val detail = withContext(Dispatchers.IO) { getJson("/api/files/detail?path=" + encoded) }
                                                selectedPath = detail.optString("path", file.path)
                                                selectedPreview = detail.optString("content_preview", "")
                                                selectedHash = detail.optJSONObject("provenance")?.optString("source_sha256", "").orEmpty()
                                            } catch (error: Exception) {
                                                message = "File inspection failed: " + error.javaClass.simpleName
                                            }
                                        }
                                    },
                                    backgroundColor = ERIA_PANEL, shape = RoundedCornerShape(12.dp)
                                ) {
                                    Column(Modifier.padding(12.dp)) {
                                        Text(file.path, color = ERIA_TEXT, fontWeight = FontWeight.Medium)
                                        Text(file.size.toString() + " bytes · " + file.extension, color = ERIA_MUTED, style = MaterialTheme.typography.caption)
                                    }
                                }
                            }
                        }
                        if (selectedPath.isNotBlank()) {
                            InfoCard("Selected file · " + selectedPath, "SHA-256: " + selectedHash.ifBlank { "not computed" } + "\n\n" + selectedPreview.take(1800))
                        }
                    }
                    "Provenance" -> {
                        Text("Original-source identity is separate from derived output. Hashes are calculated for eligible files up to 5 MiB.", color = ERIA_MUTED, style = MaterialTheme.typography.caption)
                        LazyColumn(modifier = Modifier.weight(1f)) {
                            items(provenance, key = { it.path }) { record ->
                                InfoCard(
                                    record.path,
                                    "Source SHA-256: " + record.sha256.ifBlank { "not computed (size limit or unavailable)" } +
                                        "\nSize: " + record.size + " bytes\nType: " + record.extension +
                                        "\nAuthority: NON_AUTHORITATIVE"
                                )
                            }
                        }
                        InfoCard("Derived records", "This dashboard service does not generate derived records. When another ERIA pipeline creates one, it must retain the original source ID and source hash and store its derived hash separately.")
                    }
                    "Audit" -> {
                        Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                            Text("Append-only local event history", color = ERIA_TEXT, fontWeight = FontWeight.SemiBold)
                            TextButton(onClick = { scopeCoroutine.launch { loadAudit() } }) { Text("Refresh", color = ERIA_MINT) }
                        }
                        LazyColumn(modifier = Modifier.weight(1f)) {
                            items(audit, key = { it.id }) { event ->
                                InfoCard(
                                    "#" + event.id + " · " + event.event,
                                    event.status + " · " + event.createdAt + "\n" + event.detail
                                )
                            }
                        }
                        if (audit.isEmpty()) Text("No audit events are available yet.", color = ERIA_MUTED)
                    }
                    "PONS" -> {
                        InfoCard("PONS ethics & authorization", "FAIL-CLOSED")
                        InfoCard("Decision policy", ponsPolicy)
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            MetricCard("Execution", if (executionEnabled) "Enabled" else "Disabled", Modifier.weight(1f))
                            MetricCard("Git writes", if (gitMutationEnabled) "Enabled" else "Disabled", Modifier.weight(1f))
                            MetricCard("Transmission", if (transmissionEnabled) "Enabled" else "Disabled", Modifier.weight(1f))
                        }
                        InfoCard("Human oversight", "No implicit consent. Requests begin on HOLD. This dashboard cannot approve grants or execute protected actions.")
                        InfoCard("Decision states", "HOLD: missing, unverified, or out-of-scope approval. PROPOSAL_ONLY: eligible for human review, not execution. REVIEW_READY: evidence package is ready for review, not a grant. Current request submissions remain HOLD.")
                        InfoCard("Authorization request", "Create a review request. This records a proposal only; it does not grant permission.")
                        OutlinedTextField(value = capability, onValueChange = { capability = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Capability") }, singleLine = true)
                        OutlinedTextField(value = scope, onValueChange = { scope = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Exact scope") }, singleLine = true)
                        OutlinedTextField(value = reason, onValueChange = { reason = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Reason") })
                        Button(
                            onClick = {
                                scopeCoroutine.launch {
                                    loading = true
                                    try {
                                        val body = JSONObject().put("capability", capability).put("scope", scope).put("reason", reason)
                                        withContext(Dispatchers.IO) { postJson("/api/pons/requests", body.toString()) }
                                        reason = ""
                                        loadPons()
                                        loadAudit()
                                        message = "Request recorded as HOLD. No approval was created."
                                    } catch (error: Exception) {
                                        message = "Request failed: " + error.javaClass.simpleName
                                    } finally { loading = false }
                                }
                            },
                            enabled = connected && !loading && capability.isNotBlank() && scope.isNotBlank() && reason.isNotBlank()
                        ) { Text("Submit review request · HOLD") }
                        Text(
                            if (approvalSupported) "An external approval authority is configured."
                            else "Approval authority is not configured. Requests remain HOLD.",
                            color = ERIA_AMBER, style = MaterialTheme.typography.caption
                        )
                        Text("Requests", color = ERIA_TEXT, fontWeight = FontWeight.SemiBold)
                        LazyColumn(modifier = Modifier.weight(1f)) {
                            items(requests, key = { it.id }) { request ->
                                InfoCard(
                                    request.capability + " · " + request.status,
                                    "Scope: " + request.scope + "\nReason: " + request.reason +
                                        "\nID: " + request.id + "\n" + request.createdAt
                                )
                            }
                        }
                    }
                    else -> {
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            MetricCard("Files", fileCount, Modifier.weight(1f))
                            MetricCard("Engine", if (connected) "Online" else "Offline", Modifier.weight(1f))
                            MetricCard("Mode", "Read-only", Modifier.weight(1f))
                        }
                        InfoCard("Repository root", root)
                        InfoCard("SQLite database", database)
                        InfoCard("Index timestamp", indexedAt)
                        InfoCard("Safeguards", "No Git history rewriting, source replacement, automatic execution, or outbound transmission.")
                        InfoCard("Status", message)
                        Button(onClick = { scopeCoroutine.launch { refreshAll() } }, enabled = !loading) { Text("Refresh dashboard") }
                        Button(
                            onClick = {
                                scopeCoroutine.launch {
                                    loading = true
                                    try {
                                        withContext(Dispatchers.IO) { postJson("/api/index", "{}") }
                                        refreshAll(showSpinner = false)
                                        message = "Repository metadata and source hashes refreshed."
                                    } catch (error: Exception) {
                                        message = "Index refresh failed: " + error.javaClass.simpleName
                                    } finally { loading = false }
                                }
                            },
                            enabled = connected && !loading
                        ) { Text("Refresh repository index") }
                    }
                }

                if (loading) {
                    Spacer(Modifier.height(8.dp))
                    CircularProgressIndicator(color = ERIA_MINT)
                }
                Spacer(Modifier.height(6.dp))
                Text("Local Termux API · 127.0.0.1:8765 · source-preserving · no automatic repository mutation", color = Color(0xFF71829D), style = MaterialTheme.typography.caption)
            }
        }
    }
}

@Composable
private fun MetricCard(label: String, value: String, modifier: Modifier = Modifier) {
    Card(modifier = modifier, backgroundColor = ERIA_PANEL, shape = RoundedCornerShape(12.dp)) {
        Column(Modifier.padding(10.dp)) {
            Text(value, color = ERIA_TEXT, fontWeight = FontWeight.Bold)
            Text(label, color = ERIA_MUTED, style = MaterialTheme.typography.caption)
        }
    }
}

@Composable
private fun InfoCard(title: String, body: String) {
    Card(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), backgroundColor = ERIA_PANEL, shape = RoundedCornerShape(12.dp)) {
        Column(Modifier.padding(12.dp)) {
            Text(title, color = ERIA_MINT, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(4.dp))
            Text(body, color = ERIA_TEXT, style = MaterialTheme.typography.body2)
        }
    }
}

private fun JSONArray?.toFileList(): List<RepositoryFile> {
    if (this == null) return emptyList()
    return (0 until length()).map { index ->
        val item = getJSONObject(index)
        RepositoryFile(
            path = item.optString("path"),
            size = item.optLong("size_bytes"),
            sha256 = item.optString("source_sha256"),
            extension = item.optString("extension")
        )
    }
}

private fun JSONArray?.toAuditList(): List<AuditEvent> {
    if (this == null) return emptyList()
    return (0 until length()).map { index ->
        val item = getJSONObject(index)
        AuditEvent(
            id = item.optLong("id"),
            event = item.optString("event"),
            status = item.optString("status"),
            detail = item.optJSONObject("detail")?.toString() ?: "{}",
            createdAt = item.optString("created_at")
        )
    }
}

private fun JSONArray?.toRequestList(): List<AuthorizationRequest> {
    if (this == null) return emptyList()
    return (0 until length()).map { index ->
        val item = getJSONObject(index)
        AuthorizationRequest(
            id = item.optString("request_id"),
            capability = item.optString("capability"),
            scope = item.optString("scope"),
            reason = item.optString("reason"),
            status = item.optString("status", "HOLD"),
            createdAt = item.optString("created_at")
        )
    }
}

private fun getJson(path: String): JSONObject {
    val connection = URL(ERIA_API + path).openConnection() as HttpURLConnection
    connection.requestMethod = "GET"
    connection.connectTimeout = 2500
    connection.readTimeout = 5000
    return try {
        readResponse(connection)
    } finally { connection.disconnect() }
}

private fun postJson(path: String, body: String): JSONObject {
    val connection = URL(ERIA_API + path).openConnection() as HttpURLConnection
    connection.requestMethod = "POST"
    connection.doOutput = true
    connection.connectTimeout = 2500
    connection.readTimeout = 7000
    connection.setRequestProperty("Content-Type", "application/json")
    return try {
        connection.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
        readResponse(connection)
    } finally { connection.disconnect() }
}

private fun readResponse(connection: HttpURLConnection): JSONObject {
    val code = connection.responseCode
    val stream = if (code in 200..299) connection.inputStream else connection.errorStream
    val body = stream?.bufferedReader()?.use { it.readText() }.orEmpty()
    if (code !in 200..299) throw IllegalStateException("HTTP " + code + ": " + body)
    return JSONObject(body)
}
