defmodule EriaEarthSacralLiftTest do
  use ExUnit.Case, async: true

  alias Eria.{Earth, Observation}
  alias Eria.Earth.SacralLift

  @earth_attrs %{
    domain: "earth", subject_id: "plot-1", metric: "soil_moisture",
    value: 21.4, unit: "percent", method: "gravimetric",
    observed_at: "2026-11-13T10:00:00Z", source: "soil-log-1",
    raw_payload: "soil-sample-1"
  }

  @cue_attrs %{
    consent: true, cue_id: "cue-001", cue_type: "environmental_pattern",
    pattern: "user-submitted seasonal sound pattern",
    consent_purpose: "descriptive research review",
    source_observation_ids: ["obs-earth-001"]
  }

  test "Earth is a supported observation domain with mapped subdomains" do
    assert "earth" in Observation.domains()
    assert {:ok, observation} = Observation.new(@earth_attrs)
    assert {:ok, result} = Earth.validate_observation(observation)
    assert result.domain == :earth
    assert result.subdomain == :land
  end

  test "Earth maps water, air, life and climate metrics" do
    assert {:ok, :water} = Earth.subdomain_for_metric("surface_water_level")
    assert {:ok, :air} = Earth.subdomain_for_metric("air_temperature")
    assert {:ok, :life} = Earth.subdomain_for_metric("biodiversity_index")
    assert {:ok, :climate} = Earth.subdomain_for_metric("carbon_flux")
  end

  test "Earth rejects an unsupported metric" do
    assert {:error, :unsupported_metric} = Observation.new(%{@earth_attrs | metric: "unknown_metric"})
  end

  test "Sacral-Lift creates a consented, source-linked review record only" do
    assert {:ok, result} = SacralLift.analyze(@cue_attrs)
    assert result.domain == :earth
    assert result.engine_role == :descriptive_cue_pattern_analysis
    assert result.status == :eligible_for_human_review
    assert result.interpretation == :not_generated
    assert result.subconscious_state_inference == :disabled
    assert result.covert_stimulus_generation == :disabled
    assert result.behavioral_influence == :disabled
    assert result.external_dispatch == :disabled
    assert result.execution_enabled == false
  end

  test "Sacral-Lift fails closed without explicit consent" do
    assert {:error, :explicit_consent_required} = SacralLift.analyze(%{@cue_attrs | consent: false})
  end

  test "Sacral-Lift requires source lineage and an allowed cue type" do
    assert {:error, :source_observation_ids_required} = SacralLift.analyze(%{@cue_attrs | source_observation_ids: []})
    assert {:error, :unsupported_cue_type} = SacralLift.analyze(%{@cue_attrs | cue_type: "covert_message"})
  end
end
