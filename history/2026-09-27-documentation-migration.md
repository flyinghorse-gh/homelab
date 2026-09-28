# 2026-09-27 — Documentation Migration to IDE Workflow

## Objective

Move continuity from ChatGPT web conversations into repository documentation,
using FUTO as the guiding reference and the Part 1 v6 DOCX as the record of
local adaptations and prior work.

## Changes

- Reconciled current state and installation history with recorded KVM/OPNsense,
  WAN/LAN, USB Ethernet, DuckDNS, Tailscale, and hardening milestones.
- Corrected “NAT rules empty” to the supported claim “NAT port forwards empty”.
- Added network/access details, architecture decisions, and a next-chat handoff.
- Preserved unknown dates and unresolved steps rather than treating guide
  instructions as evidence of completion.
- Recorded the user's next starting point: DOCX Chapter 2, "Ubuntu Host and
  Virtualization Foundation", beginning with inspection of existing state.
- Added the requirement to ask before committing and before pushing. No
  automatic push to `main`; edit approval does not authorize either action.
- Updated README navigation and annotated the bootstrap log's historical tasks.

## Evidence and Limits

Reviewed the local DOCX and all project Markdown documentation. Git history
confirms initial documentation/reference commits, and the active workflow
establishes that VS Code/Codex are in use. No live host, firewall, VPN, or DDNS
checks were performed; no infrastructure was changed. The reference DOCX was
retained unchanged. Its FUTO URL is recorded for future consultation.

## Next

The user reviewed the documentation and authorized staging and a local commit
on 2026-09-27. Pushing was not authorized. Diff whitespace checks and all 12
local Markdown links passed validation. Resume via
[the handoff](../docs/04-next-session.md) in a new chat.
