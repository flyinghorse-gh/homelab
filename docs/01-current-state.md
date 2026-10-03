# Current Homelab State

Last updated: 2026-10-03

DNS filtering (AdGuard Home) was built and verified between 2026-10-01 and
2026-10-03 from output the user pasted from the Ubuntu host, the OPNsense
WebGUI, a Windows PC and the AdGuard dashboard. The agent did not run these
commands itself. See the section "DNS Filtering" below.

This document incorporates the completed work recorded in the
[Part 1 v6 reference](reference/ThinkCentre_OPNsense_Self_Managed_Setup_Part_1_v6.docx),
especially its checkpoint and Chapters 7–8. Infrastructure results below are
reported by that document, not independently live-verified on 2026-09-27.
Exact milestone dates are not supplied by the reference. Fresh observations
from the DNS evaluation are explicitly identified below.

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
- User-reported WebGUI versions on 2026-09-27: OPNsense `26.7.4_1-amd64`,
  FreeBSD `15.1-RELEASE-p3`, OpenSSL `3.5.8`. These were not independently
  retrieved from the VM by the agent.
- Sleep/suspend masking is described in the reference. Current service state,
  reboot recovery, and BIOS restore-on-AC-power-loss still need verification.

## Live inspection — 2026-09-30

Output pasted by the user from the Ubuntu host (not run by the agent):

- Model: ThinkCentre M715q. Ubuntu with NetworkManager (QEMU machine type
  `pc-i440fx-resolute`). VM `opnsense`: running, 2 vCPUs, 4 GiB, virtio qcow2
  `vda`, two virtio NICs (`br-wan`, `br-lan`), empty CD-ROM (ISO ejected), VNC
  on 127.0.0.1 only. The temporary default NIC is gone. `virbr0` still exists.
- `virsh dominfo` reported Autostart: disable, contradicting the earlier note.
  Fixed on 2026-10-01 with `virsh autostart opnsense`; user-reported output
  now shows `Autostart: enable`. A later host reboot (see DNS Filtering) left
  the VM running with autostart enabled, as observed on 2026-10-03.
- Bridges are persistent NetworkManager profiles: `br-wan` (no host IP) with
  `br-wan-port`, `br-lan` 192.168.5.2/24 never-default with `br-lan-usb`.
  The USB Ethernet adapter currently shows NO-CARRIER (no cable).
- Ubuntu's current management path is the USB Wi-Fi adapter on the upstream
  network. Its Wi-Fi PSK is stored in plaintext in a root-only netplan file.
- ISO `OPNsense-26.7-dvd-amd64.iso` (2.0G) remains in the images directory.

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

## DNS Filtering

Details, evidence and limits: [DNS filtering](05-dns-filtering.md). Rationale:
ADR-011 to ADR-013 in [decisions](decisions.md). Dated log:
[history/2026-10-03-adguard-home-dns-filtering.md](../history/2026-10-03-adguard-home-dns-filtering.md).

Status: working for LAN clients that take DHCP DNS from OPNsense. Verified from
user-pasted output on 2026-10-01 to 2026-10-03.

- **Engine and placement:** AdGuard Home `v0.107.79`, official binary in
  `/opt/AdGuardHome` on the Ubuntu host, installed as the `AdGuardHome` systemd
  service (enabled). Listens on `192.168.5.2` only: DNS `53` (UDP/TCP) and the
  dashboard `3000`. Nothing is bound to `0.0.0.0`.
- **Query path:** LAN client → AdGuard Home `192.168.5.2:53` → Unbound
  `192.168.5.1:53` → recursive resolution. AdGuard's only upstream is
  `192.168.5.1`; fallback servers are empty. Query Log details showed
  `DNS server: 192.168.5.1:53`, `NOERROR`.
- **Unbound:** unchanged stock settings. Query Forwarding holds only the default
  `home.arpa` → `127.0.0.1:53053` rule (Dnsmasq); "Use System Nameservers"
  unchecked; DNS-over-TLS table empty; Unbound blocklist disabled. So Unbound
  resolves recursively over plain DNS. DNSSEC unchecked.
- **DHCP:** Dnsmasq DNS & DHCP serves the LAN (Dnsmasq DNS on port `53053`).
  A DHCP option `dns-server [6]` = `192.168.5.2` (LAN, Type Set) was added on
  2026-10-02 and applied. The test PC then showed DNS `192.168.5.2`.
  Router advertisements are enabled in Dnsmasq. The PC had IPv4 DNS only, no
  IPv6 DNS and only a link-local IPv6 address.
- **Lists:** AdGuard DNS filter (default) plus HaGeZi's Pro Blocklist (about
  277,000 rules). `doubleclick.net` returns `0.0.0.0`/`::`; `example.com`
  resolves. An allow (Unblock) and re-block of `doubleclick.net` both worked.
- **Not changed:** Browsing security and Parental control not enabled. The user
  was asked to set log rotation and statistics retention to a short period; the
  saved value was never reported back, so it is unconfirmed.
- **Admin access:** AdGuard dashboard password was reset by editing
  `AdGuardHome.yaml` (bcrypt hash). The password is held by the user outside
  Git. The dashboard is reached through an SSH tunnel from Windows
  (`ssh -L 3000:192.168.5.2:3000 <user>@192.168.5.2`, browse `localhost:3000`).
- **Backup:** an encrypted OPNsense configuration backup was taken on
  2026-10-01 before the changes and checked as not containing readable XML.
  It is stored outside the repository; its location is not recorded here.
- **Reboot test:** after a host reboot the `opnsense` VM was `running` with
  `Autostart: enable` (VM Id 1), AdGuard Home was `active` with listeners on
  `192.168.5.2`, and a blocked lookup still returned `0.0.0.0`. The check was
  run at `up 15:56` (about 16 hours after the reboot), so the boot timing is
  inferred from low process/VM IDs, not watched live.

Known limits and open items:

- A device or app that uses its own DNS server bypasses the filter. On the
  test PC `Resolve-DnsName doubleclick.net -Server 1.1.1.1` returned real
  addresses. No port-53 restriction or other enforcement exists.
- Upstream DNS is plain, not encrypted (no DoT). Resolution is recursive from
  the OPNsense VM. No anonymity is provided by DNS filtering.
- Over Tailscale, ports `53` and `3000` to `192.168.5.2` timed out while port
  `22` worked. With Tailscale disconnected on the PC and traffic on the wired
  adapter, `53` worked. `docs/03` records an allow-all TAILSCALE interface
  rule and an all-ports Grant, which does not explain the timeouts. The cause
  is **unresolved** and not yet inspected.
- Windows with Tailscale connected sent `192.168.5.x` traffic through the
  tunnel instead of the wired link, which skewed early LAN tests. Check
  `Find-NetRoute` first.
- The test PC's wired lease was `192.168.5.90`, below the recorded
  `192.168.5.100`–`.200` pool. The DHCP ranges tab was never re-read after it.
- Remote (Tailscale) clients still use their existing DNS. Tailscale DNS was
  not changed.
- Other LAN devices, a second client and the physical switch/AP deployment have
  not been tested. The household stays on the upstream router.

## Next Session

See [the next-session handoff](04-next-session.md). The DNS filtering milestone
is working for one verified LAN client; remaining items are listed above and in
the handoff.
