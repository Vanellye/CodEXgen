defmodule Eria.MultiOmics.Record do
  @moduledoc """
  A normalized, source-linked multi-omics measurement. This is an ingestion
  contract, not a parser for vendor-specific files or a biological conclusion.
  """

  @enforce_keys [:id, :domain, :subject_id, :modality, :assay, :feature, :value,
                 :unit, :source, :observed_at, :raw_sha256, :reference_version,
                 :method_version]
  defstruct [:id, :domain, :subject_id, :modality, :assay, :feature, :value,
             :unit, :source, :instrument_id, :observed_at, :raw_sha256,
             :reference_version, :method_version, :qc_status, :qc_metadata]

  @modalities ~w(genomics transcriptomics epigenomics proteomics metabolomics lipidomics microbiomics phenomics)

  def modalities, do: @modalities

  def new(attrs) when is_map(attrs) do
    with {:ok, domain} <- required_string(attrs, :domain),
         true <- domain in Eria.Observation.domains() or {:error, :unsupported_domain},
         {:ok, modality} <- required_string(attrs, :modality),
         true <- modality in @modalities or {:error, :unsupported_modality},
         {:ok, subject_id} <- required_string(attrs, :subject_id),
         {:ok, assay} <- required_string(attrs, :assay),
         {:ok, feature} <- required_string(attrs, :feature),
         {:ok, unit} <- required_string(attrs, :unit),
         {:ok, source} <- required_string(attrs, :source),
         {:ok, reference_version} <- required_string(attrs, :reference_version),
         {:ok, method_version} <- required_string(attrs, :method_version),
         {:ok, raw_payload} <- required_string(attrs, :raw_payload),
         {:ok, observed_at} <- parse_datetime(Map.get(attrs, :observed_at)),
         {:ok, value} <- numeric_value(Map.get(attrs, :value)) do
      {:ok, %__MODULE__{
        id: Map.get(attrs, :id) || new_id(),
        domain: domain,
        subject_id: subject_id,
        modality: modality,
        assay: assay,
        feature: feature,
        value: value,
        unit: unit,
        source: source,
        instrument_id: Map.get(attrs, :instrument_id),
        observed_at: observed_at,
        raw_sha256: :crypto.hash(:sha256, raw_payload) |> Base.encode16(case: :lower),
        reference_version: reference_version,
        method_version: method_version,
        qc_status: Map.get(attrs, :qc_status, "pending"),
        qc_metadata: Map.get(attrs, :qc_metadata, %{})
      }}
    else
      {:error, reason} -> {:error, reason}
      false -> {:error, :invalid_multiomics_record}
    end
  end

  def new(_), do: {:error, :invalid_attributes}

  defp required_string(attrs, key) do
    case Map.get(attrs, key) do
      value when is_binary(value) and byte_size(value) > 0 -> {:ok, value}
      _ -> {:error, {:missing_or_invalid, key}}
    end
  end

  defp parse_datetime(%DateTime{} = value), do: {:ok, value}
  defp parse_datetime(value) when is_binary(value) do
    case DateTime.from_iso8601(value) do
      {:ok, datetime, _offset} -> {:ok, datetime}
      _ -> {:error, :invalid_observed_at}
    end
  end
  defp parse_datetime(_), do: {:error, :invalid_observed_at}

  defp numeric_value(value) when is_integer(value), do: {:ok, value}
  defp numeric_value(value) when is_float(value) do
    if value == value and abs(value) < 1.0e308, do: {:ok, value}, else: {:error, :non_finite_value}
  end
  defp numeric_value(value) when is_binary(value) do
    case Float.parse(value) do
      {number, ""} -> numeric_value(number)
      _ ->
        case Integer.parse(value) do
          {integer, ""} -> {:ok, integer}
          _ -> {:error, :value_must_be_numeric}
        end
    end
  end
  defp numeric_value(_), do: {:error, :value_must_be_numeric}

  defp new_id do
    "omics-" <> (:crypto.strong_rand_bytes(12) |> Base.url_encode64(padding: false))
  end
end
