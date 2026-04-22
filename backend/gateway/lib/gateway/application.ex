defmodule Gateway.Application do
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Children setup for Cowboy WebSocket server would go here
      # Plug.Cowboy.child_spec(...)
    ]

    opts = [strategy: :one_for_one, name: Gateway.Supervisor]

    require Logger
    Logger.info("Starting Elixir Gateway...")

    Supervisor.start_link(children, opts)
  end
end
