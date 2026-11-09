#pragma once
#include <functional>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <typeindex>
#include <unordered_map>
#include <utility>
#include <vector>

namespace codexgen::pons {
enum class Lifetime { Transient, Singleton };

/** Header-only C++17 dependency container; no global state or third-party runtime. */
class Pons final {
public:
    template <typename Interface>
    using Factory = std::function<std::shared_ptr<Interface>(Pons&)>;

    template <typename Interface>
    void bind(Factory<Interface> factory, Lifetime lifetime = Lifetime::Transient) {
        if (!factory) throw std::invalid_argument("Pons factory cannot be empty");
        std::lock_guard<std::recursive_mutex> guard(mutex_);
        bindings_[std::type_index(typeid(Interface))] = Binding{
            [factory = std::move(factory)](Pons& c) -> std::shared_ptr<void> {
                auto value = factory(c);
                if (!value) throw std::runtime_error("Pons factory returned null");
                return std::static_pointer_cast<void>(value);
            }, lifetime, nullptr
        };
    }

    template <typename Interface>
    std::shared_ptr<Interface> resolve() {
        const auto key = std::type_index(typeid(Interface));
        std::lock_guard<std::recursive_mutex> guard(mutex_);
        auto found = bindings_.find(key);
        if (found == bindings_.end()) {
            throw std::runtime_error(std::string("Pons provider not registered: ") +
                                     typeid(Interface).name());
        }
        for (const auto& active : resolving_) {
            if (active == key) throw std::runtime_error("Pons dependency cycle detected");
        }
        auto& binding = found->second;
        if (binding.lifetime == Lifetime::Singleton && binding.instance) {
            return std::static_pointer_cast<Interface>(binding.instance);
        }
        resolving_.push_back(key);
        try {
            auto value = binding.factory(*this);
            resolving_.pop_back();
            if (binding.lifetime == Lifetime::Singleton) binding.instance = value;
            return std::static_pointer_cast<Interface>(value);
        } catch (...) {
            resolving_.pop_back();
            throw;
        }
    }

    template <typename Interface>
    bool contains() const {
        std::lock_guard<std::recursive_mutex> guard(mutex_);
        return bindings_.count(std::type_index(typeid(Interface))) != 0;
    }

    void clear() {
        std::lock_guard<std::recursive_mutex> guard(mutex_);
        bindings_.clear();
        resolving_.clear();
    }

private:
    struct Binding {
        std::function<std::shared_ptr<void>(Pons&)> factory;
        Lifetime lifetime;
        std::shared_ptr<void> instance;
    };
    mutable std::recursive_mutex mutex_;
    std::unordered_map<std::type_index, Binding> bindings_;
    std::vector<std::type_index> resolving_;
};
} // namespace codexgen::pons
