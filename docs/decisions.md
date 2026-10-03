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
this. Tailscale is an inbound access tunnel; it does not hide the home
connection from sites.

Reason:

The user's goal is to share as little data as possible. Each layer protects
against a different party, and moving to DoT or a VPN only shifts trust to the
resolver or VPN provider. No DoT resolver or VPN provider has been selected.
