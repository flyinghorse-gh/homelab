# 2026-10-14 — Lease Check, Remote Filtering Retest, Exit Node

Evidence types: **user-reported** (OPNsense WebGUI, phone, admin console) and
**live** (commands run by the agent on the Windows laptop). The server was not
reached by the agent.

## Open item 1: the `192.168.5.90` lease

- User-reported: Dnsmasq Hosts and Leases tabs both empty. Not a reservation.
- Wired PC Ethernet was unplugged: link-local address, `home.arpa` suffix
  retained from the last lease. No lease data left to inspect.
- Unresolved. Re-test with the cable connected (see handoff item 1).

## Remote filtering retest (Windows laptop on Tailscale)

- `doubleclick.net` → `0.0.0.0`/`::`, `example.com` resolves, port 53 on
  `192.168.5.2` reachable over the Tailscale interface, route via Tailscale.
- The laptop reached OPNsense directly on the upstream network, so it was on
  the home network. Not a true away-from-home test.

## Exit node (ADR-015)

- `tailscale status` showed OPNsense "offers exit node". The user then said
  they had enabled it and use it from their devices; the subnet route is
  approved. The tailnet policy has a shared `autogroup:internet` grant for both
  identities (pasted by the user; not stored here).
- Live test: `tailscale set --exit-node=opnsense` → internet route moved from
  Wi-Fi to Tailscale, internet reachable, `doubleclick.net` still `0.0.0.0`,
  public IPv4 unchanged (expected at home). Reverted afterwards; exit node
  confirmed cleared. First run's odd output (different IP, missing DNS lines)
  came from an IPv6/IPv4 check and output formatting; the IPv4 rerun was clean.
- Docs that said "no exit node" were updated: `docs/01`, `docs/03`, ADR-008/013
  notes, `docs/05`, guide chapter 7.

## Not verified

Away-from-home exit-node egress, OPNsense firewall/NAT edits for it, the
OPNsense exit-node setting itself, second-account device use.

## Encrypted upstream DNS (ADR-016, guide chapter 9)

- Compared resolvers from their own pages. Quad9 chosen (malware blocking,
  DNSSEC, stated no-storage policy). Mullvad DNS rejected: its page announces
  it ends 2026-11-02. Quad9 `dns11` rejected because it shares client subnet.
- User-reported: encrypted OPNsense backup taken first; both DoT entries added
  to Unbound (`9.9.9.9`, `149.112.112.112`, port `853`, verify
  `dns.quad9.net`); Windows lookups passed.
- Live capture on the Ubuntu host (user ran, output pasted): `br-wan` port
  `853` showed TCP packets between the OPNsense WAN address and `9.9.9.9`;
  port `53` showed 0 packets in 20 seconds, possibly a quiet window.
- User-reported dnsleaktest extended test: three resolvers, all on PCH's
  resolver network (Quad9's operator), one US city; no ISP resolver and no home
  IP in the list. The user's public IP was in the paste and is not recorded.
- Also decided: the second account keeps the exit-node grant.
- Added chapter 9 to the guide and nav; allowed the public Quad9 resolver
  addresses in `scripts/docs/check-guide.py`. The privacy check passes and a
  strict site build into a scratch folder succeeded.
