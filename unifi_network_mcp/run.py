"""Home Assistant app entrypoint for sirkirby/unifi-mcp (Network server).

Reads the app options from /data/options.json, maps them to the environment
variables the upstream server expects, and replaces this process with the
server (so it stays PID 1, which the server requires before it starts HTTP).
"""

import json
import os
import socket
import sys

OPTIONS_FILE = "/data/options.json"
MCP_PORT = 3000


def log(msg: str) -> None:
    print(f"[ha-wrapper] {msg}", flush=True)


def flag(value: bool) -> str:
    return "true" if value else "false"


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

    log(f"UniFi controller: {env['UNIFI_HOST']}:{env['UNIFI_PORT']} "
        f"site={env['UNIFI_SITE']} user={username}")
    log(f"MCP endpoint: http://{hostname}:{MCP_PORT}/mcp")
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
