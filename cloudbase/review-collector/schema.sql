-- Independent opt-in draft review table; old dcvlog_events remains unchanged.
CREATE TABLE IF NOT EXISTS public.dcvlog_draft_reviews (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  submission_id uuid NOT NULL UNIQUE,
  anonymous_id uuid NOT NULL,
  skill_version varchar(20) NOT NULL,
  client_count integer NOT NULL CHECK (client_count BETWEEN 1 AND 20),
  draft_status varchar(12) NOT NULL CHECK (draft_status IN ('ready', 'limited')),
  final_text text NOT NULL CHECK (char_length(final_text) BETWEEN 20 AND 12000),
  facts_summary text NOT NULL DEFAULT '' CHECK (char_length(facts_summary) <= 1600),
  consent_version varchar(40) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL DEFAULT (now() + interval '30 days')
);
CREATE INDEX IF NOT EXISTS dcvlog_draft_reviews_created_at_idx
  ON public.dcvlog_draft_reviews (created_at DESC);
ALTER TABLE public.dcvlog_draft_reviews ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.dcvlog_draft_reviews FROM PUBLIC, anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.dcvlog_draft_reviews TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.dcvlog_draft_reviews_id_seq TO service_role;

-- Expires_at does not auto-delete data: schedule this housekeeping SQL.
-- DELETE FROM public.dcvlog_draft_reviews WHERE expires_at < now();
