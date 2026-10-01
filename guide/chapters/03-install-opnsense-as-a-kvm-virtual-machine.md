# Chapter 3: Install OPNsense as a KVM Virtual Machine

!!! warning "Status: draft"
    Steps follow the author's own build. They are being re-run and re-verified
    before this chapter is marked verified. Expect rough edges.

- **Last verified:** not yet re-verified
- **OPNsense version:** 26.7.4_1-amd64 (or later stable release)
- **Time required:** 30–45 minutes

## Goal

Download and verify the OPNsense ISO, create a 20 GB virtual disk for the VM, define a KVM virtual machine with 2 vCPU and 4 GB RAM, and run the OPNsense installer to completion.

## Prerequisites

- Chapter 2 complete (KVM/QEMU/libvirt installed and working)
- At least 30 GB free disk space on the machine running KVM
- Approximately 30–45 minutes
- Patience during the installer (it takes ~5 minutes)

## Section 3.1: Download and Verify the OPNsense ISO

### Why Verify?

The SHA256 hash ensures the ISO you downloaded wasn't corrupted during transfer and is the real OPNsense release (not a man-in-the-middle attack). This is critical for security.

### Download Steps

On your Ubuntu host, open a terminal and navigate to a working directory:

```bash
mkdir -p ~/Downloads/opnsense-install
cd ~/Downloads/opnsense-install
```

Download the OPNsense ISO (this is ~600 MB; may take a few minutes on slower connections):

```bash
wget https://mirror.opnsense.org/releases/26.7/OPNsense-26.7.4_1-dvd-amd64.iso
```

If `wget` is not installed, use `curl` instead:

```bash
curl -O https://mirror.opnsense.org/releases/26.7/OPNsense-26.7.4_1-dvd-amd64.iso
```

Download the SHA256 hash file:

```bash
wget https://mirror.opnsense.org/releases/26.7/SHA256.txt
```

### Verify the Hash

Verify the ISO against the hash file:

```bash
sha256sum -c SHA256.txt | grep OPNsense-26.7.4_1-dvd-amd64.iso
```

**Expected output:**
```
OPNsense-26.7.4_1-dvd-amd64.iso: OK
```

If you see `OK`, the ISO is valid. If you see `FAILED`, the ISO is corrupted—delete it and download again.

???+ success "Verified: 3.1"
    - [ ] ISO downloaded: `ls -lh OPNsense-26.7.4_1-dvd-amd64.iso` shows ~600 MB
    - [ ] SHA256 verified: `sha256sum -c SHA256.txt | grep OK` (no FAILED)

### Troubleshooting 3.1

??? question "wget: command not found"
    Install wget: `sudo apt install wget`
    
??? question "Hash verification failed"
    The ISO is corrupted. Delete and re-download:
    ```bash
    rm OPNsense-26.7.4_1-dvd-amd64.iso
    wget https://mirror.opnsense.org/releases/26.7/OPNsense-26.7.4_1-dvd-amd64.iso
    sha256sum -c SHA256.txt | grep OPNsense
    ```

??? question "Should I use a different OPNsense version?"
    This guide uses 26.7.4_1 (current stable as of 2026-09-27). Later versions should work
    the same way. Earlier versions (26.1, 26.5) may have UI differences but same core steps.

---

## Section 3.2: Create the Virtual Disk

OPNsense will run from a QCOW2 disk file. QCOW2 is a sparse format: it starts small and grows as data is written. A 20 GB disk will initially be ~200 KB.

### Create the Disk

```bash
sudo qemu-img create -f qcow2 /var/lib/libvirt/images/opnsense.qcow2 20G
```

### Verify It Was Created

```bash
ls -lh /var/lib/libvirt/images/opnsense.qcow2
```

**Expected output:**
```
-rw-r--r-- 1 root root 193K Sep 30 12:34 /var/lib/libvirt/images/opnsense.qcow2
```

The file is small (~193 KB) because it's sparse. It will grow as OPNsense writes data during installation.

???+ success "Verified: 3.2"
    - [ ] Disk file created: `ls -lh /var/lib/libvirt/images/opnsense.qcow2` shows small size (~200 KB)

### Troubleshooting 3.2

??? question "Permission denied when creating disk"
    You need `sudo` to write to `/var/lib/libvirt/`. Run:
    ```bash
    sudo qemu-img create -f qcow2 /var/lib/libvirt/images/opnsense.qcow2 20G
    ```

??? question "Can I use a different disk size?"
    Yes. Common sizes:
    - 20 GB: default, enough for OPNsense + logs for months
    - 40 GB: more headroom if you add services later
    - 10 GB: minimum, but filling up will slow down the system
    
    Change the final `20G` to your desired size.

---

## Section 3.3: Create the KVM Virtual Machine

Now define the OPNsense VM to libvirt. This command creates the VM configuration (not the actual OS yet—that comes in Section 3.4).

