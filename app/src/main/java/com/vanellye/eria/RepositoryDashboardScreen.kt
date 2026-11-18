package com.vanellye.eria

import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.rememberScrollState
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
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.CancellationException
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
private const val REFRESH_INTERVAL_MS = 15_000L
private const val SEARCH_DEBOUNCE_MS = 350L
private val ERIA_BACKGROUND = Color(0xFF0B1020)
private val ERIA_PANEL = Color(0xFF141D31)
private val ERIA_TEXT = Color(0xFFE9EEF7)
private val ERIA_MUTED = Color(0xFF9AABC3)
private val ERIA_MINT = Color(0xFF83D6C2)
private val ERIA_AMBER = Color(0xFFF2C879)
private val ERIA_RED = Color(0xFFFFB0A7)

private enum class DashboardTab(val label: String) {
    OVERVIEW("Overview"),
    FILES("Files"),
    PROVENANCE("Provenance"),
    AUDIT("Audit"),
    PONS("PONS")
}

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
fun RepositoryDashboardScreen(modifier: Modifier = Modifier) {
    val lifecycleOwner = LocalLifecycleOwner.current
    val coroutineScope = rememberCoroutineScope()

    var tab by remember { mutableStateOf(DashboardTab.OVERVIEW) }
    var connected by remember { mutableStateOf(false) }
    var loading by remember { mutableStateOf(false) }
    var submittingRequest by remember { mutableStateOf(false) }

    var fileCount by remember { mutableStateOf("—") }
    var repositoryRoot by remember { mutableStateOf("Start the ERIA Termux server") }
    var databasePath by remember { mutableStateOf("—") }
    var indexedAt by remember { mutableStateOf("—") }
    var engineName by remember { mutableStateOf("ERIA Repository Conversation Engine") }
    var engineMode by remember { mutableStateOf("Offline") }

    var ponsPolicy by remember { mutableStateOf("PONS status unavailable") }
    var executionEnabled by remember { mutableStateOf(false) }
    var gitMutationEnabled by remember { mutableStateOf(false) }
    var transmissionEnabled by remember { mutableStateOf(false) }
    var approvalSupported by remember { mutableStateOf(false) }

    var fileQuery by remember { mutableStateOf("") }
    var provenanceQuery by remember { mutableStateOf("") }
    var files by remember { mutableStateOf<List<RepositoryFile>>(emptyList()) }
    var provenance by remember { mutableStateOf<List<RepositoryFile>>(emptyList()) }
    var auditEvents by remember { mutableStateOf<List<AuditEvent>>(emptyList()) }
    var authorizationRequests by remember { mutableStateOf<List<AuthorizationRequest>>(emptyList()) }

    var selectedPath by remember { mutableStateOf("") }
    var selectedPreview by remember { mutableStateOf("") }
    var selectedHash by remember { mutableStateOf("") }
    var previewLoading by remember { mutableStateOf(false) }

    var capability by remember { mutableStateOf("repository.read") }
    var requestedScope by remember { mutableStateOf("") }
    var requestReason by remember { mutableStateOf("") }

    var statusMessage by remember {
        mutableStateOf("Connect to the local ERIA server to inspect repository metadata.")
    }
    var filesError by remember { mutableStateOf("") }
    var provenanceError by remember { mutableStateOf("") }
    var auditError by remember { mutableStateOf("") }
    var ponsError by remember { mutableStateOf("") }

    suspend fun loadStatus() {
        try {
            val status = withContext(Dispatchers.IO) { eriaGet("/api/status") }
            val index = status.optJSONObject("index") ?: JSONObject()
            fileCount = index.optInt("files", 0).toString()
            repositoryRoot = status.optString("repository", "Unknown")
            databasePath = status.optString("database", "Unknown")
            indexedAt = index.optString("indexed_at", "Not indexed")
            engineName = status.optString("engine", "ERIA Repository Conversation Engine")
            engineMode = status.optString("mode", "Read-only inspection")
            connected = true
            statusMessage = "Repository metadata connected."
        } catch (error: CancellationException) {
            throw error
        } catch (error: Exception) {
            connected = false
            engineMode = "Offline"
            statusMessage = "Repository API unavailable. Start the Termux server. (" +
                error.javaClass.simpleName + ")"
        }
    }

    suspend fun loadPons() {
        try {
            val pons = withContext(Dispatchers.IO) { eriaGet("/api/pons/status") }
            ponsPolicy = pons.optString("capability_policy", "Policy unavailable")
            executionEnabled = pons.optBoolean("execution_enabled", false)
            gitMutationEnabled = pons.optBoolean("git_mutation_enabled", false)
            transmissionEnabled = pons.optBoolean("transmission_enabled", false)
            ponsError = ""
        } catch (error: CancellationException) {
            throw error
        } catch (error: Exception) {
            ponsError = "PONS policy unavailable: " + error.javaClass.simpleName
        }

        try {
            val response = withContext(Dispatchers.IO) { eriaGet("/api/pons/requests") }
            approvalSupported = response.optBoolean("approval_supported", false)
            authorizationRequests = response.optJSONArray("requests").toAuthorizationRequests()
        } catch (error: CancellationException) {
            throw error
        } catch (error: Exception) {
            approvalSupported = false
            ponsError = "Authorization queue unavailable: " + error.javaClass.simpleName
        }
    }

    suspend fun loadAudit() {
        try {
            val response = withContext(Dispatchers.IO) { eriaGet("/api/audit") }
            auditEvents = response.optJSONArray("events").toAuditEvents()
            auditError = ""
        } catch (error: CancellationException) {
            throw error
        } catch (error: Exception) {
            auditError = "Audit history unavailable: " + error.javaClass.simpleName
        }
    }

    suspend fun loadProvenance(term: String = provenanceQuery) {
        try {
            val encoded = URLEncoder.encode(term, "UTF-8")
            val response = withContext(Dispatchers.IO) {
                eriaGet("/api/provenance?q=" + encoded)
            }
            provenance = response.optJSONArray("records").toRepositoryFiles()
            provenanceError = ""
        } catch (error: CancellationException) {
            throw error
        } catch (error: Exception) {
            provenanceError = "Provenance unavailable: " + error.javaClass.simpleName
        }
    }

    suspend fun loadFiles(term: String) {
        if (term.trim().length < 2) {
            files = emptyList()
            filesError = ""
            return
        }
        try {
            val encoded = URLEncoder.encode(term.trim(), "UTF-8")
            val response = withContext(Dispatchers.IO) {
                eriaGet("/api/files?q=" + encoded)
            }
            files = response.optJSONArray("files").toRepositoryFiles()
            filesError = ""
        } catch (error: CancellationException) {
            throw error
        } catch (error: Exception) {
            filesError = "File search failed: " + error.javaClass.simpleName
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

    LaunchedEffect(lifecycleOwner) {
        lifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
            refreshAll(showSpinner = false)
            while (true) {
                delay(REFRESH_INTERVAL_MS)
                refreshAll(showSpinner = false)
            }
        }
    }

    LaunchedEffect(fileQuery, tab, connected) {
        if (tab == DashboardTab.FILES && connected && fileQuery.trim().length >= 2) {
            delay(SEARCH_DEBOUNCE_MS)
            loadFiles(fileQuery)
        } else if (tab == DashboardTab.FILES && fileQuery.isBlank()) {
            files = emptyList()
            filesError = ""
        }
    }

    suspend fun loadFilePreview(file: RepositoryFile) {
        previewLoading = true
        selectedPath = file.path
        selectedPreview = ""
        selectedHash = file.sha256
        try {
            val encoded = URLEncoder.encode(file.path, "UTF-8")
            val detail = withContext(Dispatchers.IO) {
                eriaGet("/api/files/detail?path=" + encoded)
            }
            selectedPath = detail.optString("path", file.path)
            selectedPreview = detail.optString("content_preview", "")
            selectedHash = detail.optJSONObject("provenance")
                ?.optString("source_sha256", file.sha256).orEmpty()
        } catch (error: CancellationException) {
            throw error
        } catch (error: Exception) {
            selectedPreview = "File inspection failed: " + error.javaClass.simpleName
        } finally {
            previewLoading = false
        }
    }

    suspend fun submitAuthorizationRequest() {
        if (capability.isBlank() || requestedScope.isBlank() || requestReason.isBlank()) {
            ponsError = "Complete all three fields before submitting a review request."
            return
        }
        submittingRequest = true
        ponsError = ""
        try {
            val body = JSONObject()
                .put("capability", capability.trim())
                .put("scope", requestedScope.trim())
                .put("reason", requestReason.trim())
            withContext(Dispatchers.IO) {
                eriaPost("/api/pons/requests", body)
            }
            requestReason = ""
            loadPons()
            loadAudit()
            statusMessage = "Request recorded as HOLD. No approval was created."
        } catch (error: CancellationException) {
            throw error
        } catch (error: Exception) {
            ponsError = "Request failed: " + error.javaClass.simpleName
        } finally {
            submittingRequest = false
        }
    }

    MaterialTheme {
        Surface(modifier = modifier.fillMaxSize(), color = ERIA_BACKGROUND) {
            Column(
                modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp, vertical = 12.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            "ERIA Repository",
                            color = ERIA_TEXT,
                            style = MaterialTheme.typography.h5,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            "Repository intelligence · PONS governance",
                            color = ERIA_MUTED,
                            style = MaterialTheme.typography.caption
                        )
                    }
                    Column(horizontalAlignment = androidx.compose.ui.Alignment.End) {
                        Text(
                            if (connected) "CONNECTED" else "OFFLINE",
                            color = if (connected) ERIA_MINT else ERIA_RED,
                            style = MaterialTheme.typography.caption,
                            fontWeight = FontWeight.Bold
                        )
                        if (loading) {
                            CircularProgressIndicator(
                                modifier = Modifier.padding(top = 4.dp),
                                color = ERIA_MINT,
                                strokeWidth = 2.dp
                            )
                        }
                    }
                }

                Spacer(Modifier.height(10.dp))
                Row(
                    modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(2.dp)
                ) {
                    DashboardTab.values().forEach { item ->
                        TextButton(onClick = { tab = item }) {
                            Text(
                                item.label,
                                color = if (tab == item) ERIA_MINT else ERIA_MUTED,
                                fontWeight = if (tab == item) FontWeight.Bold else FontWeight.Normal
                            )
                        }
                    }
                }

                when (tab) {
                    DashboardTab.OVERVIEW -> {
                        LazyColumn(
                            modifier = Modifier.weight(1f),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            item {
                                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                    MetricCard("Files", fileCount, Modifier.weight(1f))
                                    MetricCard("Engine", if (connected) "Online" else "Offline", Modifier.weight(1f))
                                    MetricCard("Mode", "Read-only", Modifier.weight(1f))
                                }
                            }
                            item { InfoCard("Repository root", repositoryRoot) }
                            item { InfoCard("SQLite database", databasePath) }
                            item { InfoCard("Index timestamp", indexedAt) }
                            item { InfoCard("Conversation engine", engineName + "\n" + engineMode) }
                            item {
                                InfoCard(
                                    "Safeguards",
                                    "No Git history rewriting, source replacement, automatic execution, or outbound transmission."
                                )
                            }
                            item { StatusCard(statusMessage, connected) }
                            item {
                                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                    Button(
                                        onClick = { coroutineScope.launch { refreshAll() } },
                                        enabled = !loading
                                    ) { Text("Refresh dashboard") }
                                    Button(
                                        onClick = {
                                            coroutineScope.launch {
                                                loading = true
                                                try {
                                                    withContext(Dispatchers.IO) {
                                                        eriaPost("/api/index", JSONObject())
                                                    }
                                                    refreshAll(showSpinner = false)
                                                    statusMessage = "Repository metadata and source hashes refreshed."
                                                } catch (error: Exception) {
                                                    statusMessage = "Index refresh failed: " +
                                                        error.javaClass.simpleName
                                                } finally {
                                                    loading = false
                                                }
                                            }
                                        },
                                        enabled = connected && !loading
                                    ) { Text("Refresh index") }
                                }
                            }
                        }
                    }

                    DashboardTab.FILES -> {
                        Column(modifier = Modifier.weight(1f)) {
                            OutlinedTextField(
                                value = fileQuery,
                                onValueChange = { fileQuery = it },
                                modifier = Modifier.fillMaxWidth(),
                                label = { Text("Search repository paths") },
                                singleLine = true
                            )
                            Text(
                                if (fileQuery.trim().length < 2) {
                                    "Type at least two characters. Results are indexed paths."
                                } else {
                                    files.size.toString() + " matching paths"
                                },
                                color = ERIA_MUTED,
                                style = MaterialTheme.typography.caption
                            )
                            if (filesError.isNotBlank()) StatusCard(filesError, false)
                            LazyColumn(
                                modifier = Modifier.weight(1f),
                                verticalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                items(files, key = { it.path }) { file ->
                                    Card(
                                        modifier = Modifier.fillMaxWidth().clickable {
                                            coroutineScope.launch { loadFilePreview(file) }
                                        },
                                        backgroundColor = ERIA_PANEL,
                                        shape = RoundedCornerShape(12.dp)
                                    ) {
                                        Column(Modifier.padding(12.dp)) {
                                            Text(file.path, color = ERIA_TEXT, fontWeight = FontWeight.Medium)
                                            Text(
                                                file.size.toString() + " bytes · " + file.extension,
                                                color = ERIA_MUTED,
                                                style = MaterialTheme.typography.caption
                                            )
                                        }
                                    }
                                }
                            }
                            if (selectedPath.isNotBlank()) {
                                InfoCard(
                                    "Selected file · " + selectedPath,
                                    (if (previewLoading) "Loading preview…\n" else "") +
                                        "SHA-256: " + selectedHash.ifBlank { "not computed" } +
                                        "\n\n" + selectedPreview.take(1800)
                                )
                            }
                        }
                    }

                    DashboardTab.PROVENANCE -> {
                        Column(modifier = Modifier.weight(1f)) {
                            OutlinedTextField(
                                value = provenanceQuery,
                                onValueChange = { provenanceQuery = it },
                                modifier = Modifier.fillMaxWidth(),
                                label = { Text("Filter provenance by path") },
                                singleLine = true
                            )
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Button(
                                    onClick = { coroutineScope.launch { loadProvenance(provenanceQuery) } },
                                    enabled = connected
                                ) { Text("Filter") }
                                Text(
                                    "SHA-256 indexed for eligible files up to 5 MiB",
                                    color = ERIA_MUTED,
                                    style = MaterialTheme.typography.caption,
                                    modifier = Modifier.weight(1f).padding(top = 12.dp)
                                )
                            }
                            if (provenanceError.isNotBlank()) StatusCard(provenanceError, false)
                            LazyColumn(
                                modifier = Modifier.weight(1f),
                                verticalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                items(provenance, key = { it.path }) { record ->
                                    InfoCard(
                                        record.path,
                                        "Source SHA-256: " +
                                            record.sha256.ifBlank { "not computed (size limit or unavailable)" } +
                                            "\nSize: " + record.size + " bytes" +
                                            "\nType: " + record.extension +
                                            "\nAuthority: NON_AUTHORITATIVE"
                                    )
                                }
                                item {
                                    InfoCard(
                                        "Derived records",
                                        "This dashboard does not generate derived records. Downstream transforms must retain the original source ID and source hash and store the derived hash separately."
                                    )
                                }
                            }
                        }
                    }

                    DashboardTab.AUDIT -> {
                        Column(modifier = Modifier.weight(1f)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    "Append-only local event history",
                                    color = ERIA_TEXT,
                                    fontWeight = FontWeight.SemiBold
                                )
                                TextButton(
                                    onClick = { coroutineScope.launch { loadAudit() } },
                                    enabled = connected
                                ) { Text("Refresh", color = ERIA_MINT) }
                            }
                            if (auditError.isNotBlank()) StatusCard(auditError, false)
                            if (auditEvents.isEmpty() && auditError.isBlank()) {
                                InfoCard("Audit history", "No audit events are available yet.")
                            }
                            LazyColumn(
                                modifier = Modifier.weight(1f),
                                verticalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                items(auditEvents, key = { it.id }) { event ->
                                    InfoCard(
                                        "#" + event.id + " · " + event.event,
                                        event.status + " · " + event.createdAt + "\n" + event.detail
                                    )
                                }
                            }
                        }
                    }

                    DashboardTab.PONS -> {
                        LazyColumn(
                            modifier = Modifier.weight(1f),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            item { InfoCard("PONS ethics & authorization", "FAIL-CLOSED") }
                            item { InfoCard("Decision policy", ponsPolicy) }
                            item {
                                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                    MetricCard(
                                        "Execution",
                                        if (executionEnabled) "Enabled" else "Disabled",
                                        Modifier.weight(1f)
                                    )
                                    MetricCard(
                                        "Git writes",
                                        if (gitMutationEnabled) "Enabled" else "Disabled",
                                        Modifier.weight(1f)
                                    )
                                    MetricCard(
                                        "Transmission",
                                        if (transmissionEnabled) "Enabled" else "Disabled",
                                        Modifier.weight(1f)
                                    )
                                }
                            }
                            item {
                                InfoCard(
                                    "Human oversight",
                                    "No implicit consent. Requests begin on HOLD. This dashboard cannot approve grants or execute protected actions."
                                )
                            }
                            item {
                                InfoCard(
                                    "Decision states",
                                    "HOLD: missing, unverified, or out-of-scope approval. " +
                                        "PROPOSAL_ONLY: eligible for human review, not execution. " +
                                        "REVIEW_READY: evidence package is ready for review, not a grant. " +
                                        "New requests submitted here always begin at HOLD."
                                )
                            }
                            item { InfoCard("Authorization request", "Submit an exact-scope proposal for human review. This does not grant permission.") }
                            item {
                                OutlinedTextField(
                                    value = capability,
                                    onValueChange = { capability = it },
                                    modifier = Modifier.fillMaxWidth(),
                                    label = { Text("Capability") },
                                    singleLine = true
                                )
                            }
                            item {
                                OutlinedTextField(
                                    value = requestedScope,
                                    onValueChange = { requestedScope = it },
                                    modifier = Modifier.fillMaxWidth(),
                                    label = { Text("Exact scope") },
                                    singleLine = true
                                )
                            }
                            item {
                                OutlinedTextField(
                                    value = requestReason,
                                    onValueChange = { requestReason = it },
                                    modifier = Modifier.fillMaxWidth(),
                                    label = { Text("Reason") }
                                )
                            }
                            item {
                                Button(
                                    onClick = { coroutineScope.launch { submitAuthorizationRequest() } },
                                    enabled = connected && !submittingRequest &&
                                        capability.isNotBlank() && requestedScope.isNotBlank() &&
                                        requestReason.isNotBlank()
                                ) {
                                    Text(if (submittingRequest) "Submitting…" else "Submit review request · HOLD")
                                }
                            }
                            item {
                                Text(
                                    if (approvalSupported) {
                                        "An external approval authority is configured; this screen still only submits requests."
                                    } else {
                                        "Approval authority is not configured. Requests remain HOLD."
                                    },
                                    color = ERIA_AMBER,
                                    style = MaterialTheme.typography.caption
                                )
                            }
                            if (ponsError.isNotBlank()) item { StatusCard(ponsError, false) }
                            item { Text("Authorization requests", color = ERIA_TEXT, fontWeight = FontWeight.SemiBold) }
                            if (authorizationRequests.isEmpty()) {
                                item { InfoCard("Request queue", "No authorization requests have been recorded.") }
                            }
                            items(authorizationRequests, key = { it.id }) { request ->
                                InfoCard(
                                    request.capability + " · " + request.status,
                                    "Scope: " + request.scope +
                                        "\nReason: " + request.reason +
                                        "\nID: " + request.id +
                                        "\n" + request.createdAt
                                )
                            }
                        }
                    }
                }

                Spacer(Modifier.height(6.dp))
                Text(
                    "Local Termux API · 127.0.0.1:8765 · source-preserving · no automatic repository mutation",
                    color = Color(0xFF71829D),
                    style = MaterialTheme.typography.caption
                )
            }
        }
    }
}

