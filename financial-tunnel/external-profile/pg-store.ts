import { randomUUID } from "node:crypto";
import type { Pool } from "pg";
import type {
  AuthorizationEvidence, CodeChangeDecision, CodeChangeProposal, ExternalIdentity, ExternalProfile, ExternalProfileStore, ProfileRole,
} from "./contracts.ts";

type ProfileRow = {
  id: string; issuer: string; subject: string; email: string | null; display_name: string | null;
  roles: ProfileRole[]; status: "ACTIVE" | "SUSPENDED"; created_at: Date; updated_at: Date;
};
const mapProfile = (r: ProfileRow): ExternalProfile => ({
  id: r.id, issuer: r.issuer, subject: r.subject, email: r.email ?? undefined,
  displayName: r.display_name ?? undefined, roles: r.roles, status: r.status,
  createdAt: r.created_at.toISOString(), updatedAt: r.updated_at.toISOString(),
});

export class PostgresExternalProfileStore implements ExternalProfileStore {
  private readonly pool: Pool;

  constructor(pool: Pool) {
    this.pool = pool;
  }

  async upsertIdentity(identity: ExternalIdentity): Promise<ExternalProfile> {
    const result = await this.pool.query<ProfileRow>(
      `INSERT INTO external_profiles (id, issuer, subject, email, display_name)
       VALUES ($1,$2,$3,$4,$5)
       ON CONFLICT (issuer, subject) DO UPDATE
         SET email = EXCLUDED.email, display_name = EXCLUDED.display_name, updated_at = now()
       RETURNING * `,
      [randomUUID(), identity.issuer, identity.subject, identity.email ?? null, identity.displayName ?? null],
    );
    return mapProfile(result.rows[0]);
  }

  async getProfile(id: string): Promise<ExternalProfile | null> {
    const result = await this.pool.query<ProfileRow>("SELECT * FROM external_profiles WHERE id=$1", [id]);
    return result.rows[0] ? mapProfile(result.rows[0]) : null;
  }

  async appendAuthorizationEvidence(e: AuthorizationEvidence): Promise<void> {
    await this.pool.query(
      `INSERT INTO external_authorization_evidence
       (id, profile_id, actor_subject, action, preview, preview_hash, decision, reason, policy_version, created_at)
       VALUES ($1,$2,$3,$4,$5::jsonb,$6,$7,$8,$9,$10)`,
      [e.id,e.profileId,e.actorSubject,e.action,JSON.stringify(e.preview),e.previewHash,e.decision,e.reason,e.policyVersion,e.createdAt],
    );
  }

  async getAuthorizationEvidence(id: string): Promise<AuthorizationEvidence | null> {
    const r = await this.pool.query(
      "SELECT * FROM external_authorization_evidence WHERE id=$1", [id],
    );
    const x = r.rows[0];
    if (!x) return null;
    return {
      id:x.id, profileId:x.profile_id, actorSubject:x.actor_subject, action:x.action,
      preview:x.preview, previewHash:x.preview_hash, decision:x.decision, reason:x.reason,
      policyVersion:x.policy_version, createdAt:new Date(x.created_at).toISOString(),
    };
  }

  async setRoles(profileId: string, roles: ProfileRole[], actorSubject: string): Promise<ExternalProfile | null> {
    const client = await this.pool.connect();
    try {
      await client.query("BEGIN");
      const updated = await client.query<ProfileRow>(
        "UPDATE external_profiles SET roles=$2, updated_at=now() WHERE id=$1 RETURNING *",
        [profileId, roles],
      );
      if (!updated.rows[0]) { await client.query("ROLLBACK"); return null; }
      await client.query(
        `INSERT INTO external_profile_events (id, profile_id, actor_subject, event_type, roles)
         VALUES ($1,$2,$3,'PROFILE_ROLES_CHANGED',$4)`,
        [randomUUID(), profileId, actorSubject, roles],
      );
      await client.query("COMMIT");
      return mapProfile(updated.rows[0]);
    } catch (error) {
      await client.query("ROLLBACK");
      throw error;
    } finally { client.release(); }
  }

  async createCodeChangeProposal(p: CodeChangeProposal): Promise<void> {
    await this.pool.query(
      `INSERT INTO external_code_change_proposals
       (id, proposer_profile_id, proposer_subject, repository, branch, base_sha, files, patch, patch_sha256, created_at)
       VALUES ($1,$2,$3,$4,$5,$6,$7::jsonb,$8,$9,$10)`,
      [p.id,p.proposerProfileId,p.proposerSubject,p.repository,p.branch,p.baseSha,JSON.stringify(p.files),p.patch,p.patchSha256,p.createdAt],
    );
  }

  async getCodeChangeProposal(id: string): Promise<CodeChangeProposal | null> {
    const r = await this.pool.query("SELECT * FROM external_code_change_proposals WHERE id=$1", [id]);
    const x = r.rows[0];
    if (!x) return null;
    return {
      id:x.id, proposerProfileId:x.proposer_profile_id, proposerSubject:x.proposer_subject,
      repository:x.repository, branch:x.branch, baseSha:x.base_sha,
      files:x.files, patch:x.patch, patchSha256:x.patch_sha256,
      createdAt:new Date(x.created_at).toISOString(),
    };
  }

  async decideCodeChangeProposal(d: CodeChangeDecision): Promise<CodeChangeDecision | null> {
    const r = await this.pool.query(
      `INSERT INTO external_code_change_decisions
       (id, proposal_id, approver_profile_id, approver_subject, decision, reason, created_at)
       VALUES ($1,$2,$3,$4,$5,$6,$7)
       ON CONFLICT (proposal_id) DO NOTHING
       RETURNING *`,
      [d.id,d.proposalId,d.approverProfileId,d.approverSubject,d.decision,d.reason,d.createdAt],
    );
    const x = r.rows[0];
    return x ? {
      id:x.id, proposalId:x.proposal_id, approverProfileId:x.approver_profile_id,
      approverSubject:x.approver_subject, decision:x.decision, reason:x.reason,
      createdAt:new Date(x.created_at).toISOString(),
    } : null;
  }

  async getCodeChangeDecision(proposalId: string): Promise<CodeChangeDecision | null> {
    const r = await this.pool.query("SELECT * FROM external_code_change_decisions WHERE proposal_id=$1", [proposalId]);
    const x = r.rows[0];
    return x ? {
      id:x.id, proposalId:x.proposal_id, approverProfileId:x.approver_profile_id,
      approverSubject:x.approver_subject, decision:x.decision, reason:x.reason,
      createdAt:new Date(x.created_at).toISOString(),
    } : null;
  }

}
