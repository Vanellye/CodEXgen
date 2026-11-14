#include "pantheon/temple_geometry.hpp"
#include <cassert>

int main() {
    using namespace pantheon::temple;
    TempleModel model;

    Shape foundation;
    foundation.id = "foundation";
    foundation.kind = ShapeKind::POLYGON;
    assert(model.addShape(foundation));

    Shape crown;
    crown.id = "crown";
    crown.kind = ShapeKind::SPHERE;
    assert(model.addShape(crown));

    BassString bass;
    bass.id = "bass-01";
    bass.from = "foundation";
    bass.to = "crown";
    bass.tension = 0.5;
    assert(model.addString(bass));

    Sway sway;
    sway.id = "sway-01";
    sway.stringId = "bass-01";
    sway.amplitude = 0.25;
    sway.periodSeconds = 4.0;
    assert(model.addSway(sway));

    Bridge bridge;
    bridge.id = "bridge-01";
    bridge.fromShape = "foundation";
    bridge.toShape = "crown";
    bridge.relation = "supports";
    assert(model.addBridge(bridge));

    SphereDirective directive;
    directive.id = "sphere-01";
    directive.purpose = "stewardship-of-the-temple";
    directive.requiredPrinciples.push_back("purpose-over-impulse");
    assert(model.addDirective(directive));

    TempleValidation valid = model.validate();
    assert(valid.valid);
    assert(model.strings().size() == 1);
    assert(model.sways().size() == 1);
    assert(model.bridges().size() == 1);
    assert(model.directives().size() == 1);

    SphereDirective unsafe;
    unsafe.id = "unsafe";
    unsafe.purpose = "unconsented-actuation";
    unsafe.requiresHumanConsent = false;
    assert(!model.addDirective(unsafe));

    Sway orphan;
    orphan.id = "orphan";
    orphan.stringId = "missing";
    orphan.periodSeconds = 1.0;
    assert(!model.addSway(orphan));
    return 0;
}
