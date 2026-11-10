#ifndef PANTHEON_ACCESS_TABLET_HPP
#define PANTHEON_ACCESS_TABLET_HPP

#include <string>
#include <vector>

namespace pantheon {

enum class AccessOperation { Read, Write };

struct AccessRequirement {
    std::string resource;
    AccessOperation operation;

    AccessRequirement() : resource(), operation(AccessOperation::Read) {}
    AccessRequirement(const std::string& resourceName, AccessOperation op)
        : resource(resourceName), operation(op) {}
};

// A grant is a narrowly scoped, host-issued record. This structure does not
// authenticate its issuer; production hosts must validate the invitation and
// approval record before constructing trusted grants.
struct AccessGrant {
    std::string subject;
    std::string resource;
    AccessOperation operation;
    std::string invitationId;
    std::string sourceRevision;
    long long expiresAtUnixSeconds;
    bool approved;

    AccessGrant()
        : subject(), resource(), operation(AccessOperation::Read),
          invitationId(), sourceRevision(), expiresAtUnixSeconds(0),
          approved(false) {}
};

struct AccessContext {
    std::string subject;
    std::string invitationId;
    std::string sourceRevision;
    long long nowUnixSeconds;

    AccessContext()
        : subject(), invitationId(), sourceRevision(), nowUnixSeconds(0) {}
};

struct AccessDecision {
    bool granted;
    std::string reason;

    AccessDecision() : granted(false), reason("not_evaluated") {}
};

class AccessTablet {
public:
    // Exact-match, default-deny evaluation. No wildcard, inherited, or
    // implicit read/write rights are supported.
    AccessDecision evaluate(const AccessRequirement& requirement,
                            const AccessContext& context,
                            const std::vector<AccessGrant>& grants) const;

    AccessDecision evaluateAll(const std::vector<AccessRequirement>& requirements,
                               const AccessContext& context,
                               const std::vector<AccessGrant>& grants) const;
};

const char* accessOperationName(AccessOperation operation);

} // namespace pantheon

#endif
