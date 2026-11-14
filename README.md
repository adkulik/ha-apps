# adkulik Home Assistant apps

Home Assistant app (add-on) repository.

[![Add repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fadkulik%2Fha-apps)

## Apps

| App | Description |
|-----|-------------|
| [UniFi Network MCP](unifi_network_mcp/DOCS.md) | MCP server for the UniFi Network application (wrapper around [sirkirby/unifi-mcp](https://github.com/sirkirby/unifi-mcp)), read-only by default |

## Installation

In Home Assistant go to **Settings → Apps → App store → ⋮ → Repositories** and add:

```
https://github.com/adkulik/ha-apps
```

## Credits

The UniFi Network MCP server is developed by [sirkirby](https://github.com/sirkirby/unifi-mcp)
(MIT license). This repository only contains the Home Assistant packaging.
