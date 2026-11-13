defmodule Eria.Observation do
  @moduledoc """
  A source-linked record of something actually observed.

  Observation data is kept separate from interpretations. The struct is immutable;
  corrections create a new record with a new identifier and an explicit relation
  to the superseded record.
  """

  @enforce_keys [:id, :domain, :subject_id, :metric, :value, :unit, :method,
                 :observed_at, :source, :raw_sha256]
  defstruct [
    :id, :domain, :subject_id, :metric, :value, :unit, :method,
    :observed_at, :source, :instrument, :conditions, :raw_sha256,
    :supersedes, quality: :unreviewed
  ]

  @domains ~w(plant animal cellular_molecular ecosystem earth)
  @metrics %{
    "plant" => ~w(photosynthesis_rate growth_rate water_exchange nutrient_uptake gene_expression),
    "animal" => ~w(physiology behavior development genetics population ecological_relationship),
    "cellular_molecular" => ~w(molecular_abundance sequence_variation cellular_signaling metabolism repair),
    "ecosystem" => ~w(energy_flow biomass biodiversity environmental_change resilience),
    "earth" => ~w(soil_moisture soil_temperature land_cover surface_water_level precipitation water_exchange air_temperature particulate_matter air_quality_index biodiversity_index biomass species_observation_count carbon_flux environmental_change resilience)
  }

  def domains, do: @domains
  def metrics, do: @metrics

  def new(attrs) when is_map(attrs) do
    with {:ok, domain} <- required_string(attrs, :domain),
         true <- domain in @domains || {:error, :unsupported_domain},
         {:ok, metric} <- required_string(attrs, :metric),
         true <- metric in Map.fetch!(@metrics, domain) || {:error, :unsupported_metric},
         {:ok, observed_at} <- parse_datetime(Map.get(attrs, :observed_at)),
         {:ok, raw_payload} <- required_string(attrs, :raw_payload),
         {:ok, source} <- required_string(attrs, :source),
         {:ok, subject_id} <- required_string(attrs, :subject_id),
         {:ok, method} <- required_string(attrs, :method),
         {:ok, unit} <- required_string(attrs, :unit),
         {:ok, value} <- numeric_value(Map.get(attrs, :value)) do
      observation = %__MODULE__{
        id: Map.get(attrs, :id) || new_id(),
        domain: domain,
        subject_id: subject_id,
        metric: metric,
        value: value,
        unit: unit,
        method: method,
        observed_at: observed_at,
        source: source,
        instrument: Map.get(attrs, :instrument),
        conditions: Map.get(attrs, :conditions, %{}),
        raw_sha256: :crypto.hash(:sha256, raw_payload) |> Base.encode16(case: :lower),
        supersedes: Map.get(attrs, :supersedes),
        quality: :unreviewed
      }

      {:ok, observation}
    else
      {:error, reason} -> {:error, reason}
      false -> {:error, :invalid_observation}
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
    "obs-" <> (:crypto.strong_rand_bytes(12) |> Base.url_encode64(padding: false))
  end
end

defmodule Eria.Inference do
  @moduledoc """
  An interpretation derived from one or more observations.
  It never masquerades as a direct measurement or clinical conclusion.
  """
  @enforce_keys [:id, :statement, :basis_observation_ids, :method, :uncertainty]
  defstruct [:id, :statement, :basis_observation_ids, :method, :uncertainty,
             :created_at, status: :hypothesis]
end
