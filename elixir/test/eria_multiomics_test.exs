defmodule EriaMultiOmicsTest do
  use ExUnit.Case, async: true

  alias Eria.{Diagnostic.Support, Evidence.Graph, MultiOmics.Ingest, MultiOmics.Record}

  defp record_attrs(overrides \\ %{}) do
    Map.merge(%{
      domain: "cellular_molecular",
      subject_id: "sample-001",
      modality: "transcriptomics",
      assay: "RNA-seq",
      feature: "GENE-A",
      value: 4.2,
      unit: "normalized_count",
      source: "lab-export-01",
      instrument_id: "sequencer-01",
      observed_at: "2026-11-13T10:00:00Z",
      raw_payload: "raw-read-count-payload",
      reference_version: "reference-build-1",
      method_version: "pipeline-1.0",
      qc_status: "pending",
      qc_metadata: %{"reported_pass" => false}
    }, overrides)
  end

  test "accepts all declared omics modalities across all organism domains" do
    for domain <- Eria.Observation.domains(),
        modality <- Record.modalities() do
      assert {:ok, record} = Record.new(record_attrs(%{domain: domain, modality: modality}))
      assert record.domain == domain
      assert record.modality == modality
      assert byte_size(record.raw_sha256) == 64
    end
  end

  test "ingestion preserves accepted records and indexed rejections" do
    result = Ingest.ingest([
      record_attrs(%{id: "valid-1"}),
      record_attrs(%{domain: "unknown"})
    ])

    assert result.counts == %{received: 2, accepted: 1, rejected: 1}
    assert hd(result.accepted).id == "valid-1"
    assert hd(result.rejected).index == 2
    assert hd(result.rejected).reason == :unsupported_domain
  end

  test "records reference and method versions and supplied QC without certifying them" do
    assert {:ok, record} = Record.new(record_attrs())
    assert record.reference_version == "reference-build-1"
    assert record.method_version == "pipeline-1.0"
    assert record.qc_status == "pending"
  end

  test "evidence graph rejects findings that cite unknown source records" do
    assert {:ok, record} = Record.new(record_attrs(%{id: "omics-1"}))
    finding = %{id: "f-1", statement: "candidate signal", source_record_ids: ["missing"],
                method: "exploratory", uncertainty: "high"}
    assert {:error, :orphan_finding_source} = Graph.build([record], [finding])
  end

  test "research support links hypotheses and never grants diagnosis or action authority" do
    ingestion = Ingest.ingest([record_attrs(%{id: "omics-1"})])
    finding = %{id: "hyp-1", statement: "exploratory expression pattern",
                source_record_ids: ["omics-1"], method: "descriptive comparison",
                uncertainty: "unquantified; requires independent analysis"}

    assert {:ok, report} = Support.build(ingestion, [finding])
    assert report.scope == "all_biological_domains"
    assert report.interpretation_boundary.mode == :research_only
    assert report.interpretation_boundary.diagnoses == []
    assert report.interpretation_boundary.intervention_authorized == false
    assert report.interpretation_boundary.independent_review_required
    assert report.interpretation_boundary.explicit_authorization_required_for_any_downstream_action
    assert length(report.evidence_graph.edges) == 1
  end
end
