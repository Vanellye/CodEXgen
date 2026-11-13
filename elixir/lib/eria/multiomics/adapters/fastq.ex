defmodule Eria.MultiOmics.Adapters.FASTQ do
  @moduledoc """
  Structural FASTQ reader. Validates four-line records and sequence/quality
  lengths; it does not assess base-call quality or biological validity.
  """

  @default_max_bytes 50_000_000
  @default_max_records 1_000_000

  def decode(binary, opts \\ []) when is_binary(binary) do
    max_bytes = Keyword.get(opts, :max_bytes, @default_max_bytes)
    max_records = Keyword.get(opts, :max_records, @default_max_records)

    cond do
      byte_size(binary) > max_bytes ->
        {:error, :input_too_large}
      true ->
        lines = binary |> String.split("\n", trim: false) |> Enum.map(&String.trim_trailing(&1, "\r"))
        lines = if List.last(lines) == "", do: Enum.drop(lines, -1), else: lines

        if rem(length(lines), 4) != 0 do
          {:error, :incomplete_fastq_record}
        else
          chunks = Enum.chunk_every(lines, 4)

          cond do
            length(chunks) > max_records -> {:error, :record_limit_exceeded}
            true -> validate_records(chunks, [], 1, binary)
          end
        end
    end
  end

  def decode(_, _), do: {:error, :input_must_be_binary}

  defp validate_records([], acc, _index, source) do
    {:ok, %{format: :fastq, records: Enum.reverse(acc), source_sha256: digest(source),
            counts: %{records: length(acc)}}}
  end

  defp validate_records([[header, sequence, plus, quality] | rest], acc, index, source) do
    cond do
      not String.starts_with?(header, "@") or byte_size(header) < 2 ->
        {:error, {:invalid_header, index}}
      sequence == "" ->
        {:error, {:empty_sequence, index}}
      not String.starts_with?(plus, "+") ->
        {:error, {:invalid_plus_line, index}}
      byte_size(sequence) != byte_size(quality) ->
        {:error, {:sequence_quality_length_mismatch, index}}
      true ->
        record = %{index: index, header: header, sequence_length: byte_size(sequence),
                   sequence_sha256: digest(sequence), quality_length: byte_size(quality)}
        validate_records(rest, [record | acc], index + 1, source)
    end
  end

  defp digest(value), do: :crypto.hash(:sha256, value) |> Base.encode16(case: :lower)
end
