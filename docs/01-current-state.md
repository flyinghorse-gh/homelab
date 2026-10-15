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
  default route advertised; Funnel off. **Exit node: changed 2026-10-14**
  (see ADR-015): OPNsense now advertises and is approved as an exit node,
  user-reported. The earlier "exit-node mode off" is superseded.
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
  `192.168.5.1:53` → Quad9 over DNS over TLS (since 2026-10-14, ADR-016; it was
  recursive resolution before that). AdGuard's only upstream is
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
- **Logging:** query-log rotation and statistics retention are both 24 hours,
  with no ignored domains (user-reported 2026-10-03). Browsing security and
  Parental control were not enabled.
- **Remote filtering (2026-10-03):** a Tailscale grant gives the restricted
  second account `tcp:3000`, `tcp:53` and `udp:53` to `192.168.5.2`, and the
  tailnet DNS page has a custom nameserver `192.168.5.2` with Override DNS
  servers on. Verified on the Windows PC over Wi-Fi: `Resolve-DnsName
  doubleclick.net` returned `0.0.0.0`/`::` and the AdGuard Query Log showed it
  blocked with client `192.168.5.1`. Remote clients all appear as
  `192.168.5.1` because Tailscale forwards their traffic from the OPNsense LAN
  address, so per-client rules cannot tell remote devices apart. Only one PC
  was tested; phones and other devices were not.
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
- **Updated 2026-10-14 (ADR-016):** Unbound forwards to Quad9 over DoT
  (`9.9.9.9`, `149.112.112.112`, port `853`, verify `dns.quad9.net`). A capture
  on `br-wan` showed port `853` traffic to `9.9.9.9`; a 20-second port `53`
  capture showed nothing but may have been quiet. Destination IPs are still
  visible to the ISP; no anonymity is provided by DNS filtering or DoT.
- Over Tailscale, ports `53` and `3000` to `192.168.5.2` timed out while port
  `22` worked. **Resolved 2026-10-03:** the tailnet policy has two identities.
  The owner identity has all ports to OPNsense and the LAN; the second account
  was limited to `tcp:443` to OPNsense and `tcp:22` to the Ubuntu host. The
  OPNsense firewall live log showed the port-22 test as `LAN Out` from
  `192.168.5.1` (pass) and no entry at all for port 3000, so the limit was in
  the Tailscale policy, not OPNsense or the host. The grant above now allows
  the dashboard and DNS for that account. `docs/03`'s earlier "all ports"
  description was incomplete.
- **Exit node (2026-10-14, ADR-015):** the tailnet policy has a "shared exit
  node" grant (`autogroup:internet`, all ports) for both identities. The user
  confirmed OPNsense is set to offer an exit node, approved the subnet route,
  and uses the exit node from their devices (phone confirmed by the user).
  Live check from the Windows laptop (`tailscale set --exit-node=opnsense`,
  then reverted): the internet route moved from Wi-Fi to the Tailscale
  interface, internet stayed reachable, and `doubleclick.net` still returned
  `0.0.0.0` (filtering survives). The public IPv4 was identical because the
  laptop was on the home network behind the same upstream router, so this
  does not prove egress from home; a test away from home is still needed. The
  laptop was left with no exit node selected. Not checked: whether the OPNsense
  Tailscale-interface rule (any/any, see `docs/03`) or outbound NAT was changed
  for this, and whether the second account's devices use it.
- Windows with Tailscale connected sent `192.168.5.x` traffic through the
  tunnel instead of the wired link, which skewed early LAN tests. Check
  `Find-NetRoute` first.
- The test PC's wired lease was `192.168.5.90`, outside the DHCP range, which
  the WebGUI confirms is `192.168.5.100`–`192.168.5.200`. The reason is
  unexplained; a static reservation (Hosts tab) or an older lease are
  candidates and were not checked.
- A broadcast from `192.168.5.165` was blocked on the WAN interface
  ("Block private networks from WAN") on 2026-10-03. Some device on the
  upstream side uses a `192.168.5.x` address, overlapping the private LAN. Not
  identified. `docs/03` says the wizard disabled the private-network block, yet
  that rule is active.
- The Tailscale DNS override is tailnet-wide: any device that cannot reach
  `192.168.5.2` loses DNS until the setting is switched off. Rollback is
  turning off Override DNS servers in the admin console.
- Other LAN devices, a second client and the physical switch/AP deployment have
  not been tested. The household stays on the upstream router.

## Next Session

See [the next-session handoff](04-next-session.md). The DNS filtering milestone
is working for one verified LAN client; remaining items are listed above and in
the handoff.