```bash
sudo virt-install \
  --name opnsense \
  --memory 4096 \
  --vcpus 2 \
  --disk /var/lib/libvirt/images/opnsense.qcow2,format=qcow2,bus=virtio \
  --cdrom ~/Downloads/opnsense-install/OPNsense-26.7.4_1-dvd-amd64.iso \
  --os-type freebsd \
  --os-variant freebsd13 \
  --boot hd,cdrom \
  --network default \
  --noautoconsole
```

**What each flag does:**
- `--name opnsense`: VM is named "opnsense" (you'll refer to it by this name)
- `--memory 4096`: 4 GB RAM (4096 MB)
- `--vcpus 2`: 2 virtual CPUs
- `--disk`: Use the QCOW2 disk we created
- `--cdrom`: Boot from the OPNsense ISO (temporary; will be removed later)
- `--os-type freebsd`: Tell libvirt this is FreeBSD (OPNsense is based on FreeBSD)
- `--boot hd,cdrom`: Try to boot from hard disk first, then CD-ROM
- `--network default`: Connect to the default libvirt network (temporary; we'll add bridges in Chapter 4)
- `--noautoconsole`: Don't try to open a console immediately

### Verify the VM Was Created

```bash
virsh list --all
```

**Expected output:**
```
 Id   Name      State
------------------------
 -    opnsense  shut off
```

The VM exists but is not running yet ("shut off").

Also verify the VM definition:

```bash
virsh dominfo opnsense
```

**Expected output (excerpt):**
```
Name:           opnsense
UUID:           <some-uuid>
Max memory:     4194304 (4 GB in KB)
Used memory:    0
CPU(s):         2
State:          shut off
```

Also verify the disk is attached:

```bash
virsh domblklist opnsense
```

**Expected output:**
```
 Target   Source
---------------------------------------------
 vda      /var/lib/libvirt/images/opnsense.qcow2
 sda      /path/to/OPNsense-26.7.4_1-dvd-amd64.iso
```

Two devices: `vda` is the hard disk, `sda` is the ISO (CD-ROM).

???+ success "Verified: 3.3"
    - [ ] VM exists: `virsh list --all | grep opnsense` shows "opnsense  shut off"
    - [ ] Memory: `virsh dominfo opnsense | grep "Max memory"` shows 4194304 KB (4 GB)
    - [ ] Disk attached: `virsh domblklist opnsense | grep vda` shows the QCOW2 path
    - [ ] ISO attached: `virsh domblklist opnsense | grep sda` shows the ISO path

### Troubleshooting 3.3

??? question "virt-install command not found"
    It's part of the `virt-manager` package. Install:
    ```bash
    sudo apt install virt-manager
    ```

??? question "Disk already exists error"
    If `/var/lib/libvirt/images/opnsense.qcow2` already exists from a failed previous attempt:
    ```bash
    sudo rm /var/lib/libvirt/images/opnsense.qcow2
    # Then re-run qemu-img create
    ```

??? question "virt-install hangs or takes a long time"
    Normal—virt-install can take 10–30 seconds to create the VM definition. Be patient.

---

## Section 3.4: Start the VM and Run the Installer

### Boot the VM

```bash
virsh start opnsense
sleep 2
```

### Access the Console

Connect to the VM's serial console:

```bash
virsh console opnsense
```

You should see FreeBSD boot messages scrolling past. After a few seconds, you'll see:

```
Welcome to OPNsense ...
```

Followed by a menu. **Be patient** — this takes ~10 seconds.

### Run the Installer

When you see the OPNsense menu, you should see options like:

```
1. Install
2. Live
3. Reboot
```

Select **1. Install**. (Type `1` and press Enter.)

The installer will then ask:

```
Proceed with installation? [y/N]
```

Type `y` and press Enter.

### Follow the Installation

The installer will prompt you through the setup:

1. **Partition Disk**
   - Select the disk (should be `/dev/vda` or just auto-detected)
   - Choose **Guided Disk Setup (UFS)** (simplest option)
   - Confirm when prompted

2. **Partition Scheme**
   - Accept defaults (MBR, then choose partition layout)
   - Usually: **Guided** → accept recommended

3. **Continue Installation**
   - Installation proceeds (~5–10 minutes)
   - You'll see: `Extracting base...`, `Extracting kernel...`, etc.
   - **Do not interrupt this.**

4. **Reboot**
   - When complete, you'll see: `Installation finished. Reboot now?`
   - Select **Yes** or let it auto-reboot

The VM will reboot and boot from the hard disk (no longer from the ISO).

### Verify Boot from Disk

After reboot, you should see the OPNsense login prompt:

```
OPNsense 26.7.4_1-amd64 (FreeBSD 15.1-RELEASE-p3)
login:
```

**Do not log in yet.** This is just verification. Exit the console:

Press **Ctrl+]** to exit the virsh console.

???+ success "Verified: 3.4"
    - [ ] VM started: `virsh list | grep opnsense` shows running
    - [ ] Installation completed: OPNsense login prompt appears
    - [ ] Boots from disk: No ISO errors, boots cleanly after reboot

### Troubleshooting 3.4

??? question "Console shows garbled text or hangs"
    The console might be slow. Wait 10–15 seconds. If it still hangs:
    ```bash
    # Exit console: Ctrl+]
    virsh reboot opnsense
    virsh console opnsense
    # Try again
    ```

??? question "Installation fails with disk errors"
    Rare but can happen if the QCOW2 file is corrupted:
    ```bash
    virsh destroy opnsense
    virsh undefine opnsense
    sudo rm /var/lib/libvirt/images/opnsense.qcow2
    # Re-start from Section 3.2
    ```

??? question "What if I mess up the installer?"
    Just power off the VM and destroy it:
    ```bash
    virsh destroy opnsense
    virsh undefine opnsense
    sudo rm /var/lib/libvirt/images/opnsense.qcow2
    # Re-start from Section 3.2
    ```
    This is not a big deal; re-installing takes only ~15 minutes.

---

## Section 3.5: Remove the ISO and Enable Autostart

Now that OPNsense has booted from disk, we no longer need the ISO attached.

### Eject the ISO

```bash
sudo virsh detach-disk opnsense --target sda
```

(You'll be prompted to confirm; press `y` or `Enter`.)

### Reboot the VM

```bash
virsh reboot opnsense
sleep 5
```

### Verify Clean Boot from Disk

```bash
virsh console opnsense
# Should see login prompt without any ISO errors
# Exit: Ctrl+]
```

### Enable Autostart

This ensures OPNsense boots automatically when the Ubuntu host boots (e.g., after a power failure):

```bash
virsh autostart opnsense
```

Verify:

```bash
virsh dominfo opnsense | grep Autostart
# Should print: Autostart:     enable
```

???+ success "Verified: 3.5"
    - [ ] ISO detached: `virsh domblklist opnsense` shows only `vda`, no `sda`
    - [ ] Boots from disk: `virsh console opnsense` shows clean boot
    - [ ] Autostart enabled: `virsh dominfo opnsense | grep Autostart` shows "enable"

### Troubleshooting 3.5

??? question "Detach fails with 'no such disk'"
    The ISO may already be detached or named differently. Just proceed:
    ```bash
    virsh reboot opnsense
    ```

??? question "Should I create a snapshot before proceeding?"
    Yes, good idea:
    ```bash
    virsh snapshot-create-as opnsense snap-clean-install "After OPNsense install, before config"
    ```
    Then, if Chapter 4 goes wrong, you can quickly revert:
    ```bash
    virsh snapshot-revert opnsense snap-clean-install
    ```

---

## Rollback

If something goes wrong in a later chapter and you want to start over:

```bash
# Stop and remove the VM
virsh destroy opnsense
virsh undefine opnsense

# Delete the disk
sudo rm /var/lib/libvirt/images/opnsense.qcow2

# Start over from Section 3.2
```

Or, if you created a snapshot in Section 3.5:

```bash
virsh snapshot-revert opnsense snap-clean-install
# Instantly back to clean OPNsense, ready for reconfiguration
```

---

## FAQ

??? question "Can I allocate more CPU or RAM to OPNsense?"
    Yes. Common recommendations:
    - **Minimal:** 2 vCPU, 4 GB RAM (this guide's setup)
    - **Comfortable:** 4 vCPU, 6–8 GB RAM
    - **High traffic:** 8+ vCPU, 16+ GB RAM
    
    To increase after install:
    ```bash
    virsh setmem opnsense --size 8192 --config  # 8 GB
    virsh setvcpus opnsense 4 --config          # 4 vCPU
    virsh reboot opnsense
    ```

??? question "How do I see the graphical boot screen instead of serial console?"
    Serial console is simpler for headless setup. For graphical:
    
    Add VNC to the VM:
    ```bash
    virsh edit opnsense
    # Find <graphics> section; change to:
    # <graphics type="vnc" port="-1" autoport="yes" listen="0.0.0.0" />
    virsh reboot opnsense
    # Connect with: vncviewer localhost:5900
    ```

??? question "What if the download is very slow?"
    OPNsense mirrors can be overloaded. Try a different mirror:
    - https://mirror.opnsense.org/releases/26.7/
    - https://mirrors.sonic.net/opnsense/releases/26.7/
    - Check [OPNsense mirror list](https://opnsense.org/download/) for others

??? question "Can I use an older or newer OPNsense version?"
    Yes. Steps are the same. Just change the version in the URLs (e.g., `26.5` instead of `26.7`).
    Note: Some UI features may differ between versions, but the core workflow is the same.

??? question "How much disk space will OPNsense actually use?"
    A clean install is ~1 GB. After a year of logs, it might reach 5–10 GB. A 20 GB disk won't
    fill up unless you enable very verbose logging.

??? question "Is the default freebsd13 OS variant correct for newer versions?"
    As of 2026-09-27, OPNsense 26.7 uses FreeBSD 15.1. The `freebsd13` variant still works but
    is slightly out of date. In virt-install, you can use:
    ```bash
    --os-variant freebsd15  # For newer OPNsense versions
    ```
    If that doesn't exist, `freebsd13` is a safe fallback.

---

**Next:** [Chapter 4: Build the Virtual WAN/LAN Network](04-build-the-virtual-wan-lan-network.md)
