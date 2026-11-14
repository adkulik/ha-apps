# Changelog

## 0.45.1

- First release: Home Assistant wrapper for `ghcr.io/sirkirby/unifi-network-mcp:0.45.1`.
- Streamable HTTP on the internal app network only (port 3000, `/mcp`), no host ports.
- Read-only by default (create/update/delete off), confirm mode for allowed changes.
- Host-header allowlist built from the container hostname and the configured public hostnames.
