defmodule Eria.Water.Storage do
  @moduledoc """
  Capacity and overflow planning for a declared storage vessel.
  The returned quantities are proposals, not valve or pump commands.
  """

  def plan(attrs) when is_map(attrs) do
    with {:ok, tank_id} <- required_id(attrs, :tank_id),
         {:ok, capacity} <- positive_number(attrs, :capacity_l),
         {:ok, current} <- non_negative_number(attrs, :current_volume_l),
         {:ok, proposed} <- non_negative_number(attrs, :proposed_inflow_l),
         true <- current <= capacity do
      remaining = capacity - current
      accepted = min(proposed, remaining)

      {:ok,
       %{
         workstream: :storage,
         tank_id: tank_id,
         capacity_l: capacity,
         current_volume_l: current,
         remaining_capacity_l: remaining,
         proposed_inflow_l: proposed,
         proposed_accepted_inflow_l: accepted,
         proposed_rejected_inflow_l: proposed - accepted,
         status: :proposal_only,
         execution_enabled: false
       }}
    else
      false -> {:error, :current_volume_exceeds_capacity}
      {:error, reason} -> {:error, reason}
    end
  end

  def plan(_), do: {:error, :invalid_storage_attributes}

  defp required_id(attrs, key) do
    case Map.get(attrs, key) do
      value when is_binary(value) and byte_size(value) > 0 -> {:ok, value}
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

  defp non_negative_number(attrs, key) do
    case Map.get(attrs, key) do
      value when is_integer(value) and value >= 0 -> {:ok, value}
      value when is_float(value) and value >= 0 and value < 1.0e308 -> {:ok, value}
      _ -> {:error, {:must_be_non_negative_number, key}}
    end
  end
end
