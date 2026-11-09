package com.vanellye.codexgen.gitbridge

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.platform.LocalContext
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
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
    var commitMessage by remember { mutableStateOf("CodEXgen: selected Olpirt changes") }
    var prTitle by remember { mutableStateOf("CodEXgen: integrate reviewed feature work") }
    var prBody by remember { mutableStateOf("Please review the selected CodEXgen changes. This PR targets the configured base branch and will not merge automatically.") }
    var promptInput by remember { mutableStateOf("") }
    var promptReport by remember { mutableStateOf<PromptOptimizationReport?>(null) }
    var message by remember { mutableStateOf("Local-first Git bridge. No action has run yet.") }
    var changes by remember { mutableStateOf<List<GitFileChange>>(emptyList()) }
    var selected by remember { mutableStateOf<Set<String>>(emptySet()) }
    var busy by remember { mutableStateOf(false) }
    val workspacePicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocumentTree()
    ) { uri ->
        if (uri != null) {
            runTask {
                val count = bridge.importWorkspaceTree(uri)
                "Imported $count file(s) into the app-private feature-branch clone. Review before committing."
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

    Column(
        Modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text("GIT FREEDOM BRIDGE", style = MaterialTheme.typography.h6)
        Text("Review changes • Select files • Commit only selected paths",
            style = MaterialTheme.typography.caption)

        OutlinedTextField(
            token, { token = it },
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
                message = "Stored token cleared."
            }) { Text("Clear") }
        }

        OutlinedTextField(author, { author = it },
            label = { Text("Commit author") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(email, { email = it },
            label = { Text("Commit email") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(base, { base = it },
            label = { Text("Protected base branch") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(feature, { feature = it },
            label = { Text("Feature branch") }, modifier = Modifier.fillMaxWidth())

        Button(
            enabled = !busy && email.contains("@"),
            onClick = {
                runTask {
                    when (val result = bridge.prepare(config)) {
                        is GitBridgeResult.Success -> result.status.message
                        is GitBridgeResult.Failure -> "${result.message}\n${result.recovery}"
                    }
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) { Text("Prepare feature branch") }

        OutlinedButton(
            enabled = !busy,
            onClick = { workspacePicker.launch(null) },
            modifier = Modifier.fillMaxWidth()
        ) { Text("Import existing CodEXgen workspace folder") }

        OutlinedButton(
            enabled = !busy,
            onClick = {
                runTask {
                    changes = bridge.reviewChanges(config)
                    selected = changes.map { it.path }.toSet()
                    "Review loaded: ${changes.size} changed path(s). Uncheck anything you do not want."
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) { Text("Refresh changed-file review") }

        Row(horizontalArrangement = Arrangement.SpaceBetween,
            modifier = Modifier.fillMaxWidth()) {
            Text("Changed files (${changes.size})", style = MaterialTheme.typography.subtitle1)
            TextButton(onClick = { selected = changes.map { it.path }.toSet() }) {
                Text("Select all")
            }
        }

        LazyColumn(
            modifier = Modifier.weight(1f, fill = true),
            verticalArrangement = Arrangement.spacedBy(2.dp)
        ) {
            items(changes, key = { it.path }) { change ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Start) {
                    Checkbox(
                        checked = change.path in selected,
                        onCheckedChange = { checked ->
                            selected = if (checked) selected + change.path
                                else selected - change.path
                        }
                    )
                    Column(Modifier.padding(top = 8.dp)) {
                        Text(change.path, style = MaterialTheme.typography.body2)
                        Text(
                            if (change.deleted) "${change.kind} • delete" else change.kind,
                            style = MaterialTheme.typography.caption
                        )
                    }
                }
                Divider()
            }
            if (changes.isEmpty()) {
                item { Text("No changes loaded. Prepare the branch, then refresh review.") }
            }
        }

        OutlinedTextField(commitMessage, { commitMessage = it },
            label = { Text("Commit message") }, modifier = Modifier.fillMaxWidth())
        Button(
            enabled = !busy && selected.isNotEmpty() && commitMessage.isNotBlank()
                && email.contains("@"),
            onClick = {
                val paths = selected.toList()
                runTask {
                    when (val result = bridge.commitSelectedAndPush(
                        config, paths, commitMessage
                    )) {
                        is GitBridgeResult.Success -> {
                            changes = bridge.reviewChanges(config)
                            selected = emptySet()
                            result.status.message
                        }
                        is GitBridgeResult.Failure -> "${result.message}\nRecovery: ${result.recovery}"
                    }
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) { Text("Commit selected + push feature branch") }


        OutlinedTextField(prTitle, { prTitle = it },
            label = { Text("Pull request title") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(prBody, { prBody = it },
            label = { Text("Pull request description") }, modifier = Modifier.fillMaxWidth())
        OutlinedButton(
            enabled = !busy && prTitle.isNotBlank(),
            onClick = {
                runTask {
                    when (val result = bridge.createPullRequest(config, prTitle, prBody)) {
                        is GitBridgeResult.Success -> result.status.message
                        is GitBridgeResult.Failure -> "${result.message}\n${result.recovery}"
                    }
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) { Text("Open pull request (no auto-merge)") }

        OutlinedButton(
            enabled = !busy,
            onClick = {
                runTask {
                    when (val result = bridge.forceWithLeaseFeatureBranch(config)) {
                        is GitBridgeResult.Success -> result.status.message
                        is GitBridgeResult.Failure -> "${result.message}\n${result.recovery}"
                    }
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) { Text("Force push feature branch with lease") }
        Text("Uses the fetched remote commit as an expected-old lease. GitHub rejects the update if the branch changed after fetch. Feature branch only; never targets the base branch.",
            style = MaterialTheme.typography.caption)

        Divider()
        Text("PROMPT OPTIMIZATION REPORT", style = MaterialTheme.typography.subtitle1)
        Text("Analyze a prompt and produce an explainable improvement report. Nothing self-modifies automatically.",
            style = MaterialTheme.typography.caption)
        OutlinedTextField(
            promptInput, { promptInput = it },
            label = { Text("Prompt to review") },
            modifier = Modifier.fillMaxWidth(),
            minLines = 3
        )
        OutlinedButton(
            enabled = !busy && promptInput.isNotBlank(),
            onClick = {
                runCatching { PromptReportEngine.analyze(promptInput) }
                    .onSuccess { promptReport = it; message = "Prompt report generated." }
                    .onFailure { message = it.message ?: "Prompt analysis failed." }
            },
            modifier = Modifier.fillMaxWidth()
        ) { Text("Generate prompt report") }
        promptReport?.let { report ->
            Text("Prompt quality score: ${report.overallScore}/100",
                style = MaterialTheme.typography.subtitle2)
            report.dimensions.forEach { dimension ->
                Text("${dimension.name}: ${dimension.score}/100 — ${dimension.finding}",
                    style = MaterialTheme.typography.caption)
                Text("Improve: ${dimension.recommendation}",
                    style = MaterialTheme.typography.caption)
            }
            Text("Suggested prompt structure:", style = MaterialTheme.typography.subtitle2)
            Text(report.optimizedDraft, style = MaterialTheme.typography.body2)
            Text(report.caveat, style = MaterialTheme.typography.caption)
        }

        if (busy) LinearProgressIndicator(Modifier.fillMaxWidth())
        Text(message, style = MaterialTheme.typography.caption)
        Text("Local repo: ${bridge.localRepositoryPath()}",
            style = MaterialTheme.typography.caption)
        Text("Imported files are copied into the app-private clone; source folder is not modified.",
            style = MaterialTheme.typography.caption)
    }
}
