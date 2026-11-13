defmodule Eria.Diagnostic.Support do
  @moduledoc """
  Research-only evidence summaries across ERIA biological domains.
  This module does not diagnose, rank clinical risk, or authorize intervention.
  """

  alias Eria.Evidence.Graph

  def build(%{accepted: records, rejected: rejected} = ingestion, findings \\ [])
      when is_list(records) and is_list(rejected) do
    with {:ok, graph} <- Graph.build(records, findings) do
      domain_counts = Enum.frequencies_by(records, & &1.domain)
      modality_counts = Enum.frequencies_by(records, & &1.modality)

      {:ok, %{
        report_type: "research_evidence_summary",
        scope: "all_biological_domains",
        generated_at: DateTime.utc_now() |> DateTime.to_iso8601(),
        counts: %{
          records_received: get_in(ingestion, [:counts, :received]) || length(records) + length(rejected),
          records_accepted: length(records),
          records_rejected: length(rejected),
          research_hypotheses: length(graph.findings)
        },
        domain_counts: domain_counts,
        modality_counts: modality_counts,
        evidence_graph: graph,
        rejected_records: rejected,
        interpretation_boundary: %{
          mode: :research_only,
          diagnoses: [],
          clinical_recommendations: [],
          intervention_authorized: false,
          independent_review_required: true,
          explicit_authorization_required_for_any_downstream_action: true
        },
        limitations: [
          "A research evidence summary is not a medical or veterinary diagnosis.",
          "No causal inference is made unless separately specified and validated by a reviewed method.",
          "No reference genome, database, assay, instrument calibration, or QC claim is independently verified here.",
          "Research hypotheses require independent review and must retain links to their source records."
        ]
      }}
    end
  end

  def build(_, _), do: {:error, :invalid_ingestion_result}
end
