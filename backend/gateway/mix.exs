defmodule Gateway.MixProject do
  use Mix.Project

  def project do
    [
      app: :gateway,
      version: "0.1.0",
      elixir: "~> 1.15",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {Gateway.Application, []}
    ]
  end

  defp deps do
    [
      # {:cowboy, "~> 2.9"},
      # {:plug, "~> 1.14"},
      # {:plug_cowboy, "~> 2.6"},
      # {:jason, "~> 1.4"}
    ]
  end
end
