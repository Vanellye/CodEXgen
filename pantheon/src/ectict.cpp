#include "pantheon/ectict.hpp"
namespace pantheon {
namespace ectict {
namespace {
bool nonEmpty(const std::string& value) { return !value.empty(); }
bool hasViewpoint(const std::vector<Viewpoint>& items, const std::string& id) {
    for (std::vector<Viewpoint>::const_iterator it = items.begin(); it != items.end(); ++it)
        if (it->id == id) return true;
    return false;
}
bool hasTension(const std::vector<Tension>& items, const std::string& id) {
    for (std::vector<Tension>::const_iterator it = items.begin(); it != items.end(); ++it)
        if (it->id == id) return true;
    return false;
}
}
bool EctictThinking::addViewpoint(const Viewpoint& v) {
    if (!nonEmpty(v.id) || !nonEmpty(v.source) || !nonEmpty(v.statement) ||
        hasViewpoint(viewpoints_, v.id)) return false;
    viewpoints_.push_back(v);
    return true;
}
bool EctictThinking::addTension(const Tension& t) {
    if (!nonEmpty(t.id) || !nonEmpty(t.question) ||
        !hasViewpoint(viewpoints_, t.leftViewpointId) ||
        !hasViewpoint(viewpoints_, t.rightViewpointId) ||
        t.leftViewpointId == t.rightViewpointId || hasTension(tensions_, t.id)) return false;
    tensions_.push_back(t);
    return true;
}
bool EctictThinking::addProposal(const GrowthProposal& p) {
    if (!nonEmpty(p.id) || !nonEmpty(p.learning) || !nonEmpty(p.nextStep) ||
        !hasTension(tensions_, p.tensionId) || !p.requiresHumanReview) return false;
    for (std::vector<GrowthProposal>::const_iterator it = proposals_.begin();
         it != proposals_.end(); ++it) if (it->id == p.id) return false;
    proposals_.push_back(p);
    return true;
}
Review EctictThinking::validate() const {
    Review r;
    for (std::vector<Tension>::const_iterator it = tensions_.begin(); it != tensions_.end(); ++it) {
        if (it->leftViewpointId == it->rightViewpointId ||
            !hasViewpoint(viewpoints_, it->leftViewpointId) ||
            !hasViewpoint(viewpoints_, it->rightViewpointId)) {
            r.valid = false;
            r.findings.push_back("Tension must preserve two distinct, registered viewpoints.");
        }
    }
    for (std::vector<GrowthProposal>::const_iterator it = proposals_.begin(); it != proposals_.end(); ++it) {
        if (!hasTension(tensions_, it->tensionId) || !it->requiresHumanReview) {
            r.valid = false;
            r.findings.push_back("Growth proposal must reference a tension and require human review.");
        }
    }
    return r;
}
const std::vector<Viewpoint>& EctictThinking::viewpoints() const { return viewpoints_; }
const std::vector<Tension>& EctictThinking::tensions() const { return tensions_; }
const std::vector<GrowthProposal>& EctictThinking::proposals() const { return proposals_; }
}
}
