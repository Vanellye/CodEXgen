#pragma once
#include <optional>
#include <string>

namespace codexgen::olpirt {
struct IConfiguratio {
    virtual ~IConfiguratio() = default;
    virtual std::optional<std::string> read(const std::string& key) const = 0;
};
struct ISecretum {
    virtual ~ISecretum() = default;
    virtual std::optional<std::string> readSecret(const std::string& alias) const = 0;
};
struct IVia {
    virtual ~IVia() = default;
    virtual bool publish(const std::string& channel, const std::string& payload) = 0;
};
struct IDatorum {
    virtual ~IDatorum() = default;
    virtual bool put(const std::string& key, const std::string& value) = 0;
    virtual std::optional<std::string> get(const std::string& key) const = 0;
};
struct IModulus {
    virtual ~IModulus() = default;
    virtual std::string execute(const std::string& input) = 0;
};
} // namespace codexgen::olpirt
