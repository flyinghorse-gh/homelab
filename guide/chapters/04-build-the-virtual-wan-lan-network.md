# Chapter 4: Build the Virtual WAN/LAN Network

!!! success "Status: verified"
    The finished result below (bridges, addresses, VM network cards) was
    checked on the author's server on 2026-09-30. The commands create the same
    profiles you will see in the expected output.

- **Last verified:** 2026-09-30, on the author's build (Ubuntu with NetworkManager)
- **Time required:** 30–45 minutes

## Goal

Create two Linux bridges on the Ubuntu host and plug OPNsense's two virtual
network cards into them:

- **br-wan** links OPNsense's WAN card to the physical port facing your home router.
- **br-lan** links OPNsense's LAN card to a second physical port for your private network,
  and gives the Ubuntu host its management address on that network.

## Prerequisites

- Chapter 3 complete (OPNsense VM installed)
- Two physical network adapters: one built-in Ethernet port and one more
  (a second port or a USB Ethernet adapter)
- **A way into the host that does not depend on the WAN port.** Putting the WAN
  port into a bridge removes its IP address from the host, which cuts any SSH
  session running over it. The author used a USB Wi-Fi adapter on the home
  network as the fallback. A monitor and keyboard on the host also work.

## Background: What Is a Bridge?

A Linux **bridge** is a virtual network switch inside the host. It connects
physical ports and virtual machine network cards so that they behave as if
they were plugged into the same switch.

Why two? OPNsense needs a WAN side and a LAN side. The host's WAN port must not
give the host an Internet address, otherwise the host would bypass the firewall.

## Section 4.1: Identify Your Network Adapters

On the **Ubuntu host**:

```bash
ip -br link
```

Illustrative output (your names differ; MACs hidden):

```
lo               UNKNOWN   00:00:00:00:00:00
enp1s0f0         UP        <MAC>      <- built-in Ethernet  (WAN)
wlp2s0           DOWN      <MAC>      <- built-in Wi-Fi
enx<USB_MAC>     DOWN      <MAC>      <- USB Ethernet       (LAN)
wlx<USB_MAC>     UP        <MAC>      <- USB Wi-Fi          (fallback access)
```

Names starting `enx` and `wlx` contain the adapter's MAC address, so treat
them as private and never paste them online.

Pick your roles and write them down:

```
WAN_NIC = the built-in Ethernet port that plugs into your home router
LAN_NIC = the second Ethernet adapter for your private network
```

A `DOWN` or `NO-CARRIER` status on the LAN adapter just means no cable is
plugged in yet. That is fine for now.

???+ success "Verified: 4.1"
    - [ ] You can name the WAN adapter and the LAN adapter
    - [ ] You have a way into the host that is not the WAN adapter

## Section 4.2: Create br-wan

Ubuntu Desktop and many Ubuntu installs manage networking with NetworkManager.
Bridges made with `nmcli` survive reboots. On the **Ubuntu host**:

```bash
nmcli con show                                  # note the current profile names
```

Create the bridge with no IP address for the host, then add the WAN adapter:

```bash
sudo nmcli con add type bridge ifname br-wan con-name br-wan \
  ipv4.method disabled ipv6.method disabled

sudo nmcli con add type ethernet ifname <WAN_NIC> con-name br-wan-port \
  master br-wan slave-type bridge
```

If you were connected over the WAN port, your SSH session ends here. Reconnect
through your fallback path. To bring the bridge up:

```bash
sudo nmcli con up br-wan
sudo nmcli con up br-wan-port
```

The host intentionally has **no IP address** on `br-wan`. OPNsense itself will
request one from your home router.

???+ success "Verified: 4.2"
    - [ ] `ip -br addr show br-wan` shows state `UP` with no IP address
    - [ ] `nmcli con show` lists `br-wan` (bridge) and `br-wan-port` (ethernet)

## Section 4.3: Create br-lan

Create the bridge with the host's management address, then add the LAN adapter:

```bash
sudo nmcli con add type bridge ifname br-lan con-name br-lan \
  ipv4.method manual ipv4.addresses 192.168.5.2/24 \
  ipv4.never-default yes ipv6.method disabled

sudo nmcli con add type ethernet ifname <LAN_NIC> con-name br-lan-usb \
  master br-lan slave-type bridge

sudo nmcli con up br-lan
```

Why `ipv4.never-default yes`? It tells the host never to use this network as
its route to the Internet. The host keeps using its normal connection for that.

Check:

```bash
ip -br addr show br-lan
nmcli -f connection.id,ipv4.never-default,ipv4.addresses con show br-lan
```

