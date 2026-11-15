# UniFi Network MCP

Runs the [UniFi Network MCP server](https://github.com/sirkirby/unifi-mcp)
by sirkirby as a Home Assistant app, so an AI assistant (e.g. Claude) can
query and - only if you allow it - change your UniFi network.

This app is a thin wrapper around the upstream image
`ghcr.io/sirkirby/unifi-network-mcp`; all MCP functionality comes from there.

## How it is reached

The server listens with Streamable HTTP on port `3000`, path `/mcp`, **only on
the internal Home Assistant app network**. No port is published on the host or
the LAN. Expose it to a remote client through an authenticated tunnel, for
example the Cloudflared app plus a Cloudflare Access application with OAuth:

```
Claude -> Cloudflare Access (login) -> Cloudflare Tunnel -> http://<app-hostname>:3000/mcp
```

The app's internal hostname is printed in the log at start-up
(`MCP endpoint: http://...:3000/mcp`). Add the public hostname you use to
**Allowed hostnames**.

The upstream HTTP transport has no login of its own. Never publish it without
an authenticating proxy in front.

## Configuration

1. In UniFi, create a dedicated **local** admin account for this app
   (not a Ubiquiti SSO account). A read-only role is enough for read-only use.
2. Enter the console address, username and password.
3. Start the app and check the log.

### Permissions

By default the server is **read-only**: `allow_create`, `allow_update` and
`allow_delete` are off, so every mutating tool is refused on the server side.

Turning one on allows that kind of change for every category. With
`permission_mode: confirm` (default) each change still needs a preview and an
explicit confirmation call.

For finer control keep the three switches off and add per-category gates to
**Extra environment variables**, for example:

```
UNIFI_POLICY_NETWORK_DNS_CREATE=true
UNIFI_POLICY_NETWORK_DNS_UPDATE=true
```

See the upstream [permissions documentation](https://github.com/sirkirby/unifi-mcp/blob/main/apps/network/docs/permissions.md)
for all categories.

## Updating

The app version follows the upstream server version. A new app version
rebuilds the wrapper on top of the matching upstream image.

## Support

If this Home Assistant packaging is useful to you, you can support my work:

[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-sponsor-EA4AAA?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/adkulik)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-support-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/adkulik)

The UniFi Network MCP server itself is the work of
[sirkirby](https://github.com/sirkirby/unifi-mcp); please consider supporting
the upstream project too.
