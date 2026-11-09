package com.vanellye.codexgen.nativebridge

/** JNI access to the native Pons/Olpirt dependency contract auditor. */
object OlpirtNativeBridge {
    private val loaded = runCatching { System.loadLibrary("codexgen_pons") }.isSuccess
    external fun nativeStatus(): String
    fun status(): String = if (loaded) {
        runCatching { nativeStatus() }
            .getOrElse { "Native bridge loaded, but status failed: ${it.message}" }
    } else {
        "Native bridge is not loaded. Build with Android NDK and CMake enabled."
    }
}
