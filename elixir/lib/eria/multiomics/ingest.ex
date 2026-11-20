defmodule Eria.MultiOmics.Ingest do
  @moduledoc """
  Validates normalized multi-omics maps and preserves every rejection with its
  input position. It does not parse FASTQ/BAM/VCF/vendor files or certify assays.
  """

  alias Eria.MultiOmics.Record

  def ingest(records) when is_list(records) do
    {accepted, rejected} =
      records
      |> Enum.with_index(1)
      |> Enum.reduce({[], []}, fn {attrs, index}, {ok, errors} ->
        case Record.new(attrs) do
          {:ok, record} -> {[record | ok], errors}
          {:error, reason} -> {ok, [%{index: index, reason: reason} | errors]}
        end
      end)

    accepted = Enum.reverse(accepted)
    rejected = Enum.reverse(rejected)

    %{
      accepted: accepted,
      rejected: rejected,
      counts: %{received: length(records), accepted: length(accepted), rejected: length(rejected)},
      provenance: %{
        raw_payload_fingerprints: Enum.map(accepted, &%{record_id: &1.id, sha256: &1.raw_sha256}),
        source_records_are_immutable: true
      },
      limitations: [
        "Inputs must already be normalized maps; vendor-specific file decoding is not included.",
        "A raw-payload SHA-256 fingerprint establishes byte identity, not source authenticity.",
        "QC status and metadata are supplied claims and are not independently verified.",
        "Reference and method versions are recorded, not certified."
      ]
    }
  end

  def ingest(_), do: %{accepted: [], rejected: [%{index: nil, reason: :input_must_be_a_list}],
                       counts: %{received: 0, accepted: 0, rejected: 1}}
end
