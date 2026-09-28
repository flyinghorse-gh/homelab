# Installation and Setup History

## 2026-09-22 — Ubuntu Installation

The mini-PC previously contained Windows.

Ubuntu installation was started without a traditional USB installer.

Grub2Win was used during the boot/install process and an Ubuntu installer ISO
was booted from local storage.

Ubuntu was successfully installed and the machine booted into Ubuntu.

Disk partitions were manually adjusted during this process.

The exact current disk layout must be documented using fresh Linux disk
inspection commands rather than relying on installation-time screenshots.

SSH was enabled after Ubuntu installation.

## 2026-09-23 onward — OPNsense Hardening

Work began on securing OPNsense management access.

Before making firewall changes:

- A configuration backup was created.

The existing configuration was inspected:

- WAN firewall rules were empty.
- NAT port forwards were empty (not a claim about all NAT rules).

Initial hardening changes were applied incrementally.

Connectivity checks performed afterward continued to work.

## 2026-09-27 — Project Repository

A private GitHub repository named `homelab` was created.

The repository was cloned to the Windows development machine.

The repository is now being prepared as the durable project record so that
VS Code, Codex, OpenCode, the Ubuntu server, and future machines can work from
the same documented state.

## Prior Work Recorded in Part 1 v6 — Exact Dates Unconfirmed

These milestones come from the
[reference DOCX](reference/ThinkCentre_OPNsense_Self_Managed_Setup_Part_1_v6.docx).
Their order follows the document; individual dates and current live state were
not independently verified during migration.

1. Installed KVM/QEMU/libvirt. An account-parsing issue was resolved by
   confirming the libvirt account and restarting libvirt.
2. Installed OPNsense with 2 vCPUs, 4096 MiB RAM, and a 20 GB virtual disk.
   Persistent disk boot and VM autostart are reported working.
3. Built `br-wan` and `br-lan`, assigned OPNsense `192.168.5.1/24` and Ubuntu
   `192.168.5.2/24`, and configured DHCP `.100`–`.200`. Verified WAN routing
   and DNS through the shared upstream router and completed the WebGUI wizard.
4. Bridged USB Ethernet to the LAN. A Windows client initially received an
   APIPA address, then obtained a LAN DHCP address and successfully pinged
   OPNsense and Ubuntu after DHCP negotiation.
5. Updated OPNsense to a repository-required maintenance release and installed
   `os-ddclient`. An empty backend account list was fixed by saving/applying
   the DuckDNS account. External DNS resolution then matched the public IPv4.
6. Installed/enrolled OPNsense in Tailscale and assigned `tailscale0`. An
   initially inactive firewall rule was resolved by explicitly reloading the
   ruleset; the legacy rule editor was also installed during diagnosis.
7. Approved the `192.168.5.0/24` subnet route and verified OPNsense HTTPS and
   Ubuntu SSH from a phone hotspot without changing the shared router.
8. Downloaded an encrypted backup before VPN hardening, audited WAN rules and
   NAT port forwards, restricted Tailscale Grants to the owner's identity,
   disabled OPNsense device-key expiry, and rechecked access successfully.

Temporary installation NIC removal, full switch/AP deployment, and BIOS
power-recovery configuration are not confirmed complete by the reference.

## 2026-09-27 — Documentation Migration to IDE Workflow

Reconciled Markdown with Part 1 v6 and added network/access details and a
next-session handoff. Prior verification is distinguished from fresh checks
still required. FUTO remains the guiding reference for the adapted setup.

Git history confirms the initial documentation and reference-document commits.
VS Code/Codex are in use. The user requires approval before Codex commits or
pushes any changes, including pushes to `main`.

No infrastructure was changed or live-verified during migration. The initial
handoff targeted DOCX Chapter 2; the follow-up below supersedes that agenda. See
[the migration log](../history/2026-09-27-documentation-migration.md).

## 2026-09-27 — Next Milestone Clarified

The user supplied the previous ChatGPT web agenda: network-wide DNS filtering
and ad blocking, adapting FUTO to OPNsense. This matches DOCX section 8.3 and
replaces the plan to revisit the Ubuntu/virtualization chapter. The first
decision is Unbound blocklists versus AdGuard Home; neither has been selected
or configured as part of this work. See [the current handoff](04-next-session.md).

Documentation migration commit `ebb717c` was created with user approval; the
user reported pushing it themselves. The user subsequently authorized a
separate commit and push of the agenda corrections. No infrastructure was changed.
