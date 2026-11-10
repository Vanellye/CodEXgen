package com.vanellye.eria

/**
 * UI state for the code-generation screen.
 * Must be a sealed type so Compose `when` branches are exhaustive.
 */
sealed interface CodeGenUiState {
    data object Idle : CodeGenUiState
    data object Loading : CodeGenUiState
    data class Success(val code: String) : CodeGenUiState
    data class Error(val message: String) : CodeGenUiState
}
