# 2026-10-01 to 2026-10-03 — AdGuard Home DNS Filtering

Built network-wide DNS filtering with the user running each step and pasting
results. The agent did not touch the server. Details and evidence:
[DNS filtering](../docs/05-dns-filtering.md).

- **2026-10-01:** read-only inspection of Unbound, Dnsmasq and DHCP (stock,
  recursive, no blocklist, no custom DHCP DNS). Compared Unbound blocklists with
  AdGuard Home; the user chose AdGuard Home for the dashboard and per-client
  rules. No plugin existed for OPNsense `26.7`, so it went on the Ubuntu host.
  Encrypted OPNsense backup taken. Installed `v0.107.79` as a systemd service on
  `192.168.5.2` only, upstream `192.168.5.1`, HaGeZi Pro list; blocking confirmed
  from the host. Dashboard password reset via the config file after a lockout.
- **2026-10-02:** LAN client test on the wired PC. Early timeouts were traced to
  Windows routing `192.168.5.x` through Tailscale; with Tailscale off everything
  worked. Added a Dnsmasq DHCP option `dns-server [6]` = `192.168.5.2` (first
  attempt used the IPv6 `Option6` field by mistake; the change only took
  effect after Apply). The PC then got `192.168.5.2` and blocked
  `doubleclick.net`. Allowlist cycle and IPv6 DNS check done. Host rebooted.
- **2026-10-03:** post-reboot check at `up 15:56`: `opnsense` VM running with
  autostart enabled, AdGuard Home active and bound, blocking still working.
  Documentation updated; guide Chapter 8 rewritten from this work.

Decisions: ADR-011 (AdGuard Home on the host), ADR-012 (single DHCP DNS
server), ADR-013 (privacy posture).

Not done: DNS over TLS, enforcement against devices using their own DNS,
per-client rules, the Tailscale port-restriction investigation, a re-read of the
DHCP pool, confirming log-retention settings, an OPNsense restore test.

Only documentation was edited by the agent. Nothing was committed or pushed.
