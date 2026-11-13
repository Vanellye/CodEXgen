defmodule Eria.Water.Recycling do
  @moduledoc """
  Tracks a wastewater stream and a proposed reuse classification.
  It never infers that treated water is safe for a use; evidence review is
  required and the quality status remains unverified.
  """

  @reuse_classes ~w(non_potable_irrigation industrial_process toilet_flushing)

  def plan(attrs) when is_map(attrs) do
    with {:ok, stream_id} <- required_id(attrs, :stream_id),
         {:ok, input_volume} <- non_negative_number(attrs, :input_volume_l),
         {:ok, proposed_recovered} <- non_negative_number(attrs, :proposed_recovered_volume_l),
         true <- proposed_recovered <= input_volume,
         {:ok, target_use} <- target_use(attrs),
         {:ok, treatment_ids} <- required_ids(attrs, :treatment_stage_ids),
         {:ok, evidence_ids} <- optional_ids(attrs, :quality_observation_ids) do
      {:ok,
       %{
         workstream: :recycling,
         stream_id: stream_id,
         input_volume_l: input_volume,
         proposed_recovered_volume_l: proposed_recovered,
         target_use: target_use,
         treatment_stage_ids: treatment_ids,
         quality_observation_ids: evidence_ids,
         reuse_quality_status: :unverified,
         suitability_status: :not_established,
         execution_enabled: false
       }}
    else
      false -> {:error, :recovered_volume_exceeds_input}
      {:error, reason} -> {:error, reason}
    end
  end

  def plan(_), do: {:error, :invalid_recycling_attributes}

  defp target_use(attrs) do
    case Map.get(attrs, :target_use) do
      value when is_binary(value) ->
        if value in @reuse_classes, do: {:ok, value}, else: {:error, :unsupported_reuse_class}
      _ -> {:error, :invalid_reuse_class}
    end
  end

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

  defp optional_ids(attrs, key) do
    case Map.get(attrs, key, []) do
      values when is_list(values) ->
        if Enum.all?(values, &(is_binary(&1) and byte_size(&1) > 0)),
          do: {:ok, values},
          else: {:error, {:invalid_ids, key}}
      _ -> {:error, {:invalid_ids, key}}
    end
  end

  defp non_negative_number(attrs, key) do
    case Map.get(attrs, key) do
      value when is_integer(value) and value >= 0 -> {:ok, value}
      value when is_float(value) and value >= 0 and value < 1.0e308 -> {:ok, value}
      _ -> {:error, {:must_be_non_negative_number, key}}
    end
  end
end
