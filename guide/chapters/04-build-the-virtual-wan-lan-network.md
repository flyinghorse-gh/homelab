# Chapter 4: Build the Virtual WAN/LAN Network

!!! warning "Status: working design, commands being re-checked"
    The author built this and it works. The exact commands below are being
    re-run on the server one by one before this chapter is marked verified.

- **Last verified:** design confirmed 2026-09-27; command syntax pending re-run
- **Time required:** 30–45 minutes

## Goal

Create two Linux bridges on Ubuntu to connect OPNsense's virtual network interfaces to your physical Ethernet adapters: one for WAN (upstream Internet) and one for LAN (private network).

## Prerequisites

- Chapter 3 complete (OPNsense VM booting)
- Two physical network adapters (one built-in Ethernet, one USB or second built-in)
- 30–45 minutes
- Understanding from Chapter 1 of why two networks are needed

## Background: What Are Bridges?

A Linux **bridge** is a virtual network switch. It forwards network packets between:
- Physical Ethernet ports (your NICs)
- Virtual machine network interfaces

**br-wan:** Connects OPNsense's WAN (virtual) interface to your upstream router's physical port
**br-lan:** Connects OPNsense's LAN (virtual) interface to your private devices' physical port

Without bridges, the VMs couldn't send/receive data from physical networks.

---

## Section 4.1: Identify Your Network Adapters

Find the names of your two Ethernet adapters.

### List All Adapters

```bash
ip link show
```

**Look for:**
- **Ethernet adapters:** Named like `enp1s0f0`, `enp1s0f1`, `enx<USB_MAC>`
- **Wi-Fi adapters:** Named like `wlx<USB_MAC>` (avoid for bridges)
- Skip `lo` (loopback)

### Example Output

```
2: enp1s0f0: <BROADCAST,MULTICAST,UP,LOWER_UP>
3: enp1s0f1: <BROADCAST,MULTICAST>
4: enx<USB_MAC>: <BROADCAST,MULTICAST>
5: wlx<USB_MAC>: <BROADCAST,MULTICAST>
```

### Assign Roles

**WAN adapter** (currently connected to home router):
- Check which has internet: `ip addr show enp1s0f0` (shows IP = connected)
- Example: `enp1s0f0`

**LAN adapter** (for private network, can be unused now):
- USB Ethernet or second built-in
- Example: `enx<USB_MAC>`

**Write down your names:**
```
WAN:  <WAN_NIC>
LAN:  <LAN_NIC>
```

???+ success "Verified: 4.1"
    - [ ] Listed adapters: `ip link show` shows at least 2 Ethernet
    - [ ] Identified WAN (connected to home router)
    - [ ] Identified LAN (USB or second port)

---

## Section 4.2: Create br-wan Bridge

Create a bridge for the WAN side and attach your upstream Ethernet adapter.

### Create and Enable Bridge

```bash
sudo ip link add br-wan type bridge
sudo ip link set br-wan up
```

### Add WAN Adapter to Bridge

Replace `<WAN_NIC>` with your actual name (e.g., `enp1s0f0`):

```bash
sudo ip link set <WAN_NIC> master br-wan
sudo ip link set <WAN_NIC> up
```

### Verify

```bash
ip link show br-wan
```

Should show `state UP` and your adapter as `master br-wan`.

???+ success "Verified: 4.2"
    - [ ] Bridge created: `ip link show | grep br-wan`
    - [ ] Adapter added: `ip link show | grep <WAN_NIC>` shows `master br-wan`
    - [ ] State is UP

---

## Section 4.3: Create br-lan Bridge

Create a bridge for your private LAN and assign Ubuntu's management IP.

### Create and Enable Bridge

```bash
sudo ip link add br-lan type bridge
sudo ip link set br-lan up
```

### Add LAN Adapter to Bridge

Replace `<LAN_NIC>` with your actual name (e.g., `enx<USB_MAC>`):

```bash
sudo ip link set <LAN_NIC> master br-lan
sudo ip link set <LAN_NIC> up
```

### Assign Ubuntu Management IP

```bash
sudo ip addr add 192.168.5.2/24 dev br-lan
```

### Verify

```bash
ip addr show br-lan
```

Should show:
- state UP
- `inet 192.168.5.2/24`

