#ifndef PANTHEON_RUNTIME_HPP
#define PANTHEON_RUNTIME_HPP

#include "pantheon/aleph.hpp"
#include "pantheon/control_gate.hpp"
#include <map>
#include <memory>
#include <string>
#include <vector>

namespace pantheon {

typedef std::map<std::string, double> NumericMap;

struct Input {
    NumericMap values;
};

struct Result {
    bool ok;
    std::string module;
    std::string message;
    NumericMap metrics;

    Result() : ok(false), module(), message(), metrics() {}
};

class Module {
public:
    virtual ~Module() {}
    virtual std::string name() const = 0;
    virtual Result execute(const Input& input) const = 0;

    // Modules that can change external or persistent state must opt in.
    virtual bool requiresControlAuthorization() const { return false; }
};

class Runtime {
public:
    Runtime();

    bool registerModule(const std::shared_ptr<Module>& module);
    bool hasModule(const std::string& name) const;
    Result execute(const std::string& name, const Input& input) const;
    Result executeControlled(const std::string& name, const Input& input,
                             const std::vector<StandardEvidence>& standards,
                             const OwnerApproval& ownerApproval) const;
    std::vector<std::string> moduleNames() const;

    // Register compensating actions before execution. Failed execution
    // automatically engages ALEPH; reversal itself still requires owner approval.
    Aleph& aleph();
    static const char* version();

private:
    std::map<std::string, std::shared_ptr<Module> > modules_;
    mutable Aleph aleph_;
};

} // namespace pantheon

#endif
