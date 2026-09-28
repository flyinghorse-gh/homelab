# Network and Remote Access

Last updated: 2026-09-27

Source: [Part 1 v6 reference](reference/ThinkCentre_OPNsense_Self_Managed_Setup_Part_1_v6.docx).
These are recorded configuration and past test results, not fresh live checks.

## Topology and Interfaces

```text
Internet → shared upstream router (10.0.0.0/24)
         → enp1s0f0 → br-wan → OPNsense WAN (DHCP)
                               OPNsense LAN (192.168.5.1/24)
                                 → br-lan
                                   ├─ Ubuntu (192.168.5.2/24)
                                   └─ enx00e04c240c18 → LAN clients
```

The shared router continues serving other household users. Keep it in routing
mode; no bridge/passthrough or public port-forward changes are part of this
design. Ubuntu must not obtain an address on `br-wan`. Its setup default route
used USB management Wi-Fi; inspect the current route before changing anything.

| Recorded VM interface | Source | MAC | Role |
|---|---|---|---|
| `vtnet1` | `br-wan` | `52:54:00:91:08:3d` | WAN |
| `vtnet2` | `br-lan` | `52:54:00:bd:38:36` | LAN |
| `vtnet0` | libvirt `default` | `52:54:00:ca:bd:ad` | Temporary OPT1; removal unconfirmed |

Map interfaces by MAC after live inspection; do not assume numbering persists.
Built-in Ethernet was identified as Realtek RTL8111/8168. Wi-Fi inventory also
includes Intel Wireless-AC 9260 (`wlp2s0`) and Realtek RTL8723BU USB Wi-Fi
(`wlxfc221c100f59`). The latter provided the management fallback during setup.

LAN DHCP was configured for `192.168.5.100`–`192.168.5.200`. WAN received
`10.0.0.11/24` via DHCP and an IPv6 address during setup. Current WAN leases and
IPv6 firewall behavior need inspection; do not treat the observed IP as static.
The WAN wizard disabled RFC1918 blocking for the private upstream and enabled
bogon blocking. Unbound was enabled; the reference describes DNSSEC as disabled
for this stage. Exact current DNS settings remain to be checked.

The direct Windows LAN test verified DHCP, bridge forwarding, ping to both LAN
addresses, and ARP matching the OPNsense LAN MAC. It did not establish completed
switch/AP deployment or normal client Internet service: the WAN cable was
temporarily borrowed for this test. Earlier “future USB Ethernet” labels in the
DOCX precede this successful test; USB Ethernet is already recorded as tested.

## DuckDNS

`os-ddclient` uses the native backend and an external IPv4 check. Publishing the
private WAN address would be incorrect for this setup. The reference reports
that the DuckDNS hostname resolved to the same public IPv4 as an independent
IP checker. IPv6 DDNS updates were disabled.

The hostname and current service state need recording/verification. Keep the
token outside Git. Do not paste generated `ddclient.json` into documentation
or chat: it can contain credentials. DDNS does not itself open ports or bypass NAT.

## Tailscale and Management Access

- OPNsense uses `os-tailscale`; `tailscale0` is assigned as TAILSCALE without
  manually configured interface addresses.
- Recorded settings: listen port `41641`, Accept DNS off, Accept Subnet Routes
  off, no exit node. The advertised and approved route is `192.168.5.0/24` only.
- The recorded active firewall rule passes inbound traffic on TAILSCALE with
  any source, destination, and protocol. This broad interface rule is paired
  with an owner-only Tailscale Grant, not a port-restricted firewall policy.
- The Grant permits the owner's identity to access the OPNsense Tailscale IP
  and private LAN on all ports. Actual identity/IP and current policy need
  inspection; placeholders in the reference are not deployable configuration.
- OPNsense device-key expiry is disabled; personal clients use normal expiry.
- No Funnel, exit node, default-route advertisement, upstream subnet
  advertisement, or public port forward is recorded.
- HTTPS WebGUI retains default/all listen interfaces and anti-lockout enabled.
  Empty WAN rules and NAT port forwards were reported in the exposure audit;
  this historical observation is not a fresh audit of all exposure paths.

External-hotspot tests passed for OPNsense Tailscale ping, HTTPS WebGUI, and
Ubuntu SSH via `192.168.5.2`. Access also worked after the Grant restriction.
Tailscale initially used a relay and later established a direct connection.

## Recovery and Safe Verification

An encrypted OPNsense backup was downloaded before hardening. Its protected
storage location, restore procedure, and restore test are not yet documented.
Keep backup contents and credentials outside Git.

Before any network change, confirm a working recovery path, capture the current
configuration safely, and provide a rollback procedure for that specific
change. Preserve the LAN anti-lockout path and verify any Wi-Fi/SSH fallback
before relying on it. Do not remove the temporary NIC until its actual use and
OPNsense assignments are understood.

Useful read-only checks on Ubuntu:

```sh
systemctl is-enabled ssh
sudo virsh list --all
sudo virsh dominfo opnsense
sudo virsh domiflist opnsense
ip -br addr
ip route
bridge link
nmcli connection show
```

Inspect persistent VM/NetworkManager configuration as well as live state before
claiming reboot persistence. These checks were not run during this migration.
Repeat remote tests from an external network before and after access changes;
record dates, results, and limitations without saving credentials.
