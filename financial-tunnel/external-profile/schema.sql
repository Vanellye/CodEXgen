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
