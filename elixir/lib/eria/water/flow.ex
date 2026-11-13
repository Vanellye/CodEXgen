defmodule Eria.Water.Flow do
  @moduledoc """
  Validates the declared handoff order across independent water workstreams.
  It records a proposed logical route only; it does not dispatch commands.
  """

  @ordered_stages [:collection, :purification, :storage, :distribution, :recycling]

  def connect(stage_records) when is_list(stage_records) do
    names = Enum.map(stage_records, fn
      %{workstream: stage} when is_atom(stage) -> Atom.to_string(stage)
      %{workstream: stage} when is_binary(stage) -> stage
      _ -> nil
    end)

    if names == Enum.map(@ordered_stages, &Atom.to_string/1) do
      {:ok,
       %{
         workstream: :integration,
         route: @ordered_stages,
         status: :logical_route_validated,
         execution_enabled: false,
         physical_dispatch: :disabled
       }}
    else
      {:error, {:invalid_stage_order, @ordered_stages}}
    end
  end

  def connect(_), do: {:error, :stage_records_must_be_a_list}
end
