defmodule Eria.Water.Distribution do
  @moduledoc """
  Deterministic demand allocation by ascending numeric priority.
  Produces a distribution proposal only; it does not actuate pumps or valves.
  """

  def plan(attrs) when is_map(attrs) do
    with {:ok, network_id} <- required_id(attrs, :network_id),
         {:ok, available} <- non_negative_number(attrs, :available_flow_lpm),
         {:ok, demands} <- demands(attrs) do
      {allocations, _remaining} =
        demands
        |> Enum.sort_by(fn demand -> {demand.priority, demand.zone_id} end)
        |> Enum.map_reduce(available, fn demand, remaining ->
          supplied = min(demand.requested_flow_lpm, remaining)
          allocation = %{
            zone_id: demand.zone_id,
            priority: demand.priority,
            requested_flow_lpm: demand.requested_flow_lpm,
            proposed_supply_flow_lpm: supplied,
            unmet_flow_lpm: demand.requested_flow_lpm - supplied
          }

          {allocation, remaining - supplied}
        end)

      {:ok,
       %{
         workstream: :distribution,
         network_id: network_id,
         available_flow_lpm: available,
         allocations: allocations,
         total_proposed_supply_lpm: Enum.reduce(allocations, 0, &(&1.proposed_supply_flow_lpm + &2)),
         status: :proposal_only,
         execution_enabled: false
       }}
    end
  end

  def plan(_), do: {:error, :invalid_distribution_attributes}

  defp required_id(attrs, key) do
    case Map.get(attrs, key) do
      value when is_binary(value) and byte_size(value) > 0 -> {:ok, value}
      _ -> {:error, {:missing_or_invalid, key}}
    end
  end

  defp demands(attrs) do
    case Map.get(attrs, :demands) do
      values when is_list(values) and values != [] ->
        parsed =
          Enum.map(values, fn demand ->
            with true <- is_map(demand),
                 zone when is_binary(zone) and byte_size(zone) > 0 <- Map.get(demand, :zone_id),
                 priority when is_integer(priority) and priority >= 0 <- Map.get(demand, :priority),
                 {:ok, requested} <- demand_number(Map.get(demand, :requested_flow_lpm)) do
              {:ok, %{zone_id: zone, priority: priority, requested_flow_lpm: requested}}
            else
              _ -> {:error, :invalid_distribution_demand}
            end
          end)

        if Enum.all?(parsed, &match?({:ok, _}, &1)),
          do: {:ok, Enum.map(parsed, fn {:ok, value} -> value end)},
          else: {:error, :invalid_distribution_demand}
      _ -> {:error, :demands_required}
    end
  end

  defp demand_number(value) when is_integer(value) and value >= 0, do: {:ok, value}
  defp demand_number(value) when is_float(value) and value >= 0 and value < 1.0e308, do: {:ok, value}
  defp demand_number(_), do: {:error, :invalid_requested_flow}

  defp non_negative_number(attrs, key) do
    case Map.get(attrs, key) do
      value when is_integer(value) and value >= 0 -> {:ok, value}
      value when is_float(value) and value >= 0 and value < 1.0e308 -> {:ok, value}
      _ -> {:error, {:must_be_non_negative_number, key}}
    end
  end
end
