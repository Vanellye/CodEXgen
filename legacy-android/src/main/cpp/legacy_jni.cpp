#include <jni.h>
#include <string>

extern "C" JNIEXPORT jstring JNICALL
Java_com_vanellye_codexgen_legacy_LegacyMainActivity_nativeStatus(
    JNIEnv* env, jobject) {
    const std::string report =
        "C++11 JNI bridge active\n"
        "Profile: API 11 legacy shell\n"
        "Storage: app-private SQLite\n"
        "Git transport: disabled in legacy profile pending API-11-safe credential design\n";
    return env->NewStringUTF(report.c_str());
}
