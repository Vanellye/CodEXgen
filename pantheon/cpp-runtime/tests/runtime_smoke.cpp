#include "pantheon/runtime.hpp"
#include "pantheon/stride_adapter.hpp"
#include <cassert>
#include <memory>
#include <string>

class SumModule : public pantheon::Module {
public:
    std::string name() const { return "sum"; }
    pantheon::Result execute(const pantheon::Input& input) const {
        pantheon::Result result;
        result.ok = true;
        result.module = name();
        result.message = "ok";
        pantheon::NumericMap::const_iterator a = input.values.find("a");
        pantheon::NumericMap::const_iterator b = input.values.find("b");
        result.metrics["sum"] = (a == input.values.end() ? 0.0 : a->second) +
                                (b == input.values.end() ? 0.0 : b->second);
        return result;
    }
};

int main() {
    pantheon::Runtime runtime;
    std::shared_ptr<pantheon::Module> module(new SumModule());
    assert(runtime.registerModule(module));
    assert(!runtime.registerModule(module));
    assert(runtime.hasModule("sum"));

    std::vector<std::pair<std::string, double> > features;
    features.push_back(std::make_pair("a", 2.0));
    features.push_back(std::make_pair("b", 3.0));
    pantheon::Result result = runtime.execute(
        "sum", pantheon::StrideFrameworkAdapter::fromFeaturePairs(features));
    assert(result.ok);
    assert(result.metrics["sum"] == 5.0);

    pantheon::Result missing = runtime.execute("missing", pantheon::Input());
    assert(!missing.ok);
    assert(missing.message == "module_not_registered");
    return 0;
}
