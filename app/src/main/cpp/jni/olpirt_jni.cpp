#include <jni.h>
#include "olpirt/freedom_bridge.hpp"
#include <set>
#include <string>
#include <vector>

extern "C" JNIEXPORT jstring JNICALL
Java_com_vanellye_codexgen_nativebridge_OlpirtNativeBridge_nativeStatus(
    JNIEnv* env, jobject /* thiz */) {
    const std::vector<codexgen::olpirt::ModuleContract> modules = {
        {"GitFreedomBridge", {"IGitTransport", "ISecretum"}},
        {"DataResonance", {"IDatorum", "IConfiguratio"}},
        {"OlpirtCore", {"IModulus"}}
    };
    const std::set<std::string> hostContracts = {
        "IGitTransport", "ISecretum", "IDatorum", "IConfiguratio", "IModulus"
    };
    const codexgen::olpirt::OlpirtLightBridge light;
    const auto report = light.illuminate(modules, hostContracts);
    const codexgen::olpirt::FreedomBridge freedom;
    const auto summary = freedom.exportSummary(report) +
        "boundary=VelumAetheris\n"
        "container=Pons C++17 (header-only)\n"
        "mode=contract-audit; host providers remain replaceable\n";
    return env->NewStringUTF(summary.c_str());
}
