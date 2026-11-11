#ifndef PANTHEON_TEMPLE_GEOMETRY_HPP
#define PANTHEON_TEMPLE_GEOMETRY_HPP

#include <string>
#include <vector>

namespace pantheon {
namespace temple {

// Geometry is a declarative model: it describes relationships and motion
// parameters. It does not drive actuators or infer anything about a person's body.
struct Point3 {
    double x;
    double y;
    double z;
    Point3() : x(0.0), y(0.0), z(0.0) {}
    Point3(double px, double py, double pz) : x(px), y(py), z(pz) {}
};

struct BassString {
    std::string id;
    std::string from;
    std::string to;
    double tension;
    BassString() : id(), from(), to(), tension(0.0) {}
};

struct Sway {
    std::string id;
    std::string stringId;
    double amplitude;
    double periodSeconds;
    Sway() : id(), stringId(), amplitude(0.0), periodSeconds(0.0) {}
};

enum class ShapeKind { POINT, LINE, TRIANGLE, POLYGON, SPHERE };

struct Shape {
    std::string id;
    ShapeKind kind;
    Point3 origin;
    double scale;
    Shape() : id(), kind(ShapeKind::POINT), origin(), scale(1.0) {}
};

struct Bridge {
    std::string id;
    std::string fromShape;
    std::string toShape;
    std::string relation;
};

struct SphereDirective {
    std::string id;
    std::string purpose;
    std::vector<std::string> requiredPrinciples;
    bool protectsHumanDignity;
    bool requiresHumanConsent;
    SphereDirective()
        : id(), purpose(), requiredPrinciples(),
          protectsHumanDignity(true), requiresHumanConsent(true) {}
};

struct TempleValidation {
    bool valid;
    std::vector<std::string> errors;
    TempleValidation() : valid(true), errors() {}
};

class TempleModel {
public:
    bool addString(const BassString& value);
    bool addSway(const Sway& value);
    bool addShape(const Shape& value);
    bool addBridge(const Bridge& value);
    bool addDirective(const SphereDirective& value);
    TempleValidation validate() const;

    const std::vector<BassString>& strings() const { return strings_; }
    const std::vector<Sway>& sways() const { return sways_; }
    const std::vector<Shape>& shapes() const { return shapes_; }
    const std::vector<Bridge>& bridges() const { return bridges_; }
    const std::vector<SphereDirective>& directives() const { return directives_; }

private:
    bool hasShape(const std::string& id) const;
    bool hasString(const std::string& id) const;
    std::vector<BassString> strings_;
    std::vector<Sway> sways_;
    std::vector<Shape> shapes_;
    std::vector<Bridge> bridges_;
    std::vector<SphereDirective> directives_;
};

} // namespace temple
} // namespace pantheon

#endif
