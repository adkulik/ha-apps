"""Home Assistant app entrypoint for sirkirby/unifi-mcp (Network server).

Reads the app options from /data/options.json, maps them to the environment
variables the upstream server expects, and replaces this process with the
server (so it stays PID 1, which the server requires before it starts HTTP).
"""

import ipaddress
import json
import os
import socket
import sys
import urllib.request

OPTIONS_FILE = "/data/options.json"
MCP_PORT = 3000
MIN_TOKEN_LENGTH = 32
SUPERVISOR_SELF_INFO = "http://supervisor/addons/self/info"


def log(msg: str) -> None:
    print(f"[ha-wrapper] {msg}", flush=True)


def flag(value: bool) -> str:
    return "true" if value else "false"


def fail(msg: str) -> None:
    log(msg)
    sys.exit(1)


def published_host_port() -> int | None | bool:
    """Host port mapped to the MCP port, None when unpublished, False when unknown.

    Reads the app's own network mapping from the Supervisor API, so the
    wrapper knows whether the server is reachable from the LAN.
    """
    token = os.environ.get("SUPERVISOR_TOKEN")
    if not token:
        return False
    request = urllib.request.Request(SUPERVISOR_SELF_INFO, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            info = json.load(response)
    except (OSError, ValueError):
        return False
    network = (info.get("data") or {}).get("network") or {}
    port = network.get(f"{MCP_PORT}/tcp")
    return int(port) if port else None


def upstream_supports_trusted_networks() -> bool:
    """Whether the bundled server honours UNIFI_MCP_HTTP_AUTH_TRUSTED_NETWORKS."""
    try:
        from unifi_mcp_shared import transport
    except ImportError:
        return False
    return hasattr(transport, "HTTP_AUTH_TRUSTED_NETWORKS_ENV")


def parse_trusted_networks(entries: list) -> list[str]:
    networks: list[str] = []
    for raw in entries or []:
        entry = str(raw).strip()
        if not entry:
            continue
        try:
            network = ipaddress.ip_network(entry, strict=False)
        except ValueError:
            fail(f"Trusted networks: '{entry}' is not an IP address or CIDR network.")
        if network.prefixlen == 0:
            fail(f"Trusted networks: '{entry}' would trust every address and switch the token off.")
        if str(network) not in networks:
            networks.append(str(network))
    return networks


def main() -> None:
    try:
        with open(OPTIONS_FILE, encoding="utf-8") as fh:
            opts = json.load(fh)
    except (OSError, ValueError) as err:
        log(f"Cannot read {OPTIONS_FILE}: {err}")
        sys.exit(1)

    username = (opts.get("unifi_username") or "").strip()
    password = opts.get("unifi_password") or ""
    if not username or not password:
        log("Set unifi_username and unifi_password in the app configuration "
            "(use a dedicated local UniFi account, not a Ubiquiti SSO account).")
        sys.exit(1)

    env = os.environ

    # Controller connection
    env["UNIFI_HOST"] = str(opts.get("unifi_host", "192.168.1.1"))
    env["UNIFI_PORT"] = str(opts.get("unifi_port", 443))
    env["UNIFI_USERNAME"] = username
    env["UNIFI_PASSWORD"] = password
    env["UNIFI_SITE"] = str(opts.get("unifi_site", "default"))
    env["UNIFI_VERIFY_SSL"] = flag(bool(opts.get("verify_ssl", False)))

    # Streamable HTTP transport on the internal app network only
    env["UNIFI_MCP_HTTP_ENABLED"] = "true"
    env["UNIFI_MCP_HTTP_TRANSPORT"] = "streamable-http"
    env["UNIFI_MCP_HOST"] = "0.0.0.0"
    env["UNIFI_MCP_PORT"] = str(MCP_PORT)

    # Host-header allowlist (DNS rebinding protection stays on):
    # loopback, this container's own hostname, plus the public hostnames
    # a reverse proxy / tunnel forwards (e.g. unifi-mcp.example.com).
    hostname = socket.gethostname()
    hosts = ["localhost", "127.0.0.1", hostname]
    hosts += [h.strip() for h in opts.get("allowed_hosts", []) if h.strip()]
    allowed = []
    for host in hosts:
        for entry in (host, f"{host}:{MCP_PORT}"):
            if entry not in allowed:
                allowed.append(entry)
    env["UNIFI_MCP_ALLOWED_HOSTS"] = ",".join(allowed)

    # Access control. The server has no login of its own unless a token is
    # set; a published host port (LAN, VPN) therefore requires one.
    auth_token = (opts.get("auth_token") or "").strip()
    trusted = parse_trusted_networks(opts.get("trusted_networks", []))
    if auth_token:
        if len(auth_token) < MIN_TOKEN_LENGTH or not (auth_token.isascii() and auth_token.isprintable()) \
                or any(ch.isspace() for ch in auth_token):
            fail(f"Access token: use at least {MIN_TOKEN_LENGTH} printable characters without spaces "
                 "(for example the output of `openssl rand -hex 32`).")
        env["UNIFI_MCP_HTTP_AUTH_TOKEN"] = auth_token
    if trusted:
        env["UNIFI_MCP_HTTP_AUTH_TRUSTED_NETWORKS"] = ",".join(trusted)

    # Permissions: server-side policy gates for mutations
    env["UNIFI_POLICY_NETWORK_CREATE"] = flag(bool(opts.get("allow_create", False)))
    env["UNIFI_POLICY_NETWORK_UPDATE"] = flag(bool(opts.get("allow_update", False)))
    env["UNIFI_POLICY_NETWORK_DELETE"] = flag(bool(opts.get("allow_delete", False)))
    env["UNIFI_NETWORK_TOOL_PERMISSION_MODE"] = str(opts.get("permission_mode", "confirm"))
    env["UNIFI_TOOL_REGISTRATION_MODE"] = str(opts.get("tool_registration_mode", "lazy"))

    # Extra KEY=VALUE pairs, e.g. per-category policy gates such as
    # UNIFI_POLICY_NETWORK_DNS_CREATE=true. Applied last, so they win.
    for item in opts.get("extra_env", []) or []:
        key, sep, value = str(item).partition("=")
        if sep and key:
            env[key.strip()] = value
            log(f"extra env: {key.strip()} set")

    # Checked after extra_env, which may set the token itself.
    token_set = bool((env.get("UNIFI_MCP_HTTP_AUTH_TOKEN") or "").strip()
                     or (env.get("UNIFI_NETWORK_MCP_HTTP_AUTH_TOKEN") or "").strip())
    if trusted:
        if not token_set:
            log("Trusted networks are set but no access token is: they have no effect.")
        elif not upstream_supports_trusted_networks():
            fail("Trusted networks need a newer UniFi Network MCP server than the one in this app version. "
                 "Clear 'Trusted networks' (clients then all need the token) or update the app.")

    host_port = published_host_port()
    if host_port and not token_set:
        fail(f"Host port {host_port} publishes the MCP server on your network, but no access token is set. "
             "Set an access token (at least 32 characters), or clear the host port in the Network section.")
    if host_port is False:
        log("Could not read the app's port mapping from the Supervisor; "
            "make sure the host port is empty or an access token is set.")

    log(f"UniFi controller: {env['UNIFI_HOST']}:{env['UNIFI_PORT']} "
        f"site={env['UNIFI_SITE']} user={username}")
    log(f"MCP endpoint: http://{hostname}:{MCP_PORT}/mcp")
    if host_port:
        log(f"Also published on host port {host_port} (token required).")
    if token_set:
        log("Access token: required" + (f", except from {', '.join(trusted)}" if trusted else "") + ".")
    elif host_port is None:
        log("Access token: none - only apps on the internal Home Assistant network can reach the server.")
    else:
        log("Access token: none.")
    log(f"Allowed hosts: {env['UNIFI_MCP_ALLOWED_HOSTS']}")
    log("Mutations: create={c} update={u} delete={d} mode={m}".format(
        c=env["UNIFI_POLICY_NETWORK_CREATE"],
        u=env["UNIFI_POLICY_NETWORK_UPDATE"],
        d=env["UNIFI_POLICY_NETWORK_DELETE"],
        m=env["UNIFI_NETWORK_TOOL_PERMISSION_MODE"],
    ))

    os.execvp("unifi-network-mcp", ["unifi-network-mcp"])


if __name__ == "__main__":
    main()
