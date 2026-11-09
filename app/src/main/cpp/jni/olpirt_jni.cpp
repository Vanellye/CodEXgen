#include <jni.h>
#include "olpirt/freedom_bridge.hpp"
#include "pantheon/runtime.hpp"
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
    const std::string summary = freedom.exportSummary(report) +
        "boundary=VelumAetheris\n" +
        std::string("container=") + pantheon::Runtime::version() + " (C++11)\n" +
        "mode=declared-contract-audit; runtime provider bindings not yet verified\n";
    return env->NewStringUTF(summary.c_str());
}
