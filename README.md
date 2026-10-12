# newera-deploy

Build & deployment glue for [leandrodaf/3d-new-era-ai](https://github.com/leandrodaf/3d-new-era-ai)
on a headless ARM64 homelab node (Coolify, kr-3).

- `docker/Dockerfile` — multi-target build: `runtime` (newera headless MCP + newera-relay) and
  `web` (Caddy serving the browser editor WASM, plus a read-only `/files/` alias for project handoff).
- `.github/workflows/build.yml` — builds natively on a free GitHub ARM64 runner and pushes to GHCR:
  `ghcr.io/niyoh120/newera` + `ghcr.io/niyoh120/newera-web`. Trigger manually
  (`workflow_dispatch`), set `upstream_ref` to a tag to pin a version.
- `compose.yaml` — the Coolify stack: editor / relay / headless serve.
  Requires `NEWERA_TOKEN` in the Coolify app environment.

Upstream is checked out fresh at build time (no fork needed); Caddyfile is injected into the context.
