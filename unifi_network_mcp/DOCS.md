# UniFi Network MCP

Runs the [UniFi Network MCP server](https://github.com/sirkirby/unifi-mcp)
by sirkirby as a Home Assistant app, so an AI assistant (e.g. Claude) can
query and - only if you allow it - change your UniFi network.

This app is a thin wrapper around the upstream image
`ghcr.io/sirkirby/unifi-network-mcp`; all MCP functionality comes from there.

## How it is reached

The server speaks Streamable HTTP on port `3000`, path `/mcp`. The upstream
server has no login of its own; this app adds two settings that control who
may call it:

- **Access token** - clients must send `Authorization: Bearer <token>`.
- **Trusted networks** - networks whose requests skip the token, because a
  proxy there has already logged the caller in.

By default no host port is published: only other apps on the internal Home
Assistant network can reach the server. If you set a host port, the app
**refuses to start without an access token**, so the server is never open on
your network without a login.

Pick the setup that matches how you reach Home Assistant:

| How you connect | Who logs callers in | Host port | Access token | Trusted networks |
|---|---|---|---|---|
| Tunnel app with its own login (e.g. Cloudflared + Cloudflare Access) | the tunnel | empty | optional | the tunnel app's network, if you set a token |
| LAN | the token | set | **required** | empty |
| VPN to your LAN (WireGuard, Tailscale subnet router, the UniFi VPN) | the VPN and the token | set | **required** | empty |
| Both a tunnel and direct LAN/VPN clients | tunnel or token | set | **required** | the tunnel app's network |

Home Assistant Cloud (Nabu Casa) only forwards the Home Assistant interface
itself, not app ports, so it cannot be used to reach this server.

### Tunnel app (e.g. Cloudflare)

```
Claude -> Cloudflare Access (login) -> Cloudflare Tunnel -> http://<app-hostname>:3000/mcp
```

The app's internal hostname is printed in the log at start-up
(`MCP endpoint: http://...:3000/mcp`). Add the public hostname you use (for
example `unifi-mcp.example.com`) to **Allowed hostnames**; requests through a
tunnel are rejected until you do. Never expose the tunnel hostname without the
tunnel's own login in front.

### LAN or VPN

1. Set an **Access token** (at least 32 characters; `openssl rand -hex 32`
   prints a good one).
2. In the app's **Network** section, enter a host port for `3000/tcp`
   (e.g. `3000`) and restart the app.
3. Add the Home Assistant IP address (e.g. `192.168.1.10`) to
   **Allowed hostnames**. If the host port is not `3000`, add `IP:port` too.
   For a VPN that reaches Home Assistant at another address (for example its
   Tailscale IP), add that address as well.
4. Point the client to `http://<home-assistant-ip>:<port>/mcp` and send the
   token, for example:

   Claude Code:

   ```
   claude mcp add --transport http unifi http://192.168.1.10:3000/mcp --header "Authorization: Bearer <token>"
   ```

   VS Code (`mcp.json`):

   ```json
   {
     "servers": {
       "unifi": {
         "type": "http",
         "url": "http://192.168.1.10:3000/mcp",
         "headers": { "Authorization": "Bearer ${input:unifi-token}" }
       }
     },
     "inputs": [
       { "id": "unifi-token", "type": "promptString", "description": "UniFi MCP token", "password": true }
     ]
   }
   ```

The port speaks plain HTTP, so the token is not encrypted on the way. A VPN
(WireGuard, Tailscale) encrypts it for you; on a plain LAN, anyone who can
watch the traffic could read it. Use this port only on a network you trust,
or reach the server through a VPN or tunnel.

### Tunnel and direct clients together

A tunnel that logs callers in (for example Cloudflare Access with OAuth for
Claude) cannot add this app's token. List the network the tunnel app connects
from in **Trusted networks** and its requests skip the token, while LAN and
VPN clients still need it. For the Cloudflared app on Home Assistant OS this
is the internal app network, normally `172.30.32.0/23`; the server log shows
the address requests arrive from.

Only list networks where every client is that authenticating proxy. Never
list your LAN or VPN range: that would turn the token off for it. Trusted
networks need a server version that supports them; with an older one the app
refuses to start and says so in the log.

## Configuration

1. In UniFi, create a dedicated **local** account for this app (not a
   Ubiquiti SSO account), with the smallest role that fits: access to the
   **Network** application only, and **View Only** if you keep the app
   read-only. Do not use a Super Admin account: the app's permission switches
   limit what the server does, not what its UniFi account could do.
2. Enter the console address, username and password. The address defaults to
   `192.168.1.1`, the UniFi factory default; change it if your gateway uses
   another address.
3. Choose how clients connect (see above): add your public hostname to
   **Allowed hostnames**, and set an **Access token** if you publish a port.
4. Start the app and check the log. It shows whether a token is required and
   which networks are trusted.

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
