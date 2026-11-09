package com.vanellye.codexgen.nativebridge;

/** JNI dependency-audit bridge. */
public final class OlpirtNativeBridge {
    private static boolean loaded;
    static {
        try { System.loadLibrary("codexgen_pons"); loaded = true; }
        catch (Throwable error) { loaded = false; }
    }
    public native String nativeStatus();
    public boolean isLoaded() { return loaded; }
    public String status() {
        if (!loaded) return "Native library unavailable for this device ABI.";
        try { return nativeStatus(); }
        catch (Throwable error) { return "Native bridge error: " + error.getClass().getName(); }
    }
}
