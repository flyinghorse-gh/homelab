# Current Homelab State

Last updated: 2026-09-27

This document describes the currently known state of the homelab.

## Primary Server

- Ubuntu Linux is installed and booting successfully on the mini-PC.
- SSH has been enabled.
- Exact hostname, IP addressing, final disk layout, CPU, RAM, and storage
  inventory still need to be recorded.

## Disk / Operating System

Ubuntu was installed after transitioning the machine away from its previous
Windows setup.

Disk partitioning was adjusted manually during installation.

The current final partition layout should be documented from fresh output of:

    lsblk
    df -h
    sudo fdisk -l

Do not infer the disk layout from old installation notes.

## Network / Firewall

OPNsense is being used as part of the homelab networking/firewall setup.

Known completed work:

- An OPNsense configuration backup was made before firewall hardening.
- WAN firewall rules were checked and were empty.
- NAT rules were checked and were empty.
- Initial management-hardening changes were completed.
- Connectivity was verified after those changes.

Exact interfaces, VLANs, subnets, DHCP configuration, and firewall policy
still need to be documented.

## Remote Access

SSH is enabled on the Ubuntu server.

Tailscale setup has been discussed but is not yet documented here as completed.

Remote-access paths should not be considered production-ready until they are
explicitly verified and documented.

## Source Control

A private GitHub repository named `homelab` has been created.

The repository has been cloned onto the primary Windows development machine.

This repository is intended to become the durable source of truth for:

- documentation
- configuration templates
- scripts
- infrastructure decisions
- change history

## Secrets

Secrets are intentionally excluded from Git.

Sensitive router/firewall backups should be stored separately in protected
storage.
