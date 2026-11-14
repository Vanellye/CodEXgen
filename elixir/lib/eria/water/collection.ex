defmodule Eria.Water.Collection do
  @moduledoc """
  Pure planning contract for water-source collection and intake.
  It produces a proposal only; it does not open an intake or control a pump.
  """

  def plan(attrs) when is_map(attrs) do
    with {:ok, source_id} <- required_id(attrs, :source_id),
         {:ok, observation_ids} <- required_ids(attrs, :source_observation_ids),
         {:ok, available} <- positive_number(attrs, :available_flow_lpm),
         {:ok, requested} <- positive_number(attrs, :requested_flow_lpm),
         true <- requested <= available do
      {:ok,
       %{
         workstream: :collection,
         source_id: source_id,
         source_observation_ids: observation_ids,
         available_flow_lpm: available,
         proposed_intake_flow_lpm: requested,
         status: :proposal_only,
         execution_enabled: false
       }}
    else
      false -> {:error, :requested_flow_exceeds_observed_availability}
      {:error, reason} -> {:error, reason}
    end
  end

  def plan(_), do: {:error, :invalid_collection_attributes}

  defp required_id(attrs, key) do
    case Map.get(attrs, key) do
      value when is_binary(value) and byte_size(value) > 0 -> {:ok, value}
      _ -> {:error, {:missing_or_invalid, key}}
    end
  end

  defp required_ids(attrs, key) do
    case Map.get(attrs, key) do
      values when is_list(values) and values != [] ->
        if Enum.all?(values, &(is_binary(&1) and byte_size(&1) > 0)),
          do: {:ok, values},
          else: {:error, {:invalid_ids, key}}
      _ -> {:error, {:missing_or_invalid, key}}
    end
  end

  defp positive_number(attrs, key) do
    case Map.get(attrs, key) do
      value when is_integer(value) and value > 0 -> {:ok, value}
      value when is_float(value) and value > 0 and value < 1.0e308 -> {:ok, value}
      _ -> {:error, {:must_be_positive_number, key}}
    end
  end
end
