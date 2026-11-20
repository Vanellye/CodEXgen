defmodule EriaWaterWorkstreamsTest do
  use ExUnit.Case, async: true

  alias Eria.Water.{Collection, Distribution, Flow, Purification, Recycling, Storage}

  test "collection requires source-linked flow observations and bounds intake" do
    attrs = %{
      source_id: "river-intake-1",
      source_observation_ids: ["obs-flow-1"],
      available_flow_lpm: 120,
      requested_flow_lpm: 80
    }

    assert {:ok, result} = Collection.plan(attrs)
    assert result.proposed_intake_flow_lpm == 80
    assert result.execution_enabled == false
    assert {:error, :requested_flow_exceeds_observed_availability} =
             Collection.plan(%{attrs | requested_flow_lpm: 121})
  end

  test "purification records treatment stages without asserting potability" do
    attrs = %{
      source_id: "intake-1",
      treatment_stages: [%{id: "filter-1", process: "sediment_filtration"}],
      sample_observation_ids: ["sample-before-1"]
    }

    assert {:ok, result} = Purification.plan(attrs)
    assert result.treatment_status == :configured_not_verified
    assert result.potability_status == :not_established
    assert result.execution_enabled == false
  end

  test "storage calculates bounded proposed inflow and overflow remainder" do
    attrs = %{
      tank_id: "tank-1",
      capacity_l: 1000,
      current_volume_l: 900,
      proposed_inflow_l: 150
    }

    assert {:ok, result} = Storage.plan(attrs)
    assert result.proposed_accepted_inflow_l == 100
    assert result.proposed_rejected_inflow_l == 50
    assert {:error, :current_volume_exceeds_capacity} =
             Storage.plan(%{attrs | current_volume_l: 1001})
  end

  test "distribution allocates available flow by priority without dispatch" do
    attrs = %{
      network_id: "network-1",
      available_flow_lpm: 100,
      demands: [
        %{zone_id: "zone-b", priority: 2, requested_flow_lpm: 80},
        %{zone_id: "zone-a", priority: 1, requested_flow_lpm: 60}
      ]
    }

    assert {:ok, result} = Distribution.plan(attrs)
    assert Enum.at(result.allocations, 0).zone_id == "zone-a"
    assert Enum.at(result.allocations, 0).proposed_supply_flow_lpm == 60
    assert Enum.at(result.allocations, 1).proposed_supply_flow_lpm == 40
    assert result.execution_enabled == false
  end

  test "recycling restricts target classes and keeps suitability unverified" do
    attrs = %{
      stream_id: "greywater-1",
      input_volume_l: 200,
      proposed_recovered_volume_l: 150,
      target_use: "non_potable_irrigation",
      treatment_stage_ids: ["treatment-1"],
      quality_observation_ids: ["sample-1"]
    }

    assert {:ok, result} = Recycling.plan(attrs)
    assert result.suitability_status == :not_established
    assert result.reuse_quality_status == :unverified
    assert result.execution_enabled == false
    assert {:error, :recovered_volume_exceeds_input} =
             Recycling.plan(%{attrs | proposed_recovered_volume_l: 201})
  end

  test "flow integration accepts only the declared five-stage order" do
    stages = Enum.map(
      [:collection, :purification, :storage, :distribution, :recycling],
      &%{workstream: &1}
    )

    assert {:ok, route} = Flow.connect(stages)
    assert route.physical_dispatch == :disabled
    assert {:error, {:invalid_stage_order, _}} =
             Flow.connect(Enum.reverse(stages))
  end
end
