#include "pantheon/rise_fall.hpp"
namespace pantheon {
const char* riseFallStateName(RiseFallState state) { switch(state) { case RiseFallState::Rise: return "RISE"; case RiseFallState::Fall: return "FALL"; default: return "WARDEN"; } }
RiseFallDecision RiseFallPolicy::evaluate(const RiseFallInput& input) const {
 RiseFallDecision d;
 if (!input.authorized) { d.reason="explicit_authorization_required"; return d; }
 if (!input.safetyClear) { d.reason="safety_review_required"; return d; }
 if (input.evidence==EvidenceState::Missing || input.evidence==EvidenceState::Conflicting) { d.reason=input.evidence==EvidenceState::Missing ? "evidence_missing" : "evidence_conflicting"; return d; }
 if (input.harmfulIntent || !input.principleAligned || input.evidence==EvidenceState::Adverse) {
  d.state=RiseFallState::Fall; d.symbol="ọ";
  d.reason=input.harmfulIntent ? "harmful_intent_requires_correction" : (!input.principleAligned ? "principle_alignment_failed" : "observed_conditions_adverse"); return d;
 }
 d.state=RiseFallState::Rise; d.symbol="ơ"; d.reason="principles_aligned_and_evidence_supportive"; return d;
}
}
