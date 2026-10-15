# Self-Managed Homelab Guide

Build your own home server firewall and DNS filtering in **9 chapters**. This guide
takes you from hardware selection through a fully operational homelab with secure
remote access and ad blocking.

The setup uses:
- **One mini PC** (like a Lenovo ThinkCentre) running Ubuntu Linux
- **OPNsense VM** running on KVM for routing and firewalling
- **Your existing home router** stays untouched; double NAT is fine
- **Zero public port forwards** needed; Tailscale handles remote access

It adapts FUTO's [Introduction to a Self Managed Life](https://wiki.futo.org/index.php/Introduction_to_a_Self_Managed_Life:_a_13_hour_%26_28_minute_presentation_by_FUTO_software),
a 13-hour reference, to a practical hands-on setup.

## How This Guide Works

- **Chapter-by-chapter** progression: each chapter covers one milestone
- **Beginner-friendly**: explains terms, shows examples, no prior Linux required
- **Verification at every step**: after each change, you'll confirm it worked
- **Rollback procedures**: know how to undo changes if something goes wrong
- **FAQ and troubleshooting**: real questions, answered plainly

## Status and Safety

!!! warning "Status Key"
    - **Verified**: tested and ready to follow (Ch. 1)
    - **Draft**: written but not yet tested (upcoming)
    - **Outline**: planned but not written yet

Chapters are built from actual verified work, not generic instructions. If a chapter
says "not yet tested", it's marked clearly—don't follow it as gospel.

**Privacy notice:** All examples use placeholders (`<LAN_SUBNET>`, `<DUCKDNS_HOSTNAME>`).
Real IPs, MAC addresses, and hostnames are never published on this site.

## Quick Start

1. **Read:** [What you need](what-you-need.md) — hardware and time checklist
2. **Learn:** [Glossary](glossary.md) — terms as you go
3. **Follow:** Start with **Chapter 1: Architecture and Hardware Baseline**
   - Takes ~30 minutes (reading only, no configuration)
   - Verify your hardware can run KVM
   - Understand the design

Then proceed chapter by chapter. Each takes 1–2 hours of hands-on work.
