defmodule Eria.Earth do
  @moduledoc """
  Earth's environmental observation domain, with measured subdomains and
  a separate consent-gated Sacral-Lift descriptive cue-analysis engine.
  """

  alias Eria.Observation

  @subdomains [:land, :water, :air, :life, :climate]
  @metrics %{
    land: ~w(soil_moisture soil_temperature land_cover),
    water: ~w(surface_water_level precipitation water_exchange),
    air: ~w(air_temperature particulate_matter air_quality_index),
    life: ~w(biodiversity_index biomass species_observation_count),
    climate: ~w(carbon_flux environmental_change resilience)
  }

  def subdomains, do: @subdomains
  def metrics, do: @metrics
  def engines, do: [Eria.Earth.SacralLift]

  def subdomain_for_metric(metric) when is_binary(metric) do
    case Enum.find(@metrics, fn {_domain, names} -> metric in names end) do
      {subdomain, _names} -> {:ok, subdomain}
      nil -> {:error, :unknown_earth_metric}
    end
  end

  def subdomain_for_metric(_), do: {:error, :invalid_metric}

  def validate_observation(%Observation{domain: "earth", metric: metric} = observation) do
    with {:ok, subdomain} <- subdomain_for_metric(metric) do
      {:ok, %{observation_id: observation.id, domain: :earth, subdomain: subdomain,
              metric: metric, provenance: observation.raw_sha256}}
    end
  end

  def validate_observation(%Observation{}), do: {:error, :observation_is_not_in_earth_domain}
  def validate_observation(_), do: {:error, :invalid_observation}
end
