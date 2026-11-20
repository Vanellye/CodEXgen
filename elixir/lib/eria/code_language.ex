defmodule Eria.CodeLanguage do
  @moduledoc """
  Parses the deliberately small, non-executable ERIA observation language.

  Grammar (one record per line):
  OBSERVE|domain|subject_id|metric|value|unit|method|ISO8601_timestamp|source|raw_payload

  This parser does not evaluate Elixir, shell, SQL, or arbitrary expressions.
  """

  alias Eria.Observation

  @record_fields 10

  def parse(input) when is_binary(input) do
    input
    |> String.split(~r/\r?\n/, trim: true)
    |> Enum.with_index(1)
    |> Enum.reduce({:ok, []}, fn {line, line_number}, {:ok, records} ->
      case parse_line(line) do
        {:ok, record} -> {:ok, [record | records]}
        {:error, reason} -> {:error, %{line: line_number, reason: reason}}
      end
    end)
    |> case do
      {:ok, records} -> {:ok, Enum.reverse(records)}
      error -> error
    end
  end

  def parse(_), do: {:error, :input_must_be_text}

  defp parse_line(line) do
    fields = String.split(line, "|", parts: @record_fields)

    case fields do
      ["OBSERVE", domain, subject_id, metric, value, unit, method, observed_at, source, raw_payload]
      when length(fields) == @record_fields ->
        Observation.new(%{
          domain: domain,
          subject_id: subject_id,
          metric: metric,
          value: value,
          unit: unit,
          method: method,
          observed_at: observed_at,
          source: source,
          raw_payload: raw_payload
        })

      ["OBSERVE" | _] -> {:error, :wrong_field_count}
      _ -> {:error, :unknown_instruction}
    end
  end
end
