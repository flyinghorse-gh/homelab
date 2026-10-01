# Chapter 3: Install OPNsense as a KVM Virtual Machine

!!! success "Status: verified"
    The finished virtual machine below, including autostart, was checked on the
    author's server with `virsh dumpxml` and `virsh dominfo`.

- **Last verified:** 2026-10-01, VM definition and autostart checked on the author's build
- **OPNsense version:** 26.7 (the author's install reports 26.7.4_1)
- **Time required:** 30–45 minutes

## Goal

Download and verify the OPNsense installer, create a 20 GB virtual disk, define
a KVM virtual machine (2 vCPUs, 4 GB RAM), install OPNsense onto the disk, and
make the VM start by itself whenever the host boots.

## Prerequisites

- Chapter 2 complete (KVM, QEMU and libvirt working)
- At least 30 GB of free disk space on the host
- A second computer to view the installer screen (see 3.4)

## Section 3.1: Download and Verify the Installer

**Why verify?** A checksum proves the file was not corrupted or tampered with.
The firewall protects your whole network, so start from a file you can trust.

1. On your other computer or the host, open the official download page:
   <https://opnsense.org/download/>.
2. Choose architecture **amd64**, image type **dvd**, and a mirror near you.
   You get a file such as `OPNsense-26.7-dvd-amd64.iso.bz2`, plus a checksum
   file listed next to it on the same mirror.
3. Put both files on the Ubuntu host, for example in `~/Downloads`.

On the **Ubuntu host**:

```bash
cd ~/Downloads
sha256sum OPNsense-*-dvd-amd64.iso.bz2     # compare with the checksum file
bunzip2 OPNsense-*-dvd-amd64.iso.bz2       # skip if you downloaded a plain .iso
ls -lh OPNsense-*-dvd-amd64.iso            # about 2 GB
```

Compare the hash printed by `sha256sum` with the line for your file in the
checksum file. They must be identical. If they differ, delete the file and
download again.

Copy the ISO to the folder libvirt is allowed to read:

```bash
sudo cp OPNsense-*-dvd-amd64.iso /var/lib/libvirt/images/
```

???+ success "Verified: 3.1"
    - [ ] Hash matches the one published by OPNsense
    - [ ] `sudo ls -lh /var/lib/libvirt/images/` shows the ISO (about 2 GB)

??? question "wget or curl: which should I use?"
    Either works. A browser download is fine too; the checksum is what matters.

??? question "The file ends in .bz2. Is that normal?"
    Yes. The mirrors ship the ISO compressed. `bunzip2` unpacks it.

## Section 3.2: Create the Virtual Disk

```bash
sudo qemu-img create -f qcow2 /var/lib/libvirt/images/opnsense.qcow2 20G
sudo ls -lh /var/lib/libvirt/images/opnsense.qcow2
```

A qcow2 file is *sparse*: it starts tiny and only grows as the VM writes data,
up to the 20 GB limit. On the author's server, the installed and running VM
uses about 4.5 GB on the host.

???+ success "Verified: 3.2"
    - [ ] `opnsense.qcow2` exists and is small right after creation

??? question "Can I choose a different size?"
    Yes. 20 GB is plenty for a firewall. Change `20G` if you plan to add more
    services inside OPNsense later.

## Section 3.3: Define the Virtual Machine

On the **Ubuntu host**:

```bash
sudo virt-install \
  --name opnsense \
  --memory 4096 \
  --vcpus 2 \
  --machine pc \
  --os-variant freebsd14.0 \
  --disk path=/var/lib/libvirt/images/opnsense.qcow2,format=qcow2,bus=virtio \
  --cdrom /var/lib/libvirt/images/OPNsense-26.7-dvd-amd64.iso \
  --network none \
  --graphics vnc,listen=127.0.0.1 \
  --noautoconsole
```

Change the ISO file name to match yours. What the options mean:

- `--memory 4096 --vcpus 2`: 4 GB RAM and 2 virtual CPUs.
- `--disk ...bus=virtio`: a fast virtual disk. OPNsense (FreeBSD) supports it.
- `--cdrom`: attaches the installer as a virtual DVD for the first boot.
- `--network none`: no network cards yet. Chapter 4 attaches the two bridges.
- `--graphics vnc,listen=127.0.0.1`: the installer screen is reachable only
  from the host itself. Nothing is exposed to your network.
- `--os-variant freebsd14.0`: tuning hints. If your `virt-install` rejects it,
  run `virt-install --osinfo list | grep -i freebsd` and use the newest one.

The VM starts running right after this command.

Check what you created:

```bash
virsh list --all
virsh dominfo opnsense
virsh domblklist opnsense
```

Expected (excerpt, your UUID differs):

```
 Id   Name       State
--------------------------
 1    opnsense   running

CPU(s):         2
Max memory:     4194304 KiB
Persistent:     yes
```

`domblklist` should list the qcow2 disk as `vda` and the ISO on the CD-ROM
device (`hda` on the author's build).

???+ success "Verified: 3.3"
    - [ ] State is `running`, CPU(s) is 2, Max memory is 4194304 KiB
    - [ ] `domblklist` shows the qcow2 file and the ISO

??? question "virt-install: command not found"
    `sudo apt install virtinst` (Chapter 2 installs virt-manager, which usually
    pulls it in).

??? question "I get a 'permission denied' on the ISO"
    The ISO must be somewhere libvirt can read. Keep it in
    `/var/lib/libvirt/images/` as shown above.

## Section 3.4: Run the Installer

The installer is graphical, so you view it through VNC. The VM listens on the
host's loopback address only, so you reach it with an SSH tunnel from your
other computer.

On your **other computer** (Windows PowerShell shown, same on macOS or Linux):

```powershell
ssh -L 5900:127.0.0.1:5900 <username>@<ubuntu-ip>
```

Leave that window open, then connect any VNC viewer to `localhost:5900`.
(Alternatively, run `virt-manager` on a computer with a screen.)

In the installer:

1. At the login prompt type `installer`, password `opnsense`.
   (These are the public, documented installer credentials, not your final
   password.)
2. Accept the default keymap, choose **Guided Installation**, and select the
   disk (the 20 GB `vtbd0` one). Confirm that the disk will be erased: it is
   the empty virtual disk, not your real drive.
3. Set a **root password** when asked. Use a long, unique one and store it in
   a password manager. Do not write it in this repository.
4. When the installer finishes, choose **Complete Install** and then
   **Reboot**.

Do not close the VM window yet. The next section removes the installer disc so
the VM boots from its own disk.

???+ success "Verified: 3.4"
    - [ ] Installer reached the end without disk errors
    - [ ] The VM rebooted and shows the OPNsense console menu or login prompt

??? question "The installer boots but I only see a black screen"
    Wait about 30 seconds. If it stays black, reconnect the VNC viewer.

??? question "It says no network interfaces were found"
    Expected. We attach networking in Chapter 4.

## Section 3.5: Remove the Installer and Enable Autostart

Eject the virtual DVD so the VM does not boot the installer again:

```bash
virsh change-media opnsense hda --eject --live --config
```

Make the VM start whenever the host boots, for example after a power cut:

```bash
virsh autostart opnsense
virsh dominfo opnsense | grep -i autostart
```

The second command must print `Autostart:  enable`.

Optionally take a snapshot of the clean install so you can return to it:

```bash
virsh shutdown opnsense      # wait until `virsh list --all` shows "shut off"
sudo cp /var/lib/libvirt/images/opnsense.qcow2 /var/lib/libvirt/images/opnsense-clean.qcow2
virsh start opnsense
```

(A plain file copy is the simplest backup for a qcow2 disk. It takes 4–5 GB.)

???+ success "Verified: 3.5"
    - [ ] `virsh domblklist opnsense` shows the CD-ROM device empty (`-`)
    - [ ] `virsh dominfo opnsense | grep -i autostart` shows `enable`
    - [ ] After `virsh reboot opnsense` the console shows the login prompt, not the installer

??? question "How can I tell autostart really works?"
    Reboot the host (`sudo reboot`), wait a minute, SSH back in and run
    `virsh list --all`. `opnsense` should be `running` without you starting it.

## Rollback

Start over from 3.2:

```bash
virsh destroy opnsense          # stop it (forced); ignore an error if already off
virsh undefine opnsense         # remove the definition
sudo rm /var/lib/libvirt/images/opnsense.qcow2
```

If you made the clean-install copy in 3.5, restore it instead:

```bash
virsh destroy opnsense
sudo cp /var/lib/libvirt/images/opnsense-clean.qcow2 /var/lib/libvirt/images/opnsense.qcow2
virsh start opnsense
```

## FAQ

??? question "Can I give OPNsense more CPU or RAM?"
    Yes, later, with the VM shut down: `virsh setmaxmem opnsense 8G --config`,
    `virsh setmem opnsense 8G --config`, `virsh setvcpus opnsense 4 --config --maximum`.
    2 vCPUs and 4 GB is enough for a home network.

??? question "Why not run OPNsense directly on the mini PC?"
    The author wanted Ubuntu on the same machine for other services, and
    snapshots and backups are easier with a VM. See Chapter 1 for the design.

??? question "Why is the ISO 2 GB, not 600 MB?"
    The `dvd` image bundles everything. It is the right one for a VM install.

??? question "Do I keep the ISO afterwards?"
    You can delete it once the VM boots from its own disk, or keep it for a
    reinstall. It is stored on the host in `/var/lib/libvirt/images/`.

---

**Next:** [Chapter 4: Build the Virtual WAN/LAN Network](04-build-the-virtual-wan-lan-network.md)
