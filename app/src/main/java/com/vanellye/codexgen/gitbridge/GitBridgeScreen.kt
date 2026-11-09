package com.vanellye.codexgen.gitbridge

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.Button
import androidx.compose.material.Checkbox
import androidx.compose.material.LinearProgressIndicator
import androidx.compose.material.MaterialTheme
import androidx.compose.material.OutlinedButton
import androidx.compose.material.OutlinedTextField
import androidx.compose.material.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@Composable
fun GitBridgeScreen() {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val bridge = remember { GitFreedomBridge(context) }
    var token by remember { mutableStateOf("") }
    var author by remember { mutableStateOf("CodEXgen Contributor") }
    var email by remember { mutableStateOf("") }
    var base by remember { mutableStateOf("main-11-of-38") }
    var feature by remember { mutableStateOf("olpirt/stride-next") }
    var commitMessage by remember { mutableStateOf("CodEXgen: add reviewed Stride updates") }
    var message by remember { mutableStateOf("Local-first Git bridge. Save a fine-grained token to begin.") }
    var changes by remember { mutableStateOf<List<GitFileChange>>(emptyList()) }
    var selected by remember { mutableStateOf<Set<String>>(emptySet()) }
    var busy by remember { mutableStateOf(false) }

    val picker = rememberLauncherForActivityResult(
        ActivityResultContracts.OpenDocumentTree()
    ) { uri ->
        if (uri != null) {
            scope.launch {
                busy = true
                message = runCatching {
                    withContext(Dispatchers.IO) { "Imported ${bridge.importWorkspaceTree(uri)} files into the app-private clone." }
                }.getOrElse { it.message ?: "Import failed." }
                busy = false
            }
        }
    }

    val config = GitBridgeConfig(
        baseBranch = base,
        featureBranch = feature,
        authorName = author,
        authorEmail = email
    )

    fun runTask(task: suspend () -> String) {
        scope.launch {
            busy = true
            message = runCatching { withContext(Dispatchers.IO) { task() } }
                .getOrElse { it.message ?: "Operation failed." }
            busy = false
        }
    }

    fun resultText(result: GitBridgeResult): String = when (result) {
        is GitBridgeResult.Success -> result.status.message
        is GitBridgeResult.Failure -> "${result.message}\n${result.recovery}"
    }

    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text("GIT FREEDOM BRIDGE", style = MaterialTheme.typography.h6)
        Text("Only the configured feature branch is committed or pushed. Pull is fast-forward-only.")
        OutlinedTextField(
            value = token,
            onValueChange = { token = it },
            label = { Text("Fine-grained GitHub token") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth()
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = {
                runCatching { bridge.saveUserToken(token) }
                    .onSuccess { token = ""; message = "Token encrypted with Android Keystore." }
                    .onFailure { message = it.message ?: "Token save failed." }
            }) { Text("Save token") }
            OutlinedButton(onClick = {
                bridge.clearUserToken()
                token = ""
                message = "Saved token cleared."
            }) { Text("Clear token") }
        }
        OutlinedTextField(author, { author = it }, label = { Text("Commit author") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(email, { email = it }, label = { Text("Commit email") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(base, { base = it }, label = { Text("Base branch") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(feature, { feature = it }, label = { Text("Feature branch") }, modifier = Modifier.fillMaxWidth())

        Button(
            enabled = !busy && email.contains("@"),
            onClick = {
                runTask {
                    resultText(bridge.prepare(config))
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) { Text("Prepare / open feature branch") }

        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(
                enabled = !busy,
                onClick = { runTask { resultText(bridge.fetchFeatureBranch(config)) } },
                modifier = Modifier.weight(1f)
            ) { Text("Fetch") }
            OutlinedButton(
                enabled = !busy,
                onClick = { runTask { resultText(bridge.pullFeatureBranch(config)) } },
                modifier = Modifier.weight(1f)
            ) { Text("Pull (FF only)") }
        }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(
                enabled = !busy,
                onClick = {
                    runTask {
                        changes = withContext(Dispatchers.IO) { bridge.reviewChanges(config) }
                        selected = changes.map { it.path }.toSet()
                        "Loaded ${changes.size} changed path(s). Review selections below."
                    }
                },
                modifier = Modifier.weight(1f)
            ) { Text("Refresh review") }
            OutlinedButton(
                enabled = !busy,
                onClick = { picker.launch(null) },
                modifier = Modifier.weight(1f)
            ) { Text("Import workspace") }
        }

        Text("Changed files (${changes.size})", style = MaterialTheme.typography.subtitle1)
        changes.forEach { change ->
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Start) {
                Checkbox(
                    checked = change.path in selected,
                    onCheckedChange = { checked ->
                        selected = if (checked) selected + change.path else selected - change.path
                    }
                )
                Column(Modifier.padding(top = 10.dp)) {
                    Text(change.path, style = MaterialTheme.typography.body2)
                    Text(if (change.deleted) "${change.kind} • delete" else change.kind,
                        style = MaterialTheme.typography.caption)
                }
            }
        }
        if (changes.isEmpty()) Text("No review entries loaded yet.")

        OutlinedTextField(
            value = commitMessage,
            onValueChange = { commitMessage = it },
            label = { Text("Commit message") },
            modifier = Modifier.fillMaxWidth()
        )
        Button(
            enabled = !busy && selected.isNotEmpty() && commitMessage.isNotBlank() && email.contains("@"),
            onClick = {
                val paths = selected.toList()
                runTask {
                    val result = bridge.commitSelectedAndPush(config, paths, commitMessage)
                    if (result is GitBridgeResult.Success) {
                        changes = bridge.reviewChanges(config)
                        selected = emptySet()
                    }
                    resultText(result)
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) { Text("Commit selected + normal push") }
        OutlinedButton(
            enabled = !busy,
            onClick = { runTask { resultText(bridge.pushFeatureBranch(config)) } },
            modifier = Modifier.fillMaxWidth()
        ) { Text("Push feature branch (no force)") }

        if (busy) LinearProgressIndicator(Modifier.fillMaxWidth())
        Text(message, style = MaterialTheme.typography.caption)
        Text("Local clone: ${bridge.localRepositoryPath()}", style = MaterialTheme.typography.caption)
        Text("Force push is intentionally not automatic. If a lease-protected rewrite is ever needed, review remote history first.")
    }
}
