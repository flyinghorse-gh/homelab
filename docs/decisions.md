# Architecture Decisions

This file records decisions that should survive individual chat sessions.

---

## ADR-001 — Git Repository Is the Project Source of Truth

Date: 2026-09-27

Decision:

The private `homelab` Git repository will be the durable source of truth for
project documentation, scripts, configuration templates, and infrastructure
history.

Reason:

Chat sessions and individual development machines should not be required to
reconstruct the environment.

---

## ADR-002 — Secrets Must Not Be Stored in Git

Date: 2026-09-27

Decision:

Passwords, private keys, authentication tokens, recovery codes, and sensitive
configuration backups will not be committed to Git.

---

## ADR-003 — Infrastructure Changes Are Incremental

Date: 2026-09-27

Decision:

Potentially disruptive infrastructure changes will be made one logical layer
at a time.

Each change should include:

1. Current-state inspection
2. Backup when appropriate
3. Change
4. Verification
5. Documentation

Reason:

This reduces the likelihood of losing access to the server or network and
makes troubleshooting easier.

---

## ADR-004 — Management Interfaces Stay Off the Public Internet

Date: 2026-09-27

Decision:

Administrative interfaces such as OPNsense management should not be directly
exposed to the WAN.

Remote management should use a controlled private-access mechanism.

---

## ADR-005 — Ubuntu Host with Virtualized OPNsense

Recorded: 2026-09-27; original decision date unknown.

The Part 1 v6 reference documents a single Lenovo ThinkCentre running Ubuntu
with KVM/QEMU/libvirt and an OPNsense VM. Ubuntu supplies virtualization and
future services; OPNsense owns routing and firewall duties. `br-wan` bridges
the built-in Ethernet NIC without a host IP; `br-lan` supplies the private LAN
and Ubuntu management at `192.168.5.2/24`.

This adapts FUTO's dedicated-router design to the available single machine.

---

## ADR-006 — Preserve the Shared Upstream Router

Recorded: 2026-09-27; original decision date unknown.

Keep the shared upstream modem/router in normal routing mode so other
household users retain service. The documented setup uses double NAT. Do not
enable bridge/passthrough mode or introduce public port forwards under this
design. Ubuntu must retain a verified management/recovery path during changes.

---

## ADR-007 — DuckDNS for Public IPv4 Tracking

Recorded: 2026-09-27; original decision date unknown.

Use DuckDNS through OPNsense `os-ddclient`, with an external IPv4 checker
because OPNsense WAN has a private upstream address. The reference selected
DuckDNS instead of FreeDNS for simplicity and its free hostname service.
DDNS does not authorize inbound exposure; update credentials remain outside Git.

---

## ADR-008 — Tailscale for Private Remote Access

Recorded: 2026-09-27; original decision date unknown.

Use Tailscale on OPNsense to reach management and advertise only
`192.168.5.0/24`. Restrict Grants to the owner's identity and the OPNsense
Tailscale address/private LAN. Do not advertise the upstream subnet or a
default route, enable exit-node mode/Funnel, or add public forwarding.

This preserves the shared router while supporting remote access through NAT.
The reference records OPNsense device-key expiry disabled for unattended
operation; personal clients keep normal expiry. Preserve LAN recovery access.

---

## ADR-009 — IDE Workflow and Explicit Git Approval

Date: 2026-09-27

Continue homelab work using IDE-based Codex and repository documentation in
place of relying on earlier ChatGPT web conversations. Keep current state,
history, decisions, component documentation, and the next-session handoff
updated as meaningful work proceeds.

Codex must ask for explicit approval before committing and before pushing.
Editing authorization does not cover these actions, and commit approval does
not imply push approval. Never push to `main` independently. A user may
explicitly approve both actions for a stated scope.

---

## ADR-010 — FUTO as the Guiding Reference

Date: 2026-09-27

Use FUTO's "Introduction to a Self Managed Life" as the guiding reference.
The Part 1 v6 DOCX records the local ThinkCentre adaptations and earlier work;
Markdown records ongoing verified state and progress. Apply guide steps only
after checking their fit with the existing infrastructure and safety rules.

The initial next-session selection was DOCX Chapter 2. The user's subsequent
agenda clarified that the intended next milestone is network-wide DNS filtering
and ad blocking, matching DOCX section 8.3. This supersedes the earlier starting
point. Compare Unbound blocklists and AdGuard Home before choosing an engine;
no implementation decision has been made. Retain unfinished foundation checks
as open tasks, without automatically repeating the installation chapter.
(The engine choice was made later: see ADR-011.)

---

## ADR-011 — AdGuard Home on the Ubuntu Host for DNS Filtering

Date: 2026-10-01

