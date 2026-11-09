package com.vanellye.codexgen

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.Button
import androidx.compose.material.CircularProgressIndicator
import androidx.compose.material.MaterialTheme
import androidx.compose.material.OutlinedTextField
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

/** Stateful wrapper: owns ViewModel + local text field state. */
@Composable
fun CodeGenRoute(
    modifier: Modifier = Modifier,
    viewModel: CodeGenViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var moduleName by remember { mutableStateOf("") }

    CodeGenScreen(
        uiState = uiState,
        moduleName = moduleName,
        onModuleNameChange = { moduleName = it },
        onGenerateClick = { name ->
            viewModel.generateCode(name, "BaseModel", listOf("id", "timestamp"))
        },
        modifier = modifier
    )
}

/** Stateless UI: draws from inputs and hoists events. */
@Composable
fun CodeGenScreen(
    uiState: CodeGenUiState,
    moduleName: String,
    onModuleNameChange: (String) -> Unit,
    onGenerateClick: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.fillMaxSize().padding(16.dp)) {
        OutlinedTextField(
            value = moduleName,
            onValueChange = onModuleNameChange,
            label = { Text("Module Name") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(12.dp))

        Button(
            onClick = { onGenerateClick(moduleName) },
            enabled = moduleName.isNotBlank() && uiState !is CodeGenUiState.Loading,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Generate Code Index")
        }

        Spacer(modifier = Modifier.height(24.dp))

        when (uiState) {
            is CodeGenUiState.Idle -> {
                Text("Enter a module name and tap generate.")
            }
            is CodeGenUiState.Loading -> {
                CircularProgressIndicator()
            }
            is CodeGenUiState.Success -> {
                Text(
                    text = uiState.code,
                    style = MaterialTheme.typography.body2,
                    modifier = Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                )
            }
            is CodeGenUiState.Error -> {
                Text(
                    text = uiState.message,
                    color = MaterialTheme.colors.error
                )
            }
        }
    }
}
