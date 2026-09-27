# Installation and Setup History

## 2026-09-22 — Ubuntu Installation

The mini-PC previously contained Windows.

Ubuntu installation was started without a traditional USB installer.

Grub2Win was used during the boot/install process and an Ubuntu installer ISO
was booted from local storage.

Ubuntu was successfully installed and the machine booted into Ubuntu.

Disk partitions were manually adjusted during this process.

The exact current disk layout must be documented using fresh Linux disk
inspection commands rather than relying on installation-time screenshots.

SSH was enabled after Ubuntu installation.

## 2026-09-23 onward — OPNsense Hardening

Work began on securing OPNsense management access.

Before making firewall changes:

- A configuration backup was created.

The existing configuration was inspected:

- WAN firewall rules were empty.
- NAT rules were empty.

Initial hardening changes were applied incrementally.

Connectivity checks performed afterward continued to work.

## 2026-09-27 — Project Repository

A private GitHub repository named `homelab` was created.

The repository was cloned to the Windows development machine.

The repository is now being prepared as the durable project record so that
VS Code, Codex, OpenCode, the Ubuntu server, and future machines can work from
the same documented state.