Decision:

Use AdGuard Home as the DNS filter, running as a systemd service on the Ubuntu
host, bound only to the host's LAN address `192.168.5.2` (DNS `53`, dashboard
`3000`). Its only upstream is OPNsense Unbound at `192.168.5.1`, with no
fallback servers. Unbound keeps its stock recursive configuration.

Reason:

The user wanted an easy on/off switch and per-client rules in a dashboard.
Unbound's built-in blocklist has only limited per-source controls. No
AdGuard Home plugin was available in the OPNsense plugin list (including
community plugins) on `26.7`, and running a third-party repository on the
firewall was judged a worse trade-off than the host. The official binary on the
host keeps the firewall unchanged.

Consequences:

- The host is a dependency for LAN DNS. The VM and the filter share one machine,
  so there is no hardware redundancy.
- The service must come up after `br-lan` has its address; this held in one
  reboot test (see current state).
- The dashboard is not exposed beyond the LAN. The setup wizard was bound to
  the LAN address (`-h 192.168.5.2`) because it listens on all interfaces by
  default and the host also has an upstream Wi-Fi link.

---

## ADR-012 — Clients Use AdGuard Home Directly, With No Secondary DNS

Date: 2026-10-02

Decision:

Hand out AdGuard Home as the only DNS server through a Dnsmasq DHCP option
`dns-server [6]` = `192.168.5.2` on the LAN. Do not add `192.168.5.1` or a
public resolver as a second server.

Reason:

Per-client rules need AdGuard Home to see each client's real address, which a
chain through Unbound would hide. A second server would let devices skip the
filter. The accepted cost is that DNS stops for LAN clients if the host or
service is down.

Rollback:

Delete or disable the DHCP option, Apply, and renew client leases. A single PC
can be pointed at `192.168.5.1` by hand.

Open: enforcement against devices that use their own DNS is not decided.

---

## ADR-013 — Privacy Posture: Filter First, Encrypted DNS and VPN Separately

Date: 2026-10-02

Decision:

DNS filtering reduces tracker and telemetry traffic and keeps query logs on
the user's own hardware, but it is not anonymity. Keep short log retention and
leave AdGuard's Browsing security and Parental control off, because those send
queries to AdGuard's servers. Treat DNS over TLS to a chosen no-log resolver as
a separate, later change, and a VPN for outbound traffic as its own chapter.
Do not change the Tailscale design (access to the LAN only, no exit node) for
this. (The no-exit-node part was later superseded by ADR-015.) Tailscale is an inbound access tunnel; it does not hide the home
connection from sites.

Reason:

The user's goal is to share as little data as possible. Each layer protects
against a different party, and moving to DoT or a VPN only shifts trust to the
resolver or VPN provider. No DoT resolver or VPN provider has been selected.

---

## ADR-014 — Remote Devices Use AdGuard Home Through Tailscale

Date: 2026-10-03

Decision:

Give the restricted second Tailscale account `tcp:3000`, `tcp:53` and `udp:53`
to the Ubuntu host `192.168.5.2` in the tailnet policy, and set the tailnet's
global nameserver to `192.168.5.2` with Override DNS servers on, so remote
devices are filtered too. Remote devices reach it over the existing
`192.168.5.0/24` subnet route. This refines ADR-008 (Tailscale design) and
overrides the earlier "keep remote Tailscale DNS unchanged initially" plan.
The firewall, subnet advertisement and no-exit-node design are unchanged.

Reason:

The user wants filtering and dashboard access away from home. The second
account had been deliberately limited to OPNsense `443` and SSH `22`; widening
it is accepted for these three ports on one address only.

Consequences:

- The setting is tailnet-wide: a device that cannot reach `192.168.5.2` loses
  DNS until the override is turned off.
- Remote devices all appear in AdGuard as `192.168.5.1`, so they cannot have
  separate per-client rules.
- Networks that also use `192.168.5.x` will break the route.

Rollback:

Turn off Override DNS servers (or delete the nameserver) in the Tailscale admin
console; remove the added grant from the policy. Keep a saved copy of the policy
outside Git. Tested on one Windows PC only. Account identities, the OPNsense
Tailscale address and the policy text are not stored in this repository.

---

## ADR-015 — OPNsense Offers a Tailscale Exit Node

Date: 2026-10-14 (user-reported change; verified in part live the same day)

Decision:

OPNsense advertises itself as a Tailscale exit node, approved in the admin
console, so the user's devices can route all internet traffic through the home
connection and OPNsense. The tailnet policy already had a shared grant
(`autogroup:internet`, all ports) for both identities, so both accounts are
permitted to use it. This supersedes the "no exit node" parts of ADR-008,
ADR-013 and ADR-014. The `192.168.5.0/24` subnet route is unchanged and still
approved. No public port forward and no upstream router change were added.

