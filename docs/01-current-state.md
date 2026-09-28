# Current Homelab State

Last updated: 2026-09-27

This document incorporates the completed work recorded in the
[Part 1 v6 reference](reference/ThinkCentre_OPNsense_Self_Managed_Setup_Part_1_v6.docx),
especially its checkpoint and Chapters 7–8. Infrastructure results below are
reported by that document, not independently live-verified on 2026-09-27.
Exact milestone dates are not supplied by the reference.

FUTO's "Introduction to a Self Managed Life" is the guiding reference, adapted
to this ThinkCentre setup. Markdown is the ongoing project record; the DOCX is
historical evidence containing both completed work and pending instructions.

## Primary Server

- Ubuntu is installed on the Lenovo ThinkCentre, running headlessly with SSH.
- KVM/QEMU/libvirt are working; AMD-V/SVM and `kvm_amd` were observed.
- The persistent `opnsense` VM boots from virtual disk and is configured to
  autostart. Creation settings: 2 vCPUs, 4096 MiB RAM, and a 20 GB qcow2 disk
  at `/var/lib/libvirt/images/opnsense.qcow2`; current allocation needs inspection.
- Exact ThinkCentre model, hostname, Ubuntu version, CPU model, total RAM,
  physical storage inventory, and final host disk layout remain undocumented.
- The reference used an OPNsense 26.7 installer and later a maintenance update;
  the current installed patch release is unknown.
- Sleep/suspend masking is described in the reference. Current service state,
  reboot recovery, and BIOS restore-on-AC-power-loss still need verification.

## Disk / Operating System

Ubuntu was installed after transitioning the machine away from its previous
Windows setup.

Disk partitioning was adjusted manually during installation.

The current final partition layout should be documented from fresh output of:

    lsblk
    df -h
    sudo fdisk -l

Do not infer the disk layout from old installation notes.

## Network / Firewall

Ubuntu hosts the bridges; OPNsense owns routing and firewall duties.

| Component | Recorded configuration |
|---|---|
| Shared upstream network | Router/NAT on `10.0.0.0/24`; stays in normal routing mode |
| WAN path | Built-in `enp1s0f0` → `br-wan` → OPNsense WAN |
| Ubuntu on `br-wan` | No host IPv4/IPv6 address intended |
| OPNsense WAN | DHCP; `10.0.0.11/24` observed, not a fixed address |
| LAN path | OPNsense LAN → `br-lan` → USB Ethernet `enx00e04c240c18` |
| OPNsense LAN | `192.168.5.1/24` |
| Ubuntu management | `192.168.5.2/24` on `br-lan`; `ipv4.never-default yes` |
| LAN DHCP pool | `192.168.5.100`–`192.168.5.200` |
| Setup management fallback | USB Wi-Fi `wlxfc221c100f59`; current address/route unknown |

Known completed work:

- An encrypted OPNsense configuration backup was downloaded before hardening.
- WAN firewall rules were checked and were empty.
- NAT port forwards were checked and were empty; this does not mean all NAT
  rules were absent.
- Initial management-hardening changes were completed.
- Connectivity was verified after those changes.
- OPNsense Internet routing and DNS worked; the WebGUI wizard was completed.
- A directly connected Windows LAN client obtained a DHCP address and reached
  both OPNsense and Ubuntu with 0% ping loss.
- WebGUI remains HTTPS-only with default/all listen interfaces and anti-lockout
  enabled. No shared upstream router changes were made.

Removal of the temporary libvirt/default NIC remains unconfirmed. Physical
switch/AP deployment and moving normal clients behind OPNsense remain pending.
No VLAN deployment is documented. See [network/access details](03-network-and-access.md).

## Dynamic DNS

DuckDNS is configured through `os-ddclient` with the native backend and an
external IPv4 checker. The hostname resolved to the public IPv4 reported by an
independent checker. IPv6 DDNS updates were disabled. The hostname and current
service state need recording/verification; keep the token outside Git.

## Remote Access

SSH is enabled on the Ubuntu server.

Tailscale is recorded as completed and externally verified:

- `os-tailscale` installed on OPNsense; `tailscale0` assigned as TAILSCALE.
- Approved advertised subnet: `192.168.5.0/24` only. No upstream subnet or
  default route advertised; exit-node mode and Funnel off.
- Grants restricted access to the owner's identity, targeting the OPNsense
  Tailscale address and private LAN. Device-key expiry disabled for OPNsense;
  personal clients retain normal expiry.
- OPNsense HTTPS and Ubuntu SSH at `192.168.5.2` succeeded from an external
  phone hotspot. Access also worked after the identity restriction was applied.
- No public port forwarding or shared upstream router changes were used.

Current reachability, actual Tailscale address, and current policy need fresh
inspection before changes affecting access. Historical success is not a fresh
audit of the running infrastructure.

## Source Control

A private GitHub repository named `homelab` has been created.

The repository has been cloned onto the primary Windows development machine.

Initial documentation and reference-document commits exist. VS Code/Codex are
in use; work is moving from ChatGPT web conversations into this repository.
Cloning onto Ubuntu has not been confirmed.

Codex must ask for explicit approval before committing and before pushing.
Editing permission authorizes neither action; never push to `main` on its own.

This repository is intended to become the durable source of truth for:

- documentation
- configuration templates
- scripts
- infrastructure decisions
- change history

## Secrets

Secrets are intentionally excluded from Git.

Sensitive router/firewall backups should be stored separately in protected
storage.

The protected backup location, restore procedure, and restore test are not yet
documented. Do not put credentials or sensitive backup contents into Git.

## Next Session

Continue with network-wide DNS filtering / ad blocking, using FUTO as the
guiding reference and DOCX section 8.3 as the recorded next milestone. The
user's follow-up agenda supersedes the earlier plan to revisit DOCX Chapter 2.
Compare Unbound blocklists with AdGuard Home before selecting or installing
anything. Filtering is not yet documented as enabled. Verify the actual LAN
client/DHCP/DNS path before changes; full switch/AP deployment remains unconfirmed.
See [the next-session handoff](04-next-session.md) for the starting checklist.
