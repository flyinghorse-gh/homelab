# Chapter 4: Build the Virtual WAN/LAN Network

!!! warning "Status: verified"
    Based on Part 1 v6 DOCX (2026-09-27).

- **Last verified:** 2026-09-27
- **Linux bridges:** br-wan, br-lan

## Goal

Create two Linux bridges to connect OPNsense virtual interfaces to physical Ethernet ports.

## Prerequisites

- Chapter 3 complete | Two network adapters | 1–2 hours

## Section 4.1: Identify Adapters

```bash
ip link show
# Note two adapter names: e.g., enp1s0f0 (WAN) and enxYYYYYYYYYYYY (LAN)
```

## Section 4.2: Create br-wan

```bash
sudo ip link add br-wan type bridge
sudo ip link set br-wan up
sudo ip link set <WAN_NIC> master br-wan
sudo ip link set <WAN_NIC> up
ip link show | grep -A2 "br-wan"
```

## Section 4.3: Create br-lan

```bash
sudo ip link add br-lan type bridge
sudo ip link set br-lan up
sudo ip link set <LAN_NIC> master br-lan
sudo ip link set <LAN_NIC> up
sudo ip addr add 192.168.5.2/24 dev br-lan
ip addr show br-lan
```

## Section 4.4: Attach to OPNsense

```bash
sudo virsh attach-interface opnsense --type bridge --source br-wan --target virtio --persistent
sudo virsh attach-interface opnsense --type bridge --source br-lan --target virtio --persistent
virsh domiflist opnsense
```

## Section 4.5: Configure in OPNsense

Boot OPNsense:

```bash
virsh console opnsense
# Option 2: Configure interfaces interactively
# Assign: WAN = DHCP from upstream; LAN = 192.168.5.1/24
# Enable LAN DHCP for 192.168.5.100-200
```

## Section 4.6: Verify

```bash
ping 192.168.5.1  # From Ubuntu; should work
# Connect LAN device: should get 192.168.5.100+ and ping both IPs and Internet
```

## Rollback

```bash
virsh detach-interface opnsense --type bridge --mac <MAC_OF_WAN>
virsh detach-interface opnsense --type bridge --mac <MAC_OF_LAN>
sudo ip link set br-wan down; sudo ip link del br-wan
sudo ip link set br-lan down; sudo ip link del br-lan
```

## FAQ

??? question "Which interface is WAN vs LAN?"
    `virsh domiflist opnsense` shows MACs. Match them to console output in OPNsense.

??? question "Can I use one NIC with VLANs?"
    Yes, but more complex. Two adapters is simpler for beginners.

---

**Next:** [Chapter 5: Complete OPNsense First-Time Web Configuration](05-complete-opnsense-first-time-web-configuration.md)