Reason:

The user wants their devices filtered and routed through the home network when
away from it, and uses it from their own devices (phone confirmed by the user).

Consequences:

- Websites see the home ISP address for devices using the exit node. Traffic is
  limited by home upload speed and depends on OPNsense and the host being up.
- The grant is broad (`ip: *`) and applies to both accounts, including the
  restricted second account, which was otherwise limited to a few ports.
- **Decided 2026-10-14:** the user chose to keep the exit-node grant for the
  second account as well. It stays broad on purpose; revisit only if that
  account's role changes.
- It is the policy, not each device's setting, that allows exit-node use; a
  device only uses it when the user selects it.
- With the exit node selected, DNS filtering still worked on the test laptop.

Firewall/NAT state (from user screenshots of the WebGUI, 2026-10-14):
Firewall → Rules shows interface rules for LAN (IPv4 and IPv6 allow-any) and
one TAILSCALE rule, "Allow Tailscale to OPNsense", source/destination/protocol
all `*`. Floating rules: none (user-reported). Firewall → NAT → Outbound mode
is **Hybrid**, with one manual rule: WAN, IPv4, source `100.64.0.0/10`, any
destination, translate to interface address, no description. That rule is what
lets exit-node traffic leave through the upstream router; it is not an inbound
rule. Port forwards: this OPNsense has no "Port Forward" page; Firewall → NAT →
Destination NAT shows no user rules, only the collapsed "Automatically
generated rules" group (screenshot, 2026-10-14). The auto-generated entries
were not expanded, so their contents are unrecorded.

Verification (live, Windows laptop on the home network, 2026-10-14):
route to the internet moved to the Tailscale interface and internet stayed
reachable; `doubleclick.net` returned `0.0.0.0`; the laptop was reverted to no
exit node. Public IP could not differ at home. Not verified: use away from home,
whether OPNsense firewall/NAT was edited for this, and the OPNsense setting
itself (user-reported only).

Rollback:

Untick the exit-node route in the Tailscale admin console and turn off the
exit-node advertisement in the OPNsense Tailscale plugin. Devices must stop
selecting it. Tighten or remove the `autogroup:internet` grant if it is no
longer wanted. Keep a saved copy of the policy outside Git.

---

## ADR-016 — Unbound Forwards to Quad9 Over DNS over TLS

Date: 2026-10-14 (user ran the change; capture output pasted by the user)

Decision:

Unbound on OPNsense forwards all lookups to Quad9 over DNS over TLS
(`9.9.9.9` and `149.112.112.112`, port `853`, verify name `dns.quad9.net`),
instead of resolving recursively over plain DNS. AdGuard Home still sits in
front and still uses Unbound at `192.168.5.1` as its only upstream. The
Query Forwarding `home.arpa` rule is unchanged. This resolves the "DNS over TLS
(planned)" item in ADR-013.

Reason:

The user wants the internet provider not to read their lookups and wants
built-in malware blocking. Quad9's recommended address blocks known malware and
validates DNSSEC. The provider's published policy (Swiss non-profit, says it
does not store IP addresses or query names) was read on 2026-10-14; it is a
stated policy, not something verified here. The `dns11` (ECS) variant was
rejected because it shares part of the client network. Mullvad DNS was rejected
because its page announces it ends on 2026-11-02. A self-run resolver on a
rented server was considered and deferred.

Consequences:

- The ISP sees an encrypted connection to Quad9, not the names looked up. It
  still sees destination IP addresses; this is not anonymity.
- Trust moves to Quad9. If Quad9 or port `853` is unreachable, lookups fail
  until the entries are removed.
- Malware blocking now comes from Quad9 in addition to AdGuard's lists.

Verification:

User-reported: three `Resolve-DnsName` checks passed (normal answers plus
`0.0.0.0` for `doubleclick.net`). Live capture on the Ubuntu host (user ran,
output pasted): on `br-wan`, port `853` showed TCP packets between the OPNsense
WAN address and `9.9.9.9`; port `53` showed 0 packets in a 20-second window that
may have been quiet. User-reported dnsleaktest extended test (2026-10-14): three resolvers, all on
Packet Clearing House's resolver network (the operator behind Quad9), in one
US city; no ISP resolver and no home IP listed, so no leak seen from that
device. Not seen: the AdGuard Query Log or Unbound log after the change, and a
plain-DNS capture taken while browsing.

Rollback:

Delete both entries under Services → Unbound DNS → DNS over TLS and Apply
(returns to recursive mode). An encrypted OPNsense backup was taken beforehand
(user-reported; stored outside the repository).
