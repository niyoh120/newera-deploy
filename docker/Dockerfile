# syntax=docker/dockerfile:1
# Builds 3D New Era AI (upstream: leandrodaf/3d-new-era-ai) for a headless homelab:
#   target "runtime" -> newera (headless MCP server) + newera-relay on debian-slim
#   target "web"     -> caddy serving the browser editor WASM + /files/ project alias

FROM rust:1.95-slim-bookworm AS build

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      pkg-config make \
      libxkbcommon-dev libwayland-dev libx11-dev \
      libxcursor-dev libxrandr-dev libxi-dev \
 && rm -rf /var/lib/apt/lists/* \
 && rustup target add wasm32-unknown-unknown \
 && cargo install wasm-bindgen-cli --version 0.2.128 --locked

WORKDIR /src
COPY Cargo.toml Cargo.lock ./
COPY crates ./crates
COPY web ./web

# Native binaries (aarch64 natively on GH arm runners, x64 on x64 runners)
RUN cargo build --release --locked -p newera -p newera-relay

# Browser editor + viewer WASM (same steps as upstream `make web web-editor`)
RUN cargo build --release --locked -p newera-web --target wasm32-unknown-unknown \
 && cp target/wasm32-unknown-unknown/release/newera_web.wasm web/ \
 && cargo build --release --locked -p newera-editor-web --target wasm32-unknown-unknown \
 && wasm-bindgen --target web --no-typescript --out-dir web/editor/pkg \
      target/wasm32-unknown-unknown/release/newera_editor_web.wasm

FROM debian:bookworm-slim AS runtime
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY --from=build /src/target/release/newera /usr/local/bin/newera
COPY --from=build /src/target/release/newera-relay /usr/local/bin/newera-relay
ENV NEWERA_TELEMETRY=0
EXPOSE 7878
CMD ["newera", "serve"]

FROM caddy:2-alpine AS web
COPY --from=build /src/web /srv/web
# Default the browser editor's MCP relay to the co-located relay on this same
# origin instead of the upstream hosted service, so /editor/ works with no params.
RUN sed -i 's#?? "https://mcp.3dneweraai.com"#?? window.location.origin#' /srv/web/editor/index.html \
 && grep -q 'window.location.origin' /srv/web/editor/index.html
COPY Caddyfile /etc/caddy/Caddyfile
