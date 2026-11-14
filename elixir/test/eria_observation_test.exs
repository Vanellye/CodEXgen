defmodule EriaObservationTest do
  use ExUnit.Case, async: true

  alias Eria.{CodeLanguage, Interpreter, Observation, Quality}

  @line "OBSERVE|plant|plot-7|photosynthesis_rate|12.5|umol_m-2_s-1|gas_exchange|2026-11-13T10:00:00Z|sensor-log-01|raw-sample-001"

  test "parses a source-linked observation without executing arbitrary code" do
    assert {:ok, [observation]} = CodeLanguage.parse(@line)
    assert observation.domain == "plant"
    assert observation.metric == "photosynthesis_rate"
    assert observation.value == 12.5
    assert byte_size(observation.raw_sha256) == 64
  end

  test "rejects unknown instructions" do
    assert {:error, %{line: 1, reason: :unknown_instruction}} =
      CodeLanguage.parse("EXEC|System.cmd|rm -rf /")
  end

  test "rejects unsupported domain and metric combinations" do
    attrs = %{
      domain: "animal", subject_id: "a-1", metric: "photosynthesis_rate",
      value: 1, unit: "unit", method: "method",
      observed_at: "2026-11-13T10:00:00Z", source: "source", raw_payload: "raw"
    }

    assert {:error, :unsupported_metric} = Observation.new(attrs)
  end

  test "quality check qualifies structurally complete observations" do
    assert {:ok, [observation]} = CodeLanguage.parse(@line)
    assert Quality.check(observation).status == :qualified
  end

  test "interpreter keeps observations separate from inferences" do
    assert {:ok, observations} = CodeLanguage.parse(@line)
    report = Interpreter.interpret(observations)

    assert report.counts.total == 1
    assert report.counts.qualified == 1
    assert report.inferences == []
    assert Enum.any?(report.interpretation_boundary, &String.contains?(&1, "No clinical diagnosis"))
  end

  test "rejects malformed timestamps" do
    bad = String.replace(@line, "2026-11-13T10:00:00Z", "not-a-date")
    assert {:error, %{reason: :invalid_observed_at}} = CodeLanguage.parse(bad)
  end
end
