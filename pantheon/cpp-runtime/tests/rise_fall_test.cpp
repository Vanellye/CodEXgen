#include "pantheon/rise_fall.hpp"
#include <cassert>
int main() {
 pantheon::RiseFallPolicy p; pantheon::RiseFallInput i; i.authorized=true; i.safetyClear=true; i.principleAligned=true; i.evidence=pantheon::EvidenceState::Supportive;
 pantheon::RiseFallDecision d=p.evaluate(i); assert(d.state==pantheon::RiseFallState::Rise); assert(d.symbol=="ơ");
 i.evidence=pantheon::EvidenceState::Adverse; d=p.evaluate(i); assert(d.state==pantheon::RiseFallState::Fall); assert(d.symbol=="ọ");
 i.evidence=pantheon::EvidenceState::Supportive; i.harmfulIntent=true; d=p.evaluate(i); assert(d.state==pantheon::RiseFallState::Fall);
 i.harmfulIntent=false; i.evidence=pantheon::EvidenceState::Conflicting; d=p.evaluate(i); assert(d.state==pantheon::RiseFallState::Warden);
 i.evidence=pantheon::EvidenceState::Supportive; i.authorized=false; d=p.evaluate(i); assert(d.state==pantheon::RiseFallState::Warden); return 0;
}
