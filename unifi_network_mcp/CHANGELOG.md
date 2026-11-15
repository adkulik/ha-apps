# Changelog

## 0.45.2

- Update to `ghcr.io/sirkirby/unifi-network-mcp:0.45.2`.
- Client list keeps live status with `include_offline`, finds offline clients by IP, and shows DHCP reservations (`fixed_ip`).
- Client details report whether the local DNS record and fixed-AP lock are enabled.
- Radio summaries show the transmit power mode and the power actually in use.

## 0.45.1

- First release: Home Assistant wrapper for `ghcr.io/sirkirby/unifi-network-mcp:0.45.1`.
- Streamable HTTP on the internal app network only (port 3000, `/mcp`), no host ports.
- Read-only by default (create/update/delete off), confirm mode for allowed changes.
- Host-header allowlist built from the container hostname and the configured public hostnames.