@Composable
private fun MetricCard(label: String, value: String, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier,
        backgroundColor = ERIA_PANEL,
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(Modifier.padding(10.dp)) {
            Text(value, color = ERIA_TEXT, fontWeight = FontWeight.Bold)
            Text(label, color = ERIA_MUTED, style = MaterialTheme.typography.caption)
        }
    }
}

@Composable
private fun InfoCard(title: String, body: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        backgroundColor = ERIA_PANEL,
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(Modifier.padding(12.dp)) {
            Text(title, color = ERIA_MINT, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(4.dp))
            Text(body, color = ERIA_TEXT, style = MaterialTheme.typography.body2)
        }
    }
}

@Composable
private fun StatusCard(message: String, success: Boolean) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        backgroundColor = ERIA_PANEL,
        shape = RoundedCornerShape(10.dp)
    ) {
        Text(
            message,
            modifier = Modifier.padding(10.dp),
            color = if (success) ERIA_MINT else ERIA_AMBER,
            style = MaterialTheme.typography.caption
        )
    }
}

private fun JSONArray?.toRepositoryFiles(): List<RepositoryFile> {
    if (this == null) return emptyList()
    return (0 until length()).mapNotNull { index ->
        val item = optJSONObject(index) ?: return@mapNotNull null
        val path = item.optString("path")
        if (path.isBlank()) return@mapNotNull null
        RepositoryFile(
            path = path,
            size = item.optLong("size_bytes"),
            sha256 = item.optString("source_sha256"),
            extension = item.optString("extension")
        )
    }
}

