#ifndef PANTHEON_ECTICT_HPP
#define PANTHEON_ECTICT_HPP
#include <string>
#include <vector>
namespace pantheon {
namespace ectict {
// ECTICT is intentionally a proper name, not an acronym expansion.
enum class EvidenceState { VERIFIED, INFERRED, UNKNOWN };
struct Viewpoint {
    std::string id;
    std::string source;
    std::string statement;
    EvidenceState evidence;
};
struct Tension {
    std::string id;
    std::string leftViewpointId;
    std::string rightViewpointId;
    std::string question;
};
struct GrowthProposal {
    std::string id;
    std::string tensionId;
    std::string learning;
    std::string nextStep;
    bool requiresHumanReview;
    GrowthProposal() : requiresHumanReview(true) {}
};
struct Review {
    bool valid;
    std::vector<std::string> findings;
    Review() : valid(true) {}
};
class EctictThinking {
public:
    bool addViewpoint(const Viewpoint& viewpoint);
    bool addTension(const Tension& tension);
    bool addProposal(const GrowthProposal& proposal);
    Review validate() const;
    const std::vector<Viewpoint>& viewpoints() const;
    const std::vector<Tension>& tensions() const;
    const std::vector<GrowthProposal>& proposals() const;
private:
    std::vector<Viewpoint> viewpoints_;
    std::vector<Tension> tensions_;
    std::vector<GrowthProposal> proposals_;
};
} // namespace ectict
} // namespace pantheon
#endif