Expected:

```
br-lan           UP             192.168.5.2/24
connection.id:                          br-lan
ipv4.never-default:                     yes
ipv4.addresses:                         192.168.5.2/24
```

???+ success "Verified: 4.3"
    - [ ] `br-lan` is `UP` with `192.168.5.2/24`
    - [ ] `ipv4.never-default` is `yes`

## Section 4.4: Attach the Bridges to the OPNsense VM

Attach WAN first, then LAN. The order matters because OPNsense names its
cards in the order it finds them (`vtnet0` is the first, `vtnet1` the second).

```bash
virsh attach-interface opnsense --type bridge --source br-wan --model virtio --persistent
virsh attach-interface opnsense --type bridge --source br-lan --model virtio --persistent
virsh domiflist opnsense
```

Expected (MACs differ):

```
 Interface   Type     Source    Model    MAC
-----------------------------------------------------------
 vnet0       bridge   br-wan    virtio   52:54:00:xx:xx:xx
 vnet1       bridge   br-lan    virtio   52:54:00:xx:xx:xx
```

???+ success "Verified: 4.4"
    - [ ] `virsh domiflist opnsense` lists exactly two cards: br-wan then br-lan
    - [ ] No leftover `default` network card is listed

??? question "I see a third card on the `default` network"
    Remove it so nothing bypasses the firewall:
    `virsh detach-interface opnsense network --mac <that-MAC> --persistent`

## Section 4.5: Tell OPNsense Which Card Is Which

Restart the VM and open its console (VNC through an SSH tunnel as in
Chapter 3, or `virsh console opnsense` if the serial console is enabled):

```bash
virsh reboot opnsense
```

At the OPNsense menu choose **1) Assign interfaces**:

- WAN = `vtnet0` (the first card, on `br-wan`)
- LAN = `vtnet1` (the second card, on `br-lan`)

Then choose **2) Set interface IP address**:

- **WAN:** DHCP (your home router provides the address)
- **LAN:** `192.168.5.1`, subnet 24, no upstream gateway, enable the DHCP server
  with the range `192.168.5.100` to `192.168.5.200`

If unsure which card is which, compare the MACs in the OPNsense menu with the
`virsh domiflist` output.

???+ success "Verified: 4.5"
    - [ ] OPNsense console shows WAN with an address from your home router
    - [ ] OPNsense console shows LAN `192.168.5.1/24`

## Section 4.6: Test

From the **Ubuntu host**:

```bash
ping -c 3 192.168.5.1       # OPNsense LAN
```

From a **computer plugged into the LAN adapter** (optional but recommended):
it should receive an address from `192.168.5.100`–`192.168.5.200` and be able
to ping `192.168.5.1` and `192.168.5.2`.

???+ success "Verified: 4.6"
    - [ ] Ubuntu pings `192.168.5.1`
    - [ ] A LAN computer gets a DHCP address and pings both `.1` and `.2`

## Reboot Check

Bridges made with `nmcli` are permanent. Prove it: `sudo reboot`, wait a
minute, reconnect, and confirm `ip -br addr show br-lan` still shows
`192.168.5.2/24` and `virsh list --all` shows OPNsense running.

## Rollback

On the **Ubuntu host**:

```bash
virsh detach-interface opnsense bridge --mac <WAN-MAC> --persistent
virsh detach-interface opnsense bridge --mac <LAN-MAC> --persistent

sudo nmcli con delete br-lan-usb br-lan br-wan-port br-wan
nmcli con show                       # find your original Ethernet profile
sudo nmcli con up "<original-profile-name>"
```

## FAQ

??? question "Do I really need two physical adapters?"
    For this design, yes: one faces your home router, one faces your private
    network. A USB Ethernet adapter (about $15) is the common choice.

??? question "Can I use Wi-Fi for the WAN or LAN side?"
    Wi-Fi cannot be bridged the same way. Use Ethernet for both. A Wi-Fi
    adapter is handy as an emergency way into the host, as the author does.

??? question "What is the `virbr0` interface?"
    libvirt's built-in NAT network. This guide does not use it. Leaving it
    alone is harmless.

??? question "Can I use a different LAN subnet?"
    Yes, any private range, as long as you use it consistently.

??? question "My SSH session died in 4.2"
    Expected when the WAN port was your connection. Reconnect through the
    fallback adapter, or use a keyboard and monitor.

---

**Next:** [Chapter 5: Complete OPNsense First-Time Web Configuration](05-complete-opnsense-first-time-web-configuration.md)
