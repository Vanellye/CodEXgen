defmodule Eria.Quality do
  @moduledoc """
  Conservative quality qualification. Passing checks means a record is
  structurally usable; it does not prove biological accuracy or calibration.
  """

  alias Eria.Observation

  def check(%Observation{} = observation) do
    checks = [
      {:source_present, is_binary(observation.source) and observation.source != ""},
      {:raw_hash_sha256, Regex.match?(~r/^[a-f0-9]{64}$/, observation.raw_sha256 || "")},
      {:timestamp_present, match?(%DateTime{}, observation.observed_at)},
      {:unit_present, is_binary(observation.unit) and observation.unit != ""},
      {:method_present, is_binary(observation.method) and observation.method != ""},
      {:numeric_value, is_number(observation.value)},
      {:domain_metric_pair, observation.metric in Map.fetch!(Observation.metrics(), observation.domain)}
    ]

    failed = for {name, false} <- checks, do: name
    status = if failed == [], do: :qualified, else: :rejected

    %{
      observation_id: observation.id,
      status: status,
      checks: Map.new(checks),
      failed_checks: failed,
      limitations: [
        "No instrument calibration certificate was independently verified.",
        "No biological plausibility or clinical validity is implied."
      ]
    }
  end
end
