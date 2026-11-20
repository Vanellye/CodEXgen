#include "pantheon/ero_source.hpp"
#include <cassert>
int main() {
 using namespace pantheon::ero;
 SourceIdentity id; id.id="ero-origin-001"; id.label="ERO"; id.originReference="declared-source://ero";
 EroSource source(id); assert(source.valid());
 SpectralRecord r; r.layer=SpectralLayer::HISTORY; r.evidence=EvidenceState::VERIFIED; r.subject="origin-history"; r.detail="history inspected"; assert(source.addRecord(r));
 r.layer=SpectralLayer::DEPENDENCY; r.evidence=EvidenceState::INFERRED; r.subject="dependency-map"; r.detail="candidate relationship"; assert(source.addRecord(r));
 r.layer=SpectralLayer::WRITE_PERMISSION; r.evidence=EvidenceState::UNKNOWN; r.subject="write-scope"; r.detail="authorization not established"; assert(source.addRecord(r));
 r.layer=SpectralLayer::UNCERTAINTY; r.evidence=EvidenceState::VERIFIED; r.subject="open-questions"; r.detail="unknowns recorded"; assert(source.addRecord(r));
 InspectionReport report=source.eyesUp(); assert(report.valid); assert(!report.findings.empty()); assert(source.records().size()==4);
 SourceIdentity incomplete; incomplete.label="ERO"; EroSource invalid(incomplete); assert(!invalid.valid()); assert(!invalid.addRecord(r)); assert(!invalid.eyesUp().valid);
 return 0;
}
