package com.vanellye.eria

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Holds generation state as a StateFlow so collectAsState() works in Compose.
 */
class CodeGenViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<CodeGenUiState>(CodeGenUiState.Idle)
    val uiState: StateFlow<CodeGenUiState> = _uiState.asStateFlow()

    fun generateCode(moduleName: String, baseClass: String, attributes: List<String>) {
        val name = moduleName.trim()
        if (name.isEmpty()) {
            _uiState.value = CodeGenUiState.Error("Module name cannot be blank.")
            return
        }

        viewModelScope.launch {
            _uiState.value = CodeGenUiState.Loading
            try {
                val code = withContext(Dispatchers.Default) {
                    buildModuleSource(name, baseClass, attributes)
                }
                _uiState.value = CodeGenUiState.Success(code)
            } catch (t: Throwable) {
                _uiState.value = CodeGenUiState.Error(t.message ?: "Code generation failed.")
            }
        }
    }

    private fun buildModuleSource(
        moduleName: String,
        baseClass: String,
        attributes: List<String>
    ): String {
        val attrInits = attributes.joinToString("\n") { attr ->
            """        self.$attr = data.get("$attr", None)"""
        }
        return """
# Auto-generated module: $moduleName
from typing import Any

class $moduleName($baseClass):
    def __init__(self, data: dict[str, Any]):
        super().__init__()
$attrInits

    def __repr__(self) -> str:
        return f"<$moduleName attributes=$attributes>"
""".trimIndent()
    }
}
