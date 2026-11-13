defmodule Eria.MultiOmics.Adapters.SAM do
  @moduledoc """
  Validates SAM text records and provides an explicit file-ingestion entry
  point. Calling decode_file/2 for BAM or CRAM automatically invokes samtools
  with an argv list (never through a shell), validates the resulting SAM, and
  removes its temporary conversion file. CRAM requires a caller-supplied
  reference path. No background watcher or implicit file-presence trigger is
  installed.
  """

  @default_max_bytes 500_000_000
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

  @doc """
  Reads SAM directly or automatically converts BAM/CRAM to temporary SAM
  during this explicit call. Options: :reference_path (required for CRAM),
  :samtools_path, :max_input_bytes, :max_output_bytes, and :max_records.
  """
  def decode_file(path, opts \\ []) when is_binary(path) do
    max_input_bytes = Keyword.get(opts, :max_input_bytes, @default_max_bytes)

    with {:ok, stat} <- File.stat(path),
         true <- stat.type == :regular,
         true <- stat.size <= max_input_bytes,
         {:ok, source} <- File.read(path) do
      source_digest = digest(source)

      case String.downcase(Path.extname(path)) do
        ".sam" ->
          with {:ok, decoded} <-
                 decode(source,
                   max_bytes: max_input_bytes,
                   max_records: Keyword.get(opts, :max_records, @default_max_records)
                 ) do
            {:ok, Map.merge(decoded, %{source_format: :sam, source_sha256: source_digest})}
          end

        ".bam" ->
          convert_and_decode(:bam, path, source_digest, opts)

        ".cram" ->
          convert_and_decode(:cram, path, source_digest, opts)

        _ ->
          {:error, :unsupported_alignment_file_extension}
      end
    else
      false -> {:error, :input_file_invalid_or_too_large}
      {:error, reason} -> {:error, {:input_file_unavailable, reason}}
    end
  end

  def decode_file(_, _), do: {:error, :input_path_must_be_binary}

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

  defp convert_and_decode(format, input_path, source_digest, opts) do
    samtools = Keyword.get(opts, :samtools_path, "samtools")
    max_output_bytes = Keyword.get(opts, :max_output_bytes, @default_max_bytes)
    reference_path = Keyword.get(opts, :reference_path)

    args_result =
      case format do
        :bam ->
          {:ok, ["view", "-h"]}

        :cram when is_binary(reference_path) and reference_path != "" ->
          {:ok, ["view", "-T", reference_path, "-h"]}

        :cram ->
          {:error, :cram_reference_required}
      end

    with {:ok, args_prefix} <- args_result do
      temp_path =
        Path.join(
          System.tmp_dir!(),
          "eria-convert-#{:erlang.unique_integer([:positive, :monotonic])}.sam"
        )

      args = args_prefix ++ ["-o", temp_path, input_path]

      try do
        with {:ok, tool_version} <- samtools_version(samtools),
             {:ok, exit_status} <- execute_samtools(samtools, args),
             {:ok, stat} <- File.stat(temp_path),
             true <- stat.type == :regular and stat.size > 0 and stat.size <= max_output_bytes,
             {:ok, sam_text} <- File.read(temp_path),
             {:ok, decoded} <-
               decode(sam_text,
                 max_bytes: max_output_bytes,
                 max_records: Keyword.get(opts, :max_records, @default_max_records)
               ) do
          {:ok,
           Map.merge(decoded, %{
             source_format: format,
             source_sha256: source_digest,
             conversion: %{
               tool: Path.basename(samtools),
               tool_version: tool_version,
               exit_status: exit_status,
               output_sha256: digest(sam_text),
               output_bytes: stat.size
             }
           })}
        else
          false -> {:error, :converted_output_invalid_or_too_large}
          {:error, reason} -> {:error, reason}
        end
      after
        File.rm(temp_path)
      end
    end
  end

  defp samtools_version(executable) do
    try do
      case System.cmd(executable, ["--version"], stderr_to_stdout: true) do
        {output, 0} ->
          version = output |> String.split("\n", trim: true) |> List.first()
          {:ok, version || "unknown"}

        {_output, status} ->
          {:error, {:samtools_version_failed, status}}
      end
    rescue
      error in ErlangError -> {:error, {:samtools_unavailable, Exception.message(error)}}
    end
  end

  defp execute_samtools(executable, args) do
    try do
      case System.cmd(executable, args, stderr_to_stdout: true) do
        {_output, 0} ->
          {:ok, 0}

        {output, status} ->
          {:error, {:samtools_conversion_failed, status, String.slice(output, 0, 4000)}}
      end
    rescue
      error in ErlangError -> {:error, {:samtools_unavailable, Exception.message(error)}}
    end
  end

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
