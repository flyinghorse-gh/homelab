# Chapter 5: Complete OPNsense First-Time Web Configuration

!!! warning "Status: draft"
    Steps follow the author's own build. They are being re-run and re-verified
    before this chapter is marked verified. Expect rough edges.

- **Last verified:** not yet re-verified

## Goal

Access OPNsense WebGUI, complete wizard, verify WAN/LAN connectivity.

## Prerequisites

- Chapter 4 complete | Browser on Ubuntu or LAN device | 1 hour

## Section 5.1: Access WebGUI

```bash
# From Ubuntu
curl -k https://192.168.5.1
# Or: Open browser to https://192.168.5.1
# Login: root / opnsense (change this in 5.6)
```

## Section 5.2: Run Setup Wizard

1. Log in to https://192.168.5.1
2. Follow wizard: General Info → WAN (DHCP) → LAN (192.168.5.1/24) → Finish

## Section 5.3: Verify WAN

In WebGUI: **Interfaces > WAN**
- IPv4 Configuration Type: DHCP
- Status: Should show upstream IP (10.0.0.x)

Test from OPNsense console:
```bash
ping 8.8.8.8  # Should work
```

## Section 5.4: Verify LAN

In WebGUI: **Interfaces > LAN**
- IPv4 Address: 192.168.5.1, Subnet: 24
- **Services > DHCPv4 > LAN**
- Enable: checked, Range: 192.168.5.100-200

## Section 5.5: Test with LAN Device

Connect a device to LAN bridge:
```bash
# On device
dhclient eth0
ip addr show  # Should show 192.168.5.1xx
ping 8.8.8.8  # Should work (internet via OPNsense)
```

## Section 5.6: Change Password

In WebGUI: **System > Settings > Administration**
- Change root password from `opnsense` to a strong password

## Rollback

```bash
virsh snapshot-revert opnsense snap-pre-config
```

## FAQ

??? question "Why self-signed certificate?"
    Default for security. Can install real cert later.

??? question "Remote WebGUI access?"
    Not yet; restricted to 192.168.5.0/24. Chapter 7 (Tailscale) adds remote access.

---

**Next:** [Chapter 6: Dynamic DNS with DuckDNS](06-dynamic-dns-with-duckdns.md)
