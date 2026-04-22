FROM elixir:1.15-alpine

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache build-base npm git

# Install hex + rebar
RUN mix local.hex --force && \
    mix local.rebar --force

COPY mix.exs ./
# RUN mix deps.get

COPY lib ./lib

# Compile the project
# RUN mix compile

CMD ["mix", "run", "--no-halt"]
