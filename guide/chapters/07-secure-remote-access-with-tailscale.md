# Chapter 7: Secure Remote Access with Tailscale

!!! warning "Status: verified"
    Based on Part 1 v6 DOCX (2026-09-27).

- **Last verified:** 2026-09-27

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

- **Do NOT enable exit node mode.** OPNsense is for private LAN access only.
- **Firewall rules apply.** Tailscale bypasses upstream NAT, but OPNsense firewall still protects.
- **Keep device key secure.** Revoke compromised keys in admin console.

## Rollback

In WebGUI: **Services > Tailscale > Disable**
Then remove OPNsense from Tailscale admin.

## FAQ

??? question "Why Tailscale over WireGuard?"
    Simpler (no key management), works through double NAT, free tier available.

??? question "Can friends access my homelab?"
    Not by default. You'd need to add them as Tailscale users (separate decision).

??? question "Can't connect from outside?"
    Check: OPNsense authorized in admin, daemon running, Tailscale daemon status in console.

---

**Next:** [Chapter 8: Operational Checkpoint](08-operational-checkpoint.md)
