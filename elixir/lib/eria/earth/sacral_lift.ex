defmodule Eria.Earth.SacralLift do
  @moduledoc """
  Consent-gated descriptive pattern analysis under the Earth domain.
  "Subliminal" is treated as a research label only: this module does not
  create hidden messages, deliver covert stimuli, infer subconscious states,
  or attempt to influence behavior.

  It validates a proposed cue record and preserves source lineage for human
  review. It performs no stimulus generation or external dispatch.
  """

  @cue_types ~w(environmental_pattern symbolic_pattern ambient_signal)

  def analyze(attrs) when is_map(attrs) do
    with true <- Map.get(attrs, :consent) == true || {:error, :explicit_consent_required},
         {:ok, cue_id} <- required_string(attrs, :cue_id),
         {:ok, cue_type} <- required_string(attrs, :cue_type),
         true <- cue_type in @cue_types || {:error, :unsupported_cue_type},
         {:ok, pattern} <- required_string(attrs, :pattern),
         {:ok, purpose} <- required_string(attrs, :consent_purpose),
         {:ok, source_ids} <- source_ids(Map.get(attrs, :source_observation_ids)) do
      {:ok, %{
        engine: "Sacral-Lift",
        domain: :earth,
        engine_role: :descriptive_cue_pattern_analysis,
        cue_id: cue_id,
        cue_type: cue_type,
        pattern: pattern,
        consent_purpose: purpose,
        source_observation_ids: source_ids,
        status: :eligible_for_human_review,
        interpretation: :not_generated,
        subconscious_state_inference: :disabled,
        covert_stimulus_generation: :disabled,
        behavioral_influence: :disabled,
        external_dispatch: :disabled,
        execution_enabled: false
      }}
    else
      {:error, reason} -> {:error, reason}
      false -> {:error, :invalid_cue_record}
    end
  end

  def analyze(_), do: {:error, :attributes_must_be_a_map}

  defp required_string(attrs, key) do
    case Map.get(attrs, key) do
      value when is_binary(value) and byte_size(value) > 0 -> {:ok, value}
      _ -> {:error, {:missing_or_invalid, key}}
    end
  end

  defp source_ids(ids) when is_list(ids) and ids != [] do
    if Enum.all?(ids, &(is_binary(&1) and &1 != "")) do
      {:ok, Enum.uniq(ids)}
    else
      {:error, :invalid_source_observation_ids}
    end
  end

  defp source_ids(_), do: {:error, :source_observation_ids_required}
end
