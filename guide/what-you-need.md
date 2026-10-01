# What You Need Before Starting

Checklist of hardware, accounts, and time before you begin.

## Hardware

- **A mini PC or small form factor computer** (~$300–1000 used or new)
  - Intel or AMD x86-64 processor with virtualization support (AMD-V or Intel VT-x)
  - At least 8 GB RAM (16 GB recommended for headroom)
  - At least 128 GB storage, SSD recommended (NVME preferred)
  - **Two network ports:** either two built-in Ethernet, or one built-in + one USB adapter
  - Quiet/fanless is nice but not required

- **Author's build:** a Lenovo ThinkCentre M715q mini PC (AMD)
- **Other good options:** ASUS NUC (11th gen+), HP EliteDesk G7/G8, custom Intel mini-ITX

- **For setup:** Keyboard, mouse, monitor (can be temporary; goes headless after Chapter 2)
- **Network:** One Ethernet cable to connect the mini PC during setup

## Accounts (Free)

- **DuckDNS** — dynamic DNS hostname so your public IP changes don't break remote access
  - Go to [duckdns.org](https://www.duckdns.org/) and sign up
  - Creates a free hostname like `<myname>.duckdns.org`
  - Keep your token secret; never commit it to Git

- **Tailscale** — secure VPN for remote access to your homelab
  - Go to [tailscale.com](https://tailscale.com/) and sign up
  - Free tier supports one user with unlimited devices
  - Personal devices stay on your Tailnet; OPNsense advertises your private LAN

## Existing Network

- Your home router (modem + router, or separate) stays as-is
  - No need to change settings
  - Household users keep working without interruption
  - The homelab sits behind it (double NAT)

## Time

- **Reading time:** 30 min per chapter on average
- **Hands-on time:** 1–2 hours per chapter for configuration and verification
- **Total (all 8 chapters):** ~12–18 hours spread over days/weeks
- **No rush:** you can stop and resume; each chapter is self-contained

## Linux Comfort

- **Required:** Basic terminal comfort (typing commands, reading output)
- **Not required:** Linux administration experience, networking expertise, or systemd knowledge
- **Helpful:** Willingness to Google errors and read docs when stuck

## A Computer to Follow Along From

You'll use a separate machine (Windows, Mac, or Linux) to:
- SSH into the Ubuntu host
- Open the OPNsense WebGUI over Tailscale
- Read this guide
- Copy-paste commands

This can be a laptop, desktop, or phone (Tailscale mobile client works great).

---

**Have everything?** Start with [Chapter 1: Architecture and Hardware Baseline](chapters/01-architecture-and-hardware-baseline.md).
