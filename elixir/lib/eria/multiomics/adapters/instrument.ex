defmodule Eria.MultiOmics.Adapters.Instrument do
  @moduledoc """
  Vendor-neutral boundary for instrument exports. A vendor adapter is an
  explicitly supplied module implementing this behavior; no module names are
  dynamically created and no imported file is executed.
  """

  @callback vendor_id() :: String.t()
  @callback decode(binary(), keyword()) ::
              {:ok, [map()]} | {:error, term()}

  def decode_with(adapter, binary, opts \\ [])

  def decode_with(adapter, binary, opts)
      when is_atom(adapter) and is_binary(binary) and is_list(opts) do
    if Code.ensure_loaded?(adapter) and function_exported?(adapter, :vendor_id, 0)
       and function_exported?(adapter, :decode, 2) do
      case adapter.decode(binary, opts) do
        {:ok, records} when is_list(records) ->
          {:ok, %{vendor: adapter.vendor_id(), records: records,
                  source_sha256: digest(binary), execution: :data_only}}
        {:error, reason} -> {:error, reason}
        _ -> {:error, :adapter_returned_invalid_shape}
      end
    else
      {:error, :unregistered_or_invalid_adapter}
    end
  end

  def decode_with(_, _, _), do: {:error, :invalid_adapter_arguments}

  defp digest(value), do: :crypto.hash(:sha256, value) |> Base.encode16(case: :lower)
end
