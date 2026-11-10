#pragma once
#include "pons/pons.hpp"
#include "olpirt/contracts.hpp"
#include <utility>

namespace codexgen::olpirt {
/** Boundary around host services; only contracts cross this veil. */
class VelumAetheris final {
public:
    pons::Pons& providers() noexcept { return providers_; }
    const pons::Pons& providers() const noexcept { return providers_; }

    template <typename Interface>
    void provide(typename pons::Pons::template Factory<Interface> factory,
                 pons::Lifetime lifetime = pons::Lifetime::Transient) {
        providers_.bind<Interface>(std::move(factory), lifetime);
    }
private:
    pons::Pons providers_;
};
} // namespace codexgen::olpirt
