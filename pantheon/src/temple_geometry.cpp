#include "pantheon/temple_geometry.hpp"

namespace pantheon {
namespace temple {

bool TempleModel::hasShape(const std::string& id) const {
    for (std::vector<Shape>::const_iterator it = shapes_.begin();
         it != shapes_.end(); ++it) if (it->id == id) return true;
    return false;
}

bool TempleModel::hasString(const std::string& id) const {
    for (std::vector<BassString>::const_iterator it = strings_.begin();
         it != strings_.end(); ++it) if (it->id == id) return true;
    return false;
}

bool TempleModel::addString(const BassString& value) {
    if (value.id.empty() || value.from.empty() || value.to.empty() ||
        value.from == value.to || value.tension < 0.0) return false;
    for (std::vector<BassString>::const_iterator it = strings_.begin();
         it != strings_.end(); ++it) if (it->id == value.id) return false;
    strings_.push_back(value);
    return true;
}

bool TempleModel::addSway(const Sway& value) {
    if (value.id.empty() || value.amplitude < 0.0 ||
        value.periodSeconds <= 0.0 || !hasString(value.stringId)) return false;
    for (std::vector<Sway>::const_iterator it = sways_.begin();
         it != sways_.end(); ++it) if (it->id == value.id) return false;
    sways_.push_back(value);
    return true;
}

bool TempleModel::addShape(const Shape& value) {
    if (value.id.empty() || value.scale <= 0.0 || hasShape(value.id)) return false;
    shapes_.push_back(value);
    return true;
}

bool TempleModel::addBridge(const Bridge& value) {
    if (value.id.empty() || value.relation.empty() ||
        value.fromShape == value.toShape ||
        !hasShape(value.fromShape) || !hasShape(value.toShape)) return false;
    for (std::vector<Bridge>::const_iterator it = bridges_.begin();
         it != bridges_.end(); ++it) if (it->id == value.id) return false;
    bridges_.push_back(value);
    return true;
}

bool TempleModel::addDirective(const SphereDirective& value) {
    if (value.id.empty() || value.purpose.empty() ||
        !value.protectsHumanDignity || !value.requiresHumanConsent) return false;
    for (std::vector<SphereDirective>::const_iterator it = directives_.begin();
         it != directives_.end(); ++it) if (it->id == value.id) return false;
    directives_.push_back(value);
    return true;
}

TempleValidation TempleModel::validate() const {
    TempleValidation result;
    if (shapes_.empty()) result.errors.push_back("temple_requires_at_least_one_shape");
    if (directives_.empty()) result.errors.push_back("temple_requires_sphere_directive");

    for (std::vector<Sway>::const_iterator it = sways_.begin();
         it != sways_.end(); ++it) {
        if (!hasString(it->stringId))
            result.errors.push_back("sway_has_no_bass_string:" + it->id);
    }
    for (std::vector<Bridge>::const_iterator it = bridges_.begin();
         it != bridges_.end(); ++it) {
        if (!hasShape(it->fromShape) || !hasShape(it->toShape))
            result.errors.push_back("bridge_endpoint_missing:" + it->id);
    }
    result.valid = result.errors.empty();
    return result;
}

} // namespace temple
} // namespace pantheon
