defmodule Eria.Evidence.Graph do
  @moduledoc """
  Links derived research findings to the exact multi-omics records they cite.
  Findings are data, not executable instructions or established diagnoses.
  """

  def build(records, findings) when is_list(records) and is_list(findings) do
    record_ids = records |> Enum.map(& &1.id) |> MapSet.new()

    Enum.reduce_while(findings, {:ok, []}, fn finding, {:ok, acc} ->
      case validate_finding(finding, record_ids) do
        {:ok, normalized} -> {:cont, {:ok, [normalized | acc]}}
        {:error, reason} -> {:halt, {:error, reason}}
      end
    end)
    |> case do
      {:ok, validated} ->
        validated = Enum.reverse(validated)
        edges = Enum.flat_map(validated, fn finding ->
          Enum.map(finding.source_record_ids, fn record_id ->
            %{from: record_id, to: finding.id, relation: "supports_or_informs"}
          end)
        end)
        {:ok, %{record_ids: MapSet.to_list(record_ids), findings: validated, edges: edges}}
      error -> error
    end
  end

  def build(_, _), do: {:error, :records_and_findings_must_be_lists}

  defp validate_finding(finding, record_ids) when is_map(finding) do
    id = Map.get(finding, :id)
    statement = Map.get(finding, :statement)
    source_ids = Map.get(finding, :source_record_ids)
    method = Map.get(finding, :method)
    uncertainty = Map.get(finding, :uncertainty)

    cond do
      not nonempty_string?(id) -> {:error, :finding_id_required}
      not nonempty_string?(statement) -> {:error, :finding_statement_required}
      not nonempty_string?(method) -> {:error, :finding_method_required}
      not nonempty_string?(uncertainty) -> {:error, :finding_uncertainty_required}
      not (is_list(source_ids) and source_ids != []) -> {:error, :finding_sources_required}
      not Enum.all?(source_ids, &MapSet.member?(record_ids, &1)) -> {:error, :orphan_finding_source}
      true ->
        {:ok, %{id: id, statement: statement, source_record_ids: source_ids,
                method: method, uncertainty: uncertainty, status: :research_hypothesis}}
    end
  end

  defp validate_finding(_, _), do: {:error, :finding_must_be_a_map}
  defp nonempty_string?(value), do: is_binary(value) and byte_size(value) > 0
end
