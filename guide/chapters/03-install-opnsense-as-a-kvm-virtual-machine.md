# Chapter 3: Install OPNsense as a KVM Virtual Machine

!!! warning "Status: verified"
    Based on Part 1 v6 DOCX (2026-09-27).

- **Last verified:** 2026-09-27
- **OPNsense version:** 26.7.4_1-amd64

## Goal

Download OPNsense, create a 20 GB KVM VM (2 vCPU, 4 GB RAM), and run the installer.

## Prerequisites

- Chapter 2 complete (KVM working) | ~30 GB free disk space | 1–2 hours

## Section 3.1: Download and Verify

```bash
cd ~/Downloads
wget https://mirror.opnsense.org/releases/26.7/OPNsense-26.7.4_1-dvd-amd64.iso
wget https://mirror.opnsense.org/releases/26.7/SHA256.txt
sha256sum -c SHA256.txt | grep OPNsense
# Should print: "OK"
```

## Section 3.2: Create VM

```bash
sudo qemu-img create -f qcow2 /var/lib/libvirt/images/opnsense.qcow2 20G
sudo virt-install --name opnsense --memory 4096 --vcpus 2 \
  --disk /var/lib/libvirt/images/opnsense.qcow2,format=qcow2 \
  --cdrom ~/Downloads/OPNsense-26.7.4_1-dvd-amd64.iso \
  --os-type freebsd --os-variant freebsd13 --network default --noautoconsole
virsh list --all  # Should show "opnsense"
```

## Section 3.3: Install

```bash
virsh start opnsense
virsh console opnsense
# Select: Install (UFS) > Guided Disk > Default
# Exit console: Ctrl+]
```

## Section 3.4: Finalize

```bash
virsh detach-disk opnsense --target sda
virsh reboot opnsense
virsh autostart opnsense
```

## Rollback

```bash
virsh destroy opnsense; virsh undefine opnsense
rm /var/lib/libvirt/images/opnsense.qcow2
```

## FAQ

??? question "More resources?"
    `virsh setmem opnsense --size 6144 --config` (6 GB)
    `virsh setvcpus opnsense 4 --config` (4 CPU)

??? question "Snapshot for safety?"
    `virsh snapshot-create-as opnsense snap-pre-config "Before config"`

---

**Next:** [Chapter 4: Build the Virtual WAN/LAN Network](04-build-the-virtual-wan-lan-network.md)