private fun JSONArray?.toAuditEvents(): List<AuditEvent> {
    if (this == null) return emptyList()
    return (0 until length()).mapNotNull { index ->
        val item = optJSONObject(index) ?: return@mapNotNull null
        AuditEvent(
            id = item.optLong("id"),
            event = item.optString("event", "unknown_event"),
            status = item.optString("status", "UNKNOWN"),
            detail = item.optJSONObject("detail")?.toString() ?: "{}",
            createdAt = item.optString("created_at")
        )
    }
}

private fun JSONArray?.toAuthorizationRequests(): List<AuthorizationRequest> {
    if (this == null) return emptyList()
    return (0 until length()).mapNotNull { index ->
        val item = optJSONObject(index) ?: return@mapNotNull null
        val id = item.optString("request_id")
        if (id.isBlank()) return@mapNotNull null
        AuthorizationRequest(
            id = id,
            capability = item.optString("capability", "unknown"),
            scope = item.optString("scope"),
            reason = item.optString("reason"),
            status = item.optString("status", "HOLD"),
            createdAt = item.optString("created_at")
        )
    }
}

private suspend fun eriaGet(path: String): JSONObject = withContext(Dispatchers.IO) {
    eriaRequest(path, "GET", null)
}

private suspend fun eriaPost(path: String, body: JSONObject): JSONObject = withContext(Dispatchers.IO) {
    eriaRequest(path, "POST", body.toString())
}

