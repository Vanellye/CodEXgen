defmodule Eria.Interpreter do
  @moduledoc """
  Validates and summarizes observations without silently converting them
  into causal claims, diagnoses, or action permissions.
  """

  alias Eria.{Observation, Quality}

  def interpret(records) when is_list(records) do
    unless Enum.all?(records, &match?(%Observation{}, &1)) do
      raise ArgumentError, "interpret/1 accepts only Eria.Observation records"
    end

    qualified = Enum.map(records, fn record ->
      quality = Quality.check(record)
      %{observation: record, quality: quality}
    end)

    %{
      engine: "ERIA Code-Language Interpretation Engine",
      schema_version: "1.0",
      generated_at: DateTime.utc_now() |> DateTime.to_iso8601(),
      counts: %{
        total: length(records),
        qualified: Enum.count(qualified, &(&1.quality.status == :qualified)),
        rejected: Enum.count(qualified, &(&1.quality.status == :rejected))
      },
      observations: Enum.map(qualified, fn item ->
        %{
          observation_id: item.observation.id,
          domain: item.observation.domain,
          subject_id: item.observation.subject_id,
          metric: item.observation.metric,
          value: item.observation.value,
          unit: item.observation.unit,
          observed_at: DateTime.to_iso8601(item.observation.observed_at),
          source: item.observation.source,
          raw_sha256: item.observation.raw_sha256,
          quality: item.quality
        }
      end),
      inferences: [],
      interpretation_boundary: [
        "The report describes submitted observations and structural quality checks only.",
        "No causal relationship is inferred by default.",
        "No clinical diagnosis or authorization for biological modification is produced."
      ]
    }
  end

  def interpret(_), do: {:error, :records_must_be_a_list}
end
