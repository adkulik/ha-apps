# Changelog

## 0.53.0

- Update to `ghcr.io/sirkirby/unifi-network-mcp:0.53.0`.
- Upstream changes: https://github.com/sirkirby/unifi-mcp/releases/tag/network/v0.53.0

## 0.50.3.1

- Wrapper-only release on `ghcr.io/sirkirby/unifi-network-mcp:0.50.3`, which brings the trusted-networks support (sirkirby/unifi-mcp#1110).
- New **Access token** option: clients must send `Authorization: Bearer <token>`.
- New **Trusted networks** option: networks whose requests skip the token because a proxy there already logs callers in (e.g. the Cloudflared app). Needs a server version that supports it; older ones make the app refuse to start with an explanation.
- **Breaking:** with a host port set, the app now refuses to start without an access token, so the server is never open on the network without a login. Set a token, or clear the host port.
- The documentation describes the setups for a tunnel app, LAN, VPN (WireGuard, Tailscale) and a mix, and recommends a Network-only UniFi account instead of a Super Admin.

## 0.50.3

- Update to `ghcr.io/sirkirby/unifi-network-mcp:0.50.3`.
- Upstream changes: https://github.com/sirkirby/unifi-mcp/releases/tag/network/v0.50.3

## 0.50.2

- Update to `ghcr.io/sirkirby/unifi-network-mcp:0.50.2`.
- Upstream changes: https://github.com/sirkirby/unifi-mcp/releases/tag/network/v0.50.2

## 0.50.1

- Update to `ghcr.io/sirkirby/unifi-network-mcp:0.50.1`.
- Upstream changes: https://github.com/sirkirby/unifi-mcp/releases/tag/network/v0.50.1

## 0.50.0

- Update to `ghcr.io/sirkirby/unifi-network-mcp:0.50.0`.
- Upstream changes: https://github.com/sirkirby/unifi-mcp/releases/tag/network/v0.50.0

## 0.48.1

- Update to `ghcr.io/sirkirby/unifi-network-mcp:0.48.1`.
- Upstream changes: https://github.com/sirkirby/unifi-mcp/releases/tag/network/v0.48.1

## 0.48.0

- Update to `ghcr.io/sirkirby/unifi-network-mcp:0.48.0`.
- Upstream changes: https://github.com/sirkirby/unifi-mcp/releases/tag/network/v0.48.0

## 0.46.0

- Update to `ghcr.io/sirkirby/unifi-network-mcp:0.46.0`.
- Upstream changes: https://github.com/sirkirby/unifi-mcp/releases/tag/network/v0.46.0

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
