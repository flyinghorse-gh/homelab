# Chapter 8: Operational Checkpoint

!!! warning "Status: verified"
    Based on Part 1 v6 DOCX (2026-09-27).

- **Last verified:** 2026-09-27

## Goal

Verify all infrastructure works reliably and create backups before moving to DNS filtering.

## Section 8.1: Verification Checklist

**On Ubuntu:**
```bash
systemctl status libvirtd ssh
ip addr show br-wan br-lan
virsh list
```

**On OPNsense:**
```bash
virsh console opnsense
# ifconfig  (WAN IP + LAN 192.168.5.1)
# ping 8.8.8.8  (Internet access)
```

**From LAN device:**
```bash
ping 192.168.5.1   # OPNsense
ping 192.168.5.2   # Ubuntu
ping 8.8.8.8       # Internet
```

**Tailscale (external):**
- Can reach OPNsense WebGUI via Tailscale IP
- Can SSH to Ubuntu via Tailscale IP

## Section 8.2: Create Backups

```bash
# VM definition
virsh dumpxml opnsense > ~/opnsense-backup-$(date +%Y%m%d).xml

# OPNsense config (via WebGUI)
# System > Backup & Restore > Backup Configuration
# Download encrypted .xml file (keep password safe, not in Git)

# Store backups outside Git in protected location
```

## Section 8.3: Document Current State

Update your project docs with:
- Ubuntu version, OPNsense version
- IP ranges, hostnames, Tailscale network
- Any customizations

## Section 8.4: What's Next

**Chapter 9:** DNS filtering / ad blocking

You'll compare Unbound vs AdGuard Home, configure blocklists, and test blocking.

## Rollback

```bash
# Restore VM from snapshot
virsh snapshot-revert opnsense snap-pre-config

# Or restore OPNsense config (WebGUI)
```

## FAQ

??? question "Keep backups forever?"
    Keep one recent backup. Delete older ones after confirming new setup works.

??? question "Move to different hardware?"
    VM XML + OPNsense config backup allow recreation on another Ubuntu host.

---

**Next:** [Chapter 9: Network-wide DNS Filtering](09-network-wide-dns-filtering.md)
