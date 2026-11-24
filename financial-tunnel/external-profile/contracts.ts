export type ProfileRole = "member" | "financial_approver" | "profile_admin";
export type ProfileStatus = "ACTIVE" | "SUSPENDED";

export interface ExternalIdentity {
  issuer: string;
  subject: string;
  email?: string;
  displayName?: string;
}

export interface ExternalProfile extends ExternalIdentity {
  id: string;
  roles: ProfileRole[];
  status: ProfileStatus;
  createdAt: string;
  updatedAt: string;
}

export interface TransactionPreview {
  /** Subject of the identity that initiated the transaction; approver must differ. */
  initiatedBySubject: string;
  amountMinor: number;
  currency: string;
  destinationRef: string;
  network?: string;
  expiresAt: string;
}

export interface AuthorizationEvidence {
  id: string;
  profileId: string;
  actorSubject: string;
  action: string;
  preview: TransactionPreview;
  previewHash: string;
  decision: "ALLOW" | "DENY";
  reason: string;
  policyVersion: string;
  createdAt: string;
}

export interface ProfileEvent {
  id: string;
  profileId: string;
  actorSubject: string;
  eventType: "PROFILE_ROLES_CHANGED";
  roles: ProfileRole[];
  createdAt: string;
}

export interface ExternalProfileStore {
  upsertIdentity(identity: ExternalIdentity): Promise<ExternalProfile>;
  getProfile(id: string): Promise<ExternalProfile | null>;
  appendAuthorizationEvidence(evidence: AuthorizationEvidence): Promise<void>;
  getAuthorizationEvidence(id: string): Promise<AuthorizationEvidence | null>;
  setRoles(profileId: string, roles: ProfileRole[], actorSubject: string): Promise<ExternalProfile | null>;
  createCodeChangeProposal(proposal: CodeChangeProposal): Promise<void>;
  getCodeChangeProposal(id: string): Promise<CodeChangeProposal | null>;
  decideCodeChangeProposal(decision: CodeChangeDecision): Promise<CodeChangeDecision | null>;
  getCodeChangeDecision(proposalId: string): Promise<CodeChangeDecision | null>;
}


export interface CodeChangeProposal {
  id: string;
  proposerProfileId: string;
  proposerSubject: string;
  repository: "Vanellye/CodEXgen";
  branch: "feature/eria-financial-tunnel";
  baseSha: string;
  files: string[];
  patch: string;
  patchSha256: string;
  createdAt: string;
}

export interface CodeChangeDecision {
  id: string;
  proposalId: string;
  approverProfileId: string;
  approverSubject: string;
  decision: "ALLOW" | "DENY";
  reason: string;
  createdAt: string;
}
