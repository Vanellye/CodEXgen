#ifndef PANTHEON_ERO_SOURCE_HPP
#define PANTHEON_ERO_SOURCE_HPP
#include <string>
#include <vector>
namespace pantheon { namespace ero {
enum class EvidenceState { VERIFIED, INFERRED, UNKNOWN };
enum class SpectralLayer { SOURCE_IDENTITY, HISTORY, DEPENDENCY, WRITE_PERMISSION, UNCERTAINTY };
struct SourceIdentity { std::string id; std::string label; std::string originReference; };
struct SpectralRecord { SpectralLayer layer; EvidenceState evidence; std::string subject; std::string detail; };
struct InspectionReport { bool valid; std::vector<std::string> findings; InspectionReport() : valid(false) {} };
// ERO identifies an origin; EYES_UP records layered inspection. Descriptive only:
// no write grants, code execution, or promotion of inferred claims to verified facts.
class EroSource {
public:
 explicit EroSource(const SourceIdentity& identity);
 bool valid() const;
 const SourceIdentity& identity() const;
 bool addRecord(const SpectralRecord& record);
 InspectionReport eyesUp() const;
 const std::vector<SpectralRecord>& records() const;
private:
 SourceIdentity identity_;
 std::vector<SpectralRecord> records_;
};
} }
#endif
