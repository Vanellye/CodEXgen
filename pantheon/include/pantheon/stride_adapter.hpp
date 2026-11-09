#ifndef PANTHEON_STRIDE_ADAPTER_HPP
#define PANTHEON_STRIDE_ADAPTER_HPP

#include "pantheon/runtime.hpp"
#include <string>
#include <utility>
#include <vector>

namespace pantheon {

// Compatibility seam for Stride's existing feature/channel-oriented APIs.
// The adapter copies numeric inputs; it does not emit signals or access devices.
class StrideFrameworkAdapter {
public:
    static Input fromFeaturePairs(
        const std::vector<std::pair<std::string, double> >& features) {
        Input input;
        for (std::vector<std::pair<std::string, double> >::const_iterator it =
                 features.begin(); it != features.end(); ++it) {
            input.values[it->first] = it->second;
        }
        return input;
    }
};

} // namespace pantheon

#endif
