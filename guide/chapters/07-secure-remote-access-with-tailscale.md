# Chapter 7: Secure Remote Access with Tailscale

!!! success "Status: verified"
    Built and confirmed working on the author's own homelab. Your hardware and
    versions may differ slightly, so check each step's result before moving on.

- **Last verified:** 2026-09-27, on the author's build

## Goal

Install Tailscale to securely reach OPNsense and Ubuntu from outside your network.

## Prerequisites

- Chapter 6 complete | Tailscale account (free) from https://tailscale.com | 1 hour

## Section 7.1: Create Tailscale Account

1. Go to https://tailscale.com
2. Sign in or create account
3. Generate/note auth key from admin console

## Section 7.2: Install on OPNsense

In WebGUI:

1. **System > Firmware > Plugins**
2. Install `os-tailscale`
3. Reboot OPNsense
4. **Services > Tailscale > Settings**
5. Enable: checked, Auth Key: paste yours
6. Click Enable Tailscale

## Section 7.3: Configure Subnets

In WebGUI: **Services > Tailscale > Subnets**

- Advertise Subnets: `192.168.5.0/24` (your private LAN)
- Advertise Exit Node: **unchecked** (important!)
- Save

## Section 7.4: Authorize in Tailscale Admin

1. Go to https://login.tailscale.com/admin/machines
2. Find and authorize the OPNsense machine
3. Note Tailscale IP (e.g., 100.x.y.z)

## Section 7.5: Test Remote Access

From external network (phone on cellular, laptop at cafe):

1. Install Tailscale app and sign in
2. Browser: `https://100.x.y.z/` (OPNsense Tailscale IP)
3. You should reach OPNsense WebGUI remotely

Also SSH:
```bash
ssh <user>@100.a.b.c  # Ubuntu Tailscale IP
```

## Important Security

- **Exit node is optional and off by default.** An exit node sends *all* of a
  device's internet traffic through your home connection. Leave it off until
  you want that. The author turned it on later and checked that DNS filtering
  (Chapter 8) still works with it; see the optional note below.
- **Firewall rules apply.** Tailscale bypasses upstream NAT, but OPNsense firewall still protects.
- **Keep device key secure.** Revoke compromised keys in admin console.

## Rollback

In WebGUI: **Services > Tailscale > Disable**
Then remove OPNsense from Tailscale admin.

## FAQ

??? question "Why Tailscale over WireGuard?"
    Simpler (no key management), works through double NAT, free tier available.

??? question "What is an exit node, and should I turn it on?"
    An *exit node* is a device on your tailnet that other devices can send all
    their internet traffic through. Sites then see your home connection's
    address, and the speed is limited by your home upload speed. It is
    optional. If you turn it on, you must advertise it in the OPNsense
    Tailscale settings, approve it in the Tailscale admin console, and have a
    policy rule allowing `autogroup:internet`. On the device, select it
    (`tailscale set --exit-node=<MACHINE_NAME>`) and undo it with
    `tailscale set --exit-node=`. Check that the device's internet route uses
    the `Tailscale` interface and that DNS filtering still works. If the
    device is on your home network, the public IP will not change, so test it
    away from home to prove it. *(Planned: the author's away-from-home test is
    not finished yet.)*

??? question "Can friends access my homelab?"
    Not by default. You'd need to add them as Tailscale users (separate decision).

??? question "Can't connect from outside?"
    Check: OPNsense authorized in admin, daemon running, Tailscale daemon status in console.

---

**Next:** [Chapter 8: Network-wide DNS Filtering](08-network-wide-dns-filtering.md)
