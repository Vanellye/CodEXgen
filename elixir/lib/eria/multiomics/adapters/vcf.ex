defmodule Eria.MultiOmics.Adapters.VCF do
  @moduledoc """
  Conservative VCF text validator. Retains headers and variant fields without
  annotation, pathogenicity interpretation, or clinical classification.
  """

  @default_max_bytes 50_000_000
  @default_max_records 1_000_000

  def decode(input, opts \\ [])

  def decode(binary, opts) when is_binary(binary) do
    max_bytes = Keyword.get(opts, :max_bytes, @default_max_bytes)
    max_records = Keyword.get(opts, :max_records, @default_max_records)

    cond do
      byte_size(binary) > max_bytes -> {:error, :input_too_large}
      true ->
        lines = String.split(binary, "\n", trim: true)
        meta = Enum.filter(lines, &String.starts_with?(&1, "##"))
        column_header = Enum.find(lines, &String.starts_with?(&1, "#CHROM\t"))

        if is_nil(column_header) do
          {:error, :missing_vcf_column_header}
        else
          data = Enum.reject(lines, &String.starts_with?(&1, "#"))

          cond do
            length(data) > max_records -> {:error, :record_limit_exceeded}
            true -> parse_records(data, [], 1, meta, column_header, binary)
          end
        end
    end
  end

  def decode(_, _), do: {:error, :input_must_be_binary}

  defp parse_records([], acc, _index, meta, header, source) do
    {:ok, %{format: :vcf, metadata: meta, column_header: header,
            records: Enum.reverse(acc), source_sha256: digest(source),
            counts: %{records: length(acc)}}}
  end

  defp parse_records([line | rest], acc, index, meta, header, source) do
    fields = String.split(line, "\t")

    case fields do
      [chrom, pos, id, ref, alt, qual, filter, info | sample_fields]
      when chrom != "" and ref != "" and alt != "" ->
        with {position, ""} <- Integer.parse(pos),
             true <- position > 0 do
          record = %{chrom: chrom, position: position, id: id, ref: ref,
                     alt: String.split(alt, ","), quality: qual, filter: filter,
                     info: info, sample_fields: sample_fields}
          parse_records(rest, [record | acc], index + 1, meta, header, source)
        else
          _ -> {:error, {:invalid_vcf_position, index}}
        end
      _ ->
        {:error, {:invalid_vcf_columns, index}}
    end
  end

  defp digest(value), do: :crypto.hash(:sha256, value) |> Base.encode16(case: :lower)
end
