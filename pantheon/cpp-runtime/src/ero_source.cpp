#include "pantheon/ero_source.hpp"
namespace pantheon { namespace ero {
EroSource::EroSource(const SourceIdentity& identity) : identity_(identity) {}
bool EroSource::valid() const {
 return !identity_.id.empty() && !identity_.label.empty() && !identity_.originReference.empty();
}
const SourceIdentity& EroSource::identity() const { return identity_; }
bool EroSource::addRecord(const SpectralRecord& record) {
 if (!valid() || record.subject.empty() || record.detail.empty()) return false;
 records_.push_back(record); return true;
}
InspectionReport EroSource::eyesUp() const {
 InspectionReport report;
 if (!valid()) { report.findings.push_back("source_identity_incomplete"); return report; }
 report.valid = true; report.findings.push_back("source_identity_present");
 if (records_.empty()) report.findings.push_back("spectral_series_empty");
 bool history=false, dependencies=false, permissions=false, uncertainty=false;
 for (std::vector<SpectralRecord>::const_iterator it=records_.begin(); it!=records_.end(); ++it) {
  if (it->layer==SpectralLayer::HISTORY) history=true;
  if (it->layer==SpectralLayer::DEPENDENCY) dependencies=true;
  if (it->layer==SpectralLayer::WRITE_PERMISSION) permissions=true;
  if (it->layer==SpectralLayer::UNCERTAINTY) uncertainty=true;
  if (it->evidence==EvidenceState::INFERRED) report.findings.push_back("inference_requires_verification:"+it->subject);
  else if (it->evidence==EvidenceState::UNKNOWN) report.findings.push_back("unknown_requires_investigation:"+it->subject);
 }
 if (!history) report.findings.push_back("history_not_inspected");
 if (!dependencies) report.findings.push_back("dependencies_not_inspected");
 if (!permissions) report.findings.push_back("write_rights_not_verified");
 if (!uncertainty) report.findings.push_back("uncertainty_not_recorded");
 return report;
}
const std::vector<SpectralRecord>& EroSource::records() const { return records_; }
} }
