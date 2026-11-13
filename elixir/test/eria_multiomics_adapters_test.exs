defmodule Eria.MultiOmics.Adapters.InstrumentFixture do
  @behaviour Eria.MultiOmics.Adapters.Instrument
  def vendor_id, do: "fixture-vendor"
  def decode("ok", _opts), do: {:ok, [%{feature: "F1", value: 1}]}
  def decode(_, _opts), do: {:error, :fixture_rejected}
end

defmodule EriaMultiOmicsAdaptersTest do
  use ExUnit.Case, async: true

  alias Eria.MultiOmics.Adapters.{FASTQ, Instrument, SAM, VCF}

  test "FASTQ validates records and preserves source fingerprint" do
    input = "@read-1\nACGT\n+\n!!!!\n"
    assert {:ok, result} = FASTQ.decode(input)
    assert result.counts.records == 1
    assert hd(result.records).sequence_length == 4
    assert byte_size(result.source_sha256) == 64
  end

  test "FASTQ rejects mismatched sequence and quality lengths" do
    assert {:error, {:sequence_quality_length_mismatch, 1}} =
             FASTQ.decode("@read-1\nACGT\n+\n!!!\n")
  end

  test "FASTQ enforces input bounds" do
    assert {:error, :input_too_large} = FASTQ.decode("@r\nA\n+\n!\n", max_bytes: 2)
  end

  test "VCF retains header and parses coordinates without annotating variants" do
    input = "##fileformat=VCFv4.3\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\nchr1\t12\t.\tA\tG\t.\tPASS\t.\n"
    assert {:ok, result} = VCF.decode(input)
    assert result.counts.records == 1
    assert hd(result.records).position == 12
    assert hd(result.records).alt == ["G"]
  end

  test "VCF rejects malformed positions" do
    input = "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\nchr1\tzero\t.\tA\tG\t.\tPASS\t.\n"
    assert {:error, {:invalid_vcf_position, 1}} = VCF.decode(input)
  end

  test "SAM text adapter validates numeric alignment fields" do
    input = "@HD\tVN:1.6\nread-1\t0\tchr1\t10\t60\t4M\t*\t0\t0\tACGT\t!!!!\n"
    assert {:ok, result} = SAM.decode(input)
    assert result.counts.records == 1
    assert hd(result.records).position == 10
  end

  test "BAM and CRAM conversion plans remain argv-only descriptions" do
    assert {:ok, bam} = SAM.conversion_plan(:bam, "reads.bam", "reads.sam")
    assert bam.shell == false
    assert bam.execution == :not_performed
    assert {:ok, cram} = SAM.conversion_plan(:cram, "reads.cram", "reads.sam", "ref.fa")
    assert "ref.fa" in cram.argv
    assert {:error, :cram_reference_required} =
             SAM.conversion_plan(:cram, "reads.cram", "reads.sam", nil)
  end

  test "BAM decode_file automatically converts, validates, and fingerprints output" do
    dir = Path.join(System.tmp_dir!(), "eria-bam-test-#{System.unique_integer([:positive])}")
    File.mkdir_p!(dir)
    on_exit(fn -> File.rm_rf!(dir) end)

    sam = Path.join(dir, "reads.sam")
    bam = Path.join(dir, "reads.bam")
    File.write!(sam, "@HD\tVN:1.6\n@SQ\tSN:chr1\tLN:100\nread-1\t0\tchr1\t10\t60\t4M\t*\t0\t0\tACGT\t!!!!\n")
    {_, 0} = System.cmd("samtools", ["view", "-b", "-o", bam, sam])

    assert {:ok, result} = SAM.decode_file(bam)
    assert result.source_format == :bam
    assert result.counts.records == 1
    assert hd(result.records).position == 10
    assert result.conversion.exit_status == 0
    assert byte_size(result.conversion.output_sha256) == 64
  end

  test "CRAM decode_file requires an explicit reference and converts automatically" do
    dir = Path.join(System.tmp_dir!(), "eria-cram-test-#{System.unique_integer([:positive])}")
    File.mkdir_p!(dir)
    on_exit(fn -> File.rm_rf!(dir) end)

    reference = Path.join(dir, "ref.fa")
    sam = Path.join(dir, "reads.sam")
    cram = Path.join(dir, "reads.cram")
    File.write!(reference, ">chr1\n" <> String.duplicate("A", 100) <> "\n")
    {_, 0} = System.cmd("samtools", ["faidx", reference])
    File.write!(sam, "@HD\tVN:1.6\n@SQ\tSN:chr1\tLN:100\nread-1\t0\tchr1\t10\t60\t4M\t*\t0\t0\tAAAA\t!!!!\n")
    {_, 0} = System.cmd("samtools", ["view", "-C", "-T", reference, "-o", cram, sam])

    assert {:error, :cram_reference_required} = SAM.decode_file(cram)
    assert {:ok, result} = SAM.decode_file(cram, reference_path: reference)
    assert result.source_format == :cram
    assert result.counts.records == 1
    assert hd(result.records).position == 10
    assert result.conversion.exit_status == 0
  end

  test "vendor adapter returns normalized records and source digest" do
    assert {:ok, result} = Instrument.decode_with(Eria.MultiOmics.Adapters.InstrumentFixture, "ok")
    assert result.vendor == "fixture-vendor"
    assert result.records == [%{feature: "F1", value: 1}]
    assert {:error, :fixture_rejected} =
             Instrument.decode_with(Eria.MultiOmics.Adapters.InstrumentFixture, "bad")
  end

  test "instrument adapter rejects unregistered module shape" do
    assert {:error, :unregistered_or_invalid_adapter} = Instrument.decode_with(String, "input")
  end
end
