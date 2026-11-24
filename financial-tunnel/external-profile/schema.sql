CREATE TABLE IF NOT EXISTS external_profiles (
  id uuid PRIMARY KEY,
  issuer text NOT NULL,
  subject text NOT NULL,
  email text,
  display_name text,
  roles text[] NOT NULL DEFAULT ARRAY['member']::text[],
  status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','SUSPENDED')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (issuer, subject)
);

CREATE TABLE IF NOT EXISTS external_authorization_evidence (
  id uuid PRIMARY KEY,
  profile_id uuid NOT NULL REFERENCES external_profiles(id),
  actor_subject text NOT NULL,
  action text NOT NULL,
  preview jsonb NOT NULL,
  preview_hash char(64) NOT NULL,
  decision text NOT NULL CHECK (decision IN ('ALLOW','DENY')),
  reason text NOT NULL,
  policy_version text NOT NULL,
  created_at timestamptz NOT NULL
);

CREATE TABLE IF NOT EXISTS external_profile_events (
  id uuid PRIMARY KEY,
  profile_id uuid NOT NULL REFERENCES external_profiles(id),
  actor_subject text NOT NULL,
  event_type text NOT NULL,
  roles text[] NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Application roles should receive INSERT/SELECT only on evidence tables.
-- The trigger also rejects accidental UPDATE/DELETE through an over-privileged connection.
CREATE OR REPLACE FUNCTION reject_external_evidence_mutation() RETURNS trigger AS $$
BEGIN RAISE EXCEPTION 'external evidence is append-only'; END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS external_authorization_evidence_immutable ON external_authorization_evidence;
CREATE TRIGGER external_authorization_evidence_immutable
BEFORE UPDATE OR DELETE ON external_authorization_evidence
FOR EACH ROW EXECUTE FUNCTION reject_external_evidence_mutation();

DROP TRIGGER IF EXISTS external_profile_events_immutable ON external_profile_events;
CREATE TRIGGER external_profile_events_immutable
BEFORE UPDATE OR DELETE ON external_profile_events
FOR EACH ROW EXECUTE FUNCTION reject_external_evidence_mutation();

CREATE INDEX IF NOT EXISTS external_evidence_profile_created
  ON external_authorization_evidence(profile_id, created_at DESC);


-- ADMIN-controlled code changes: proposals and decisions are separate append-only records.
-- Approval authorizes a reviewed patch for the feature branch; it does not execute or commit it.
CREATE TABLE IF NOT EXISTS external_code_change_proposals (
  id uuid PRIMARY KEY,
  proposer_profile_id uuid NOT NULL REFERENCES external_profiles(id),
  proposer_subject text NOT NULL,
  repository text NOT NULL CHECK (repository = 'Vanellye/CodEXgen'),
  branch text NOT NULL CHECK (branch = 'feature/eria-financial-tunnel'),
  base_sha char(40) NOT NULL CHECK (base_sha ~ '^[0-9a-fA-F]{40}$'),
  files jsonb NOT NULL CHECK (jsonb_typeof(files) = 'array'),
  patch text NOT NULL CHECK (length(patch) BETWEEN 1 AND 131072),
  patch_sha256 char(64) NOT NULL CHECK (patch_sha256 ~ '^[0-9a-f]{64}$'),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS external_code_change_decisions (
  id uuid PRIMARY KEY,
  proposal_id uuid NOT NULL UNIQUE REFERENCES external_code_change_proposals(id),
  approver_profile_id uuid NOT NULL REFERENCES external_profiles(id),
  approver_subject text NOT NULL,
  decision text NOT NULL CHECK (decision IN ('ALLOW','DENY')),
  reason text NOT NULL CHECK (length(reason) BETWEEN 1 AND 500),
  created_at timestamptz NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS external_code_change_proposals_immutable ON external_code_change_proposals;
CREATE TRIGGER external_code_change_proposals_immutable
BEFORE UPDATE OR DELETE ON external_code_change_proposals
FOR EACH ROW EXECUTE FUNCTION reject_external_evidence_mutation();

DROP TRIGGER IF EXISTS external_code_change_decisions_immutable ON external_code_change_decisions;
CREATE TRIGGER external_code_change_decisions_immutable
BEFORE UPDATE OR DELETE ON external_code_change_decisions
FOR EACH ROW EXECUTE FUNCTION reject_external_evidence_mutation();

CREATE INDEX IF NOT EXISTS external_code_change_proposals_owner_created
  ON external_code_change_proposals(proposer_profile_id, created_at DESC);
