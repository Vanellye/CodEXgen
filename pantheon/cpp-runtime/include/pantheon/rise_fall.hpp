#ifndef PANTHEON_RISE_FALL_HPP
#define PANTHEON_RISE_FALL_HPP
#include <string>
namespace pantheon {
enum class RiseFallState { Rise, Fall, Warden };
enum class EvidenceState { Supportive, Adverse, Conflicting, Missing };
struct RiseFallInput {
 bool principleAligned; bool harmfulIntent; bool authorized; bool safetyClear; EvidenceState evidence;
 RiseFallInput() : principleAligned(false), harmfulIntent(false), authorized(false), safetyClear(false), evidence(EvidenceState::Missing) {}
};
struct RiseFallDecision {
 RiseFallState state; std::string symbol; std::string reason;
 RiseFallDecision() : state(RiseFallState::Warden), symbol("WARDEN"), reason("not_evaluated") {}
};
class RiseFallPolicy { public: RiseFallDecision evaluate(const RiseFallInput& input) const; };
const char* riseFallStateName(RiseFallState state);
}
#endif
