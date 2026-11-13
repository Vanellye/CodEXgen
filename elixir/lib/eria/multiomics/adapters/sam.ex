defmodule Eria.MultiOmics.Adapters.SAM do
  @moduledoc """
  Validates SAM text records. BAM/CRAM conversion is not performed by this
  parser; conversion execution is tracked as a separate, explicitly invoked
  ingestion stage. This module never launches external processes.
  """

  @default_max_bytes 50_000_000
  @default_max_records 1_000_000

  def decode(input, opts \\ [])

  def decode(binary, opts) when is_binary(binary) do
    max_bytes = Keyword.get(opts, :max_bytes, @default_max_bytes)
    max_records = Keyword.get(opts, :max_records, @default_max_records)

    cond do
      byte_size(binary) > max_bytes ->
        {:error, :input_too_large}

      true ->
        lines = String.split(binary, "\n", trim: true)
        headers = Enum.filter(lines, &String.starts_with?(&1, "@"))
        records = Enum.reject(lines, &String.starts_with?(&1, "@"))

        cond do
          length(records) > max_records ->
            {:error, :record_limit_exceeded}

          true ->
            parse_records(records, [], 1, headers, binary)
        end
    end
  end

  def decode(_, _), do: {:error, :input_must_be_binary}

  def conversion_plan(:bam, input_path, output_path)
      when is_binary(input_path) and is_binary(output_path) do
    {:ok,
     %{
       executable: "samtools",
       argv: ["view", "-h", "-o", output_path, input_path],
       shell: false,
       execution: :not_performed
     }}
  end

  def conversion_plan(:cram, input_path, output_path, reference_path)
      when is_binary(input_path) and is_binary(output_path) and is_binary(reference_path) do
    {:ok,
     %{
       executable: "samtools",
       argv: ["view", "-T", reference_path, "-h", "-o", output_path, input_path],
       shell: false,
       execution: :not_performed
     }}
  end

  def conversion_plan(:cram, _input, _output, _reference),
    do: {:error, :cram_reference_required}

  def conversion_plan(_, _, _), do: {:error, :unsupported_alignment_format}
  def conversion_plan(_, _, _, _), do: {:error, :unsupported_alignment_format}

  defp parse_records([], acc, _index, headers, source) do
    {:ok,
     %{
       format: :sam,
       headers: headers,
       records: Enum.reverse(acc),
       source_sha256: digest(source),
       counts: %{records: length(acc)}
     }}
  end

  defp parse_records([line | rest], acc, index, headers, source) do
    case String.split(line, "\t") do
      [qname, flag, rname, pos, mapq, cigar, rnext, pnext, tlen, sequence, quality | tags] ->
        with {flag_value, ""} <- Integer.parse(flag),
             {position, ""} <- Integer.parse(pos),
             {mapping_quality, ""} <- Integer.parse(mapq),
             true <- flag_value >= 0 and position >= 0 and mapping_quality >= 0 do
          record = %{
            qname: qname,
            flag: flag_value,
            rname: rname,
            position: position,
            mapping_quality: mapping_quality,
            cigar: cigar,
            rnext: rnext,
            pnext: pnext,
            template_length: tlen,
            sequence: sequence,
            quality: quality,
            tags: tags
          }

          parse_records(rest, [record | acc], index + 1, headers, source)
        else
          _ -> {:error, {:invalid_sam_numeric_field, index}}
        end

      _ ->
        {:error, {:invalid_sam_columns, index}}
    end
  end

  defp digest(value), do: :crypto.hash(:sha256, value) |> Base.encode16(case: :lower)
end