private fun eriaRequest(path: String, method: String, body: String?): JSONObject {
    require(path.startsWith("/") && !path.startsWith("//")) { "Invalid local API path." }
    val connection = (URL(ERIA_API + path).openConnection() as HttpURLConnection).apply {
        requestMethod = method
        connectTimeout = 3000
        readTimeout = 7000
        useCaches = false
        setRequestProperty("Accept", "application/json")
        if (body != null) {
            doOutput = true
            setRequestProperty("Content-Type", "application/json; charset=utf-8")
        }
    }

    return try {
        if (body != null) {
            connection.outputStream.use { output ->
                output.write(body.toByteArray(Charsets.UTF_8))
            }
        }
        val code = connection.responseCode
        val stream = if (code in 200..299) connection.inputStream else connection.errorStream
        val responseBody = stream?.bufferedReader(Charsets.UTF_8)?.use { reader ->
            val output = StringBuilder()
            val buffer = CharArray(8192)
            var total = 0
            while (true) {
                val count = reader.read(buffer)
                if (count < 0) break
                total += count
                if (total > 1_048_576) throw IllegalStateException("ERIA response exceeded 1 MiB.")
                output.append(buffer, 0, count)
            }
            output.toString()
        }.orEmpty()

        if (code !in 200..299) {
            throw IllegalStateException("HTTP " + code + ": " + responseBody.take(500))
        }
        if (responseBody.isBlank()) JSONObject() else JSONObject(responseBody)
    } finally {
        connection.disconnect()
    }
}
