package com.vanellye.codexgen.gitbridge

data class GitBridgeConfig(
    val repositoryUrl: String = "https://github.com/Vanellye/CodEXgen.git",
    val baseBranch: String = "main-11-of-38",
    val featureBranch: String = "olpirt/stride-next",
    val authorName: String,
    val authorEmail: String
)

data class GitBridgeStatus(
    val message: String,
    val localBranch: String? = null,
    val pendingChanges: Int = 0,
    val remotePushComplete: Boolean = false
)

data class GitFileChange(
    val path: String,
    val kind: String,
    val deleted: Boolean
)

sealed interface GitBridgeResult {
    data class Success(val status: GitBridgeStatus) : GitBridgeResult
    data class Failure(val message: String, val recovery: String) : GitBridgeResult
}
