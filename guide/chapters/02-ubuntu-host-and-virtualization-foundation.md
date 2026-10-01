# Chapter 2: Ubuntu Host and Virtualization Foundation

!!! success "Status: verified"
    Built and confirmed working on the author's own homelab. Your hardware and
    versions may differ slightly, so check each step's result before moving on.

- **Last verified:** 2026-09-27, on the author's build
- **Ubuntu:** 22.04 LTS or later
- **Tools:** KVM, QEMU, libvirt

## Goal

Install Ubuntu, enable KVM virtualization, set up SSH for headless management,
disable sleep, and configure auto-start on power recovery.

## Prerequisites

- Ubuntu 22.04 LTS or later installed and booting
- Keyboard, mouse, monitor (temporary)
- Network connection (Ethernet preferred)
- `sudo` access

## Section 2.1: Install KVM/QEMU/libvirt

```bash
sudo apt update
sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager
sudo usermod -aG libvirt $USER
sudo usermod -aG kvm $USER
# Log out and back in for group changes
newgrp libvirt
```

Verify:

```bash
grep -c svm /proc/cpuinfo  # AMD: should be > 0
# or
grep -c vmx /proc/cpuinfo  # Intel: should be > 0

systemctl status libvirtd  # Should show "active (running)"
virsh list --all           # Should return empty (no VMs yet)
```

???+ success "Verified: 2.1"
    - [ ] Packages installed: `dpkg -l | grep libvirt`
    - [ ] User in group: `groups | grep libvirt`
    - [ ] Virtualization detected: `grep svm/vmx /proc/cpuinfo`
    - [ ] libvirtd running: `systemctl status libvirtd`

## Section 2.2: Enable SSH for Headless Management

```bash
sudo apt install -y openssh-server openssh-client
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh
```

Find your upstream IP:

```bash
ip addr show | grep "inet " | grep -v "127.0.0.1"
# e.g., inet 10.0.0.X/24
```

From another machine:

```bash
ssh <username>@<ubuntu-ip>
# Should connect; exit when done
```

???+ success "Verified: 2.2"
    - [ ] SSH running: `systemctl status ssh`
    - [ ] Can SSH in from another machine
    - [ ] Ubuntu IP is on upstream network (10.0.0.x)

## Section 2.3: Disable Sleep and Configure Power Recovery

Prevent sleep:

```bash
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
systemctl status sleep.target  # Should show "masked"
```

Configure BIOS (the author has not yet confirmed this step on their own machine, so treat it as recommended, not verified):
1. Reboot, press F2/Del during startup
2. Find "Restore on AC Power Loss" or "Power After Power Loss"
3. Set to **On** or **Restore Last State**
4. Save and exit

???+ success "Verified: 2.3"
    - [ ] Sleep masked: `systemctl status sleep.target` shows "masked"
    - [ ] BIOS setting changed (visual confirmation)
    - [ ] Host stays awake: SSH still responsive after 5 min of inactivity

## Section 2.4: Final Verification and Reboot

```bash
echo "=== Verification ==="
systemctl status libvirtd --no-pager | head -3
systemctl status ssh --no-pager | head -3
echo "Virtualization: $(grep -c svm /proc/cpuinfo 2>/dev/null || grep -c vmx /proc/cpuinfo)"
echo "Sleep: $(systemctl status sleep.target 2>&1 | grep -c masked)"

sudo reboot
# After ~30 sec, SSH back in from another machine
ssh <username>@<ubuntu-ip>
```

## Rollback

```bash
sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target
# Revert BIOS setting: Restore on AC Power Loss → Off/Default
```

## FAQ

??? question "Why mask sleep instead of lid settings?"
    Masking works headlessly and persists across reboots.

??? question "Can I use Wi-Fi?"
    Yes, but Ethernet is more reliable for the long term.

??? question "What if virtualization isn't detected?"
    - Reboot and re-check BIOS (some boards have nested menus)
    - Update BIOS firmware from maker's support site
    - Ensure no other hypervisor (Hyper-V) is running

??? question "Do I need a static IP now?"
    Not yet; DHCP is fine. Chapter 3+ assigns static IPs to the private LAN.

??? question "Will the host overheat running 24/7?"
    Most mini PCs are rated for 24/7 operation. Check your model's specs.
    Monitor temps: `watch sensors` (install `lm-sensors` first if needed).

---

**Next:** [Chapter 3: Install OPNsense as a KVM Virtual Machine](03-install-opnsense-as-a-kvm-virtual-machine.md)
