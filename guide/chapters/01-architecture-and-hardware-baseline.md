# Chapter 1: Architecture and Hardware Baseline

!!! warning "Status: draft"
    This chapter describes the design and initial inventory. It does not require
    configuration changes. Use it to understand what you need and verify your
    hardware can run KVM.

- **Last verified:** as of 2026-09-27 (worked example only; verify your own hardware)
- **Software:** Ubuntu (any recent LTS), BIOS/firmware (any that supports AMD-V or Intel VT)

## Goal

Understand the homelab architecture, gather your hardware inventory, and verify
your mini PC can run KVM virtualization. This is a read-only chapter; you don't
change anything yet.

## Prerequisites

- A mini PC or small form-factor computer with two Ethernet ports (or one built-in
  + one USB adapter)
- Virtualization support in the CPU (AMD-V / EPYC / Ryzen, or Intel VT)
- At least 8 GB RAM (16 GB recommended)
- At least 128 GB storage (SSD recommended)
- Physical access to the machine, a keyboard, mouse, and monitor for initial setup
- An OS to install (Ubuntu 22.04 LTS or later)
- Basic Linux command-line comfort (or willingness to learn)

## Section 1.1: The Design — One Machine, Two Networks

Your homelab runs on a single mini PC:

- **Ubuntu host**: runs headlessly (no monitor) after initial setup, with SSH access.
  It hosts KVM virtualization and future services.
- **OPNsense VM**: a virtual machine that runs on KVM. It owns all routing, firewall,
  and DNS duties.
- **Shared upstream router**: your existing home router (modem + router combo, or separate).
  It stays untouched in normal mode. Other household users keep working.
- **Private LAN**: OPNsense creates a private network (`<LAN_SUBNET>` like `192.168.5.0/24`)
  that your devices will join. This is behind OPNsense, not the shared router.

### Network paths

```
    [Shared upstream router: 10.0.0.0/24]
                  |
              (port 1)
                  |
        [Ubuntu host: enp1s0f0]
                  |
            [br-wan bridge]
                  |
         [OPNsense WAN DHCP]
                  |
         [OPNsense LAN: 192.168.5.1]
                  |
            [br-lan bridge]
                  |
        [Ubuntu: USB Ethernet]
                  |
          [Your LAN devices]
```

Why this design?

- **Why two networks?** The upstream router keeps all its current functionality.
  OPNsense doesn't replace it; it sits behind it and adds a second, private
  network for your controlled devices.
- **Why virtual?** OPNsense as a VM lets you run it on cheap hardware and take
  snapshots for recovery. You can pause it without shutting down Ubuntu.
- **Why Ubuntu as the host?** It's familiar, widely supported, and has good KVM
  tooling. You'll also run future services here (DNS caching, dashboards, backups).

### What you'll control

- **Firewall rules**: block/allow traffic between your LAN and the Internet
- **DNS**: filter ads, block malware domains, or use encrypted DNS
- **VPN access**: reach your homelab securely from outside the house
- **DHCP**: assign IP addresses to your LAN devices

### What you won't touch

- The shared upstream router (it keeps serving other users)
- Modem settings (kept as-is)
- Household Wi-Fi (unless you choose to)

## Section 1.2: Hardware Discovery — Know What You Have

Before you start, document your hardware. You'll reference it later.

### On your mini PC

Open a terminal and run these commands to capture your inventory:

=== "Ubuntu command line"

    ```bash
    # Processor and RAM
    lscpu | grep -E "Model name|CPU|Stepping|Flags"
    free -h
    
    # Storage and partitions
    lsblk
    df -h
    
    # Network adapters
    ip link show
    ethtool -i enp1s0f0 2>/dev/null | head -3  # adjust interface name
    ```

Record the output in a text file. You need:

- CPU model and support for `vmx` (Intel) or `svm` (AMD)
- Total RAM
- Disk layout (NVME, SSD, HDD, and which device is which)
- All network adapter names and MAC addresses (they'll look like `enp1s0f0`, `enx...`, `wlx...`)

??? example "Illustrative inventory output (values are examples only)"

    Your output will differ. What matters is the shape of the results.

    ```
    $ lscpu | grep -E "Model name|Flags"
    Model name:   <your CPU model>
    Flags:        ... svm ...        # AMD: look for "svm"; Intel: look for "vmx"

    $ free -h
                   total        used        free
    Mem:             15Gi       2.1Gi       3.9Gi

    $ lsblk
    NAME        SIZE TYPE MOUNTPOINTS
    nvme0n1     238G disk
    ├─nvme0n1p1   1G part /boot/efi
    └─nvme0n1p2 237G part /

    $ ip link show
    2: enp1s0:  <BROADCAST,MULTICAST,UP,LOWER_UP> ...   # built-in Ethernet
    3: enx<USB_MAC>: <BROADCAST,MULTICAST> ...          # USB Ethernet adapter
    4: wlx<USB_MAC>: <BROADCAST,MULTICAST> ...          # USB Wi-Fi adapter
    ```

    Adapter names starting with `enx` or `wlx` embed the adapter's MAC address.
    Treat them like MAC addresses: keep them in your private notes, not in anything you share.

??? example "Example: Generic x86-64 system"

    If you're using a different system (ASUS NUC, HP EliteDesk, custom PC), your output
    will look similar. The key things to check:
    
    - **CPU Flags**: look for `vmx` (Intel) or `svm` (AMD). Both are fine; both enable KVM.
    - **Total RAM**: 16 GB or more is ideal. 8 GB is minimum but tight.
    - **Storage**: at least 60 GB free is good. You'll use ~20 GB for OPNsense, more for future services.
    - **Network**: one built-in Ethernet for WAN + one USB adapter for LAN is typical.

### What to do with this

Make a **local note** (NOT in Git) that records:

- Your CPU model and whether it has `vmx` or `svm` in the Flags
- Total RAM and how much is free
- Free disk space (how much is available for `/home` or the VM disk)
- The exact names of your network adapters (e.g., `enp1s0f0`, `enxYYYYYYYYYYYY`)
- The MAC addresses of your Ethernet adapters

**Do not commit or push this file.** Treat it as internal working notes. You'll use it in Chapter 2 when you configure the bridges.

## Section 1.3: Verify Virtualization Support

Virtualization must be enabled in your BIOS and your CPU must support it.

### Check the CPU

If your inventory output includes `svm` (AMD) or `vmx` (Intel) in the Flags line,
your CPU supports virtualization. If not, this design won't work on your machine.

### Check BIOS

1. **Reboot** your machine and immediately start pressing the BIOS entry key:
   - `F2` — most ThinkCentres, some HP, ASUS, Dell systems
   - `Del` — many generic Intel boards, older systems
   - `Esc` or `F12` — some HP, Lenovo models
   - Check your machine's manual if unsure.

2. Once in the BIOS, look for **Security** or **Advanced** settings. Find one of these:
   - **Intel VT-x**, **Intel Virtualization Technology**, or **VT-d** (Intel systems)
   - **AMD-V**, **SVM Mode**, or **Secure Virtual Machine** (AMD systems)

3. Make sure it is set to **Enabled**. If it says **Disabled**, change it to **Enabled**.

4. **Save and exit** (usually `Ctrl+S` or `F10`, then confirm).


### Test on Ubuntu

Once you have Ubuntu installed (Chapter 2), run:

```bash
grep -cw svm /proc/cpuinfo   # Should print > 0 (AMD)
# or
grep -cw vmx /proc/cpuinfo   # Should print > 0 (Intel)
```

If this prints `0`, virtualization is not available or not enabled.

??? tip "If virtualization is not available"

    - Check your BIOS again; the setting might be under CPU Features or Advanced.
    - Update your BIOS firmware (visit the motherboard maker's support site).
    - On some systems, Hyper-V (Windows) conflicts with KVM (Linux). Disable Hyper-V
      in Windows, then enable VT-x/SVM in BIOS.
    - Some cloud VMs and corporate machines disable virtualization entirely. You cannot
      run this homelab on them.

## Verification

This chapter is read-only. Nothing to verify yet. Once you complete it, you should have:

- [ ] Documented your CPU model and verified it supports virtualization
- [ ] Recorded your RAM and available disk space
- [ ] Listed the names of your network adapters (and stored their MAC addresses locally)
- [ ] Checked your BIOS and confirmed virtualization is enabled
- [ ] (Soon) Installed Ubuntu and confirmed KVM support with `grep` (done in Chapter 2)

## Rollback

No infrastructure changes in this chapter. Skip if not relevant.

## FAQ

??? question "Can I use an older CPU?"

    If your CPU supports AMD-V or Intel VT-x, yes:
    
    - **AMD**: Ryzen, EPYC, FX, Phenom II (Bulldozer era and later)
    - **Intel**: Core i5/i7 "Sandy Bridge" (2011) or later; some older Xeons
    - **Other**: ARM (Pi, mobile), older Atoms, Celerons — these do *not* support KVM
    
    Check your CPU model at [cpudb.stanford.edu](https://cpudb.stanford.edu) or
    your CPU vendor's ark. Search for "VT-x" or "AMD-V" in the specs.

??? question "How much RAM do I need?"

    A minimum of 8 GB works: ~2 GB for Ubuntu host, ~4–6 GB for OPNsense and a few
    clients. 16 GB or more gives you headroom for future services.

??? question "Do I need two Ethernet ports?"

    Not strictly. Configurations that work:
    
    - **Two built-in Ethernet ports** (ideal): one for WAN, one for LAN
    - **One built-in + one USB Ethernet**: the USB can bridge the LAN. This is what the
      is a common setup.
    - **One built-in + USB Wi-Fi**: the Wi-Fi can be a fallback for management, but avoid
      it for the main WAN/LAN paths.
    
    **Avoid**: Wi-Fi as your WAN or LAN bridge. It works in a pinch, but USB Ethernet or
    built-in ports are more reliable.
    
    If your mini PC has only one Ethernet port and no USB adapters available, you can
    still set it up, but you'll need to borrow a second adapter during the bridge
    configuration (Chapter 4), or use your laptop as a temporary proxy.

??? question "Can I use a Raspberry Pi or ARM machine?"

    No. The guide assumes x86-64 and Linux KVM. ARM systems (Pi, some cloud instances)
    do not support the required virtualization mode.

??? question "Why not just run OPNsense directly on the machine?"

    You *could*, but then you lose the flexibility to:
    - Take snapshots and roll back OPNsense safely
    - Run future services on Ubuntu alongside it
    - Pause OPNsense without shutting down the machine
    - Use different storage for the firewall VM (easier backups)

??? question "What if my shared router is a modem/router combo?"

    That's fine. The shared router can be a single device or two separate devices.
    The design works the same: OPNsense sits downstream of it, not replacing it.

??? question "What hardware should I buy?"

    Any fanless or low-power x86-64 mini PC with two Ethernet ports:
    
    - **Author's build**: a Lenovo ThinkCentre mini PC with an AMD CPU
    - **Also good**: ASUS NUC (11th gen or later, with i5/i7; some models have only one
      Ethernet), HP EliteDesk G7/G8, Zotac ZBOX (some models), custom Intel mini-ITX builds
    - **Avoid**: Fanless Atoms, ARM boards, cloud VMs with virtualization disabled
    
    Requirements:
    - Intel VT-x or AMD-V support (check CPU specs before buying)
    - At least 8 GB RAM (16 GB recommended)
    - At least 128 GB storage (256 GB SSD ideal)
    - Two Ethernet ports, or one port + willingness to buy a USB adapter (~$15)
    - Quiet and efficient (fanless is nice but not required)
    
    Budget: $300–600 used, $500–1000 new. Refurbished ThinkCentres and EliteDesks are
    often good value on eBay.

??? question "Is this design secure?"

    It depends on your threat model. OPNsense adds:
    - Firewall rules (blocks unwanted inbound traffic)
    - DNS filtering (blocks malware domains)
    - VPN access (secure remote reach)

    It does *not* protect against:
    - Compromises of the shared router (the upstream machine)
    - Attacks on devices already on your network
    - Misconfigured firewall rules

    Later chapters harden the setup (Chapters 7–8). Start simple and test at each step.