???+ success "Verified: 4.3"
    - [ ] Bridge created and UP
    - [ ] Adapter added as master
    - [ ] Ubuntu IP is 192.168.5.2/24

---

## Section 4.4: Attach Bridges to OPNsense VM

Tell OPNsense to use these bridges.

### Attach WAN Bridge

```bash
sudo virsh attach-interface opnsense \
  --type bridge --source br-wan \
  --model virtio --persistent
```

### Attach LAN Bridge

```bash
sudo virsh attach-interface opnsense \
  --type bridge --source br-lan \
  --model virtio --persistent
```

### Verify Attached

```bash
virsh domiflist opnsense
```

Should show:
- One interface connected to `br-wan`
- One interface connected to `br-lan`

**Note the MAC addresses** of these two interfaces; you'll use them to identify WAN vs LAN in OPNsense.

???+ success "Verified: 4.4"
    - [ ] Interfaces attached: `virsh domiflist opnsense` shows both bridges
    - [ ] Noted MAC addresses for WAN and LAN interfaces

---

## Section 4.5: Configure OPNsense to Use Bridges

Boot OPNsense and configure which interface is WAN and which is LAN.

### Reboot to Detect Interfaces

```bash
virsh reboot opnsense
sleep 5
```

### Access Console

```bash
virsh console opnsense
```

### Configure Interfaces

At the prompt, select the option to **assign interfaces** or **configure network** (usually option 1–2).

OPNsense will show detected network interfaces with MAC addresses. Match them:
- **WAN interface:** The MAC from br-wan (you noted this in 4.4)
- **LAN interface:** The MAC from br-lan

Assign accordingly:
- **WAN:** Set to DHCP (gets IP from your upstream router)
- **LAN:** Set to static `192.168.5.1/24`

Enable DHCP on LAN for client pool: `192.168.5.100–192.168.5.200`.

Save and exit. OPNsense reboots.

### Verify Boot

After reboot, you should see login prompt with no errors.

Exit console: **Ctrl+]**

???+ success "Verified: 4.5"
    - [ ] Interfaces configured in OPNsense
    - [ ] WAN is DHCP
    - [ ] LAN is 192.168.5.1/24 with DHCP enabled

---

## Section 4.6: Test Connectivity

### From Ubuntu

```bash
ping 192.168.5.1
```

Should succeed. If it fails, check that OPNsense LAN is set to 192.168.5.1/24.

### From LAN Device (Optional)

Plug a computer into the LAN adapter:
```bash
ping 192.168.5.1   # OPNsense
ping 192.168.5.2   # Ubuntu
ping 8.8.8.8       # Internet
```

All should work.

???+ success "Verified: 4.6"
    - [ ] Ubuntu → OPNsense ping works
    - [ ] (Optional) LAN device gets DHCP + ping succeeds

---

## Rollback

```bash
virsh detach-interface opnsense --type bridge --source br-wan --persistent
virsh detach-interface opnsense --type bridge --source br-lan --persistent

sudo ip addr del 192.168.5.2/24 dev br-lan
sudo ip link set br-lan down && sudo ip link del br-lan
sudo ip link set br-wan down && sudo ip link del br-wan
```

---

## FAQ

??? question "Do I need two physical adapters?"
    Yes, for this guide. Alternatives:
    - Use VLAN tagging on one adapter (advanced)
    - USB Ethernet adapter (~$15, recommended if you only have one built-in)

??? question "My Wi-Fi adapter only?"
    Not ideal for WAN/LAN paths; too unreliable. Use Ethernet if possible.

??? question "What if I don't have a spare LAN device to test?"
    The key test is: `ping 192.168.5.1` from Ubuntu. If that works, bridges are good.
    Full LAN testing comes in Chapter 5.

??? question "Should I make bridges permanent?"
    For now, they're temporary (recreated at reboot). A later chapter will cover making them
    permanent in `/etc/network/interfaces` or Netplan.

??? question "Can I use a different LAN subnet?"
    Yes. Use `192.168.100.0/24` or any private range. Just be consistent everywhere.

---

**Next:** [Chapter 5: Complete OPNsense First-Time Web Configuration](05-complete-opnsense-first-time-web-configuration.md)
