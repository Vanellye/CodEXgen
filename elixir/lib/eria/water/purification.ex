defmodule Eria.Water.Purification do
  @moduledoc """
  Describes a configured treatment train without asserting treatment efficacy
  or potability. Evidence and laboratory verification remain external inputs.
  """

  def plan(attrs) when is_map(attrs) do
    with {:ok, source_id} <- required_id(attrs, :source_id),
         {:ok, treatment_stages} <- stages(attrs),
         {:ok, sample_ids} <- optional_ids(attrs, :sample_observation_ids) do
      {:ok,
       %{
         workstream: :purification,
         source_id: source_id,
         treatment_stages: treatment_stages,
         sample_observation_ids: sample_ids,
         treatment_status: :configured_not_verified,
         potability_status: :not_established,
         execution_enabled: false
       }}
    end
  end

  def plan(_), do: {:error, :invalid_purification_attributes}

  defp required_id(attrs, key) do
    case Map.get(attrs, key) do
      value when is_binary(value) and byte_size(value) > 0 -> {:ok, value}
      _ -> {:error, {:missing_or_invalid, key}}
    end
  end

  defp stages(attrs) do
    case Map.get(attrs, :treatment_stages) do
      values when is_list(values) and values != [] ->
        valid =
          Enum.all?(values, fn stage ->
            is_map(stage) and
              is_binary(Map.get(stage, :id)) and byte_size(Map.get(stage, :id)) > 0 and
              is_binary(Map.get(stage, :process)) and byte_size(Map.get(stage, :process)) > 0
          end)

        if valid, do: {:ok, values}, else: {:error, :invalid_treatment_stage}
      _ -> {:error, :treatment_stages_required}
    end
  end

  defp optional_ids(attrs, key) do
    case Map.get(attrs, key, []) do
      values when is_list(values) ->
        if Enum.all?(values, &(is_binary(&1) and byte_size(&1) > 0)),
          do: {:ok, values},
          else: {:error, {:invalid_ids, key}}
      _ -> {:error, {:invalid_ids, key}}
    end
  end
end
