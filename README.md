# Homelab

This repository is the source of truth for my personal homelab.

## Goals

- Build a secure, reliable self-hosted environment.
- Keep infrastructure changes documented and reproducible.
- Make the project usable from Windows, Linux, VS Code, Codex, and OpenCode.
- Preserve enough context that a new person or AI agent can understand the environment.

## Start Here

Before making changes, read:

1. `AGENTS.md`
2. `docs/01-current-state.md`
3. `docs/decisions.md`
4. `docs/04-next-session.md`

## Reference and Current Checkpoint

Use FUTO's [Introduction to a Self Managed Life](https://wiki.futo.org/index.php/Introduction_to_a_Self_Managed_Life:_a_13_hour_%26_28_minute_presentation_by_FUTO_software)
as the guiding reference, adapted to a Lenovo ThinkCentre running Ubuntu with
virtualized OPNsense and a shared upstream router that must remain operational.

The Part 1 v6 DOCX records working virtualization, WAN/LAN bridges, a physical
LAN test, DuckDNS, and Tailscale remote access tested from an external hotspot.
These are historical results, not fresh live verification. Markdown is the
ongoing record as work moves from ChatGPT web into IDE-based Codex.

The next milestone is **network-wide DNS filtering / ad blocking**, adapting
FUTO to OPNsense. Start by comparing Unbound blocklists with AdGuard Home and
inspecting the private LAN's actual DNS path. No filtering engine is selected yet.

## Documentation

- `docs/01-current-state.md` — what exists right now
- `docs/02-installation-history.md` — how we got here
- `docs/decisions.md` — important architectural decisions
- [Network and access](docs/03-network-and-access.md) — topology, recorded
  configuration, verification, and recovery gaps
- [Next-session handoff](docs/04-next-session.md) — DNS filtering agenda
  and a prompt for a new chat
- [Part 1 v6 reference](docs/reference/ThinkCentre_OPNsense_Self_Managed_Setup_Part_1_v6.docx)
  — historical setup record and local adaptations of FUTO
- `history/` — dated work logs

## Important

Secrets, passwords, private keys, authentication tokens, recovery codes,
and sensitive configuration backups must never be committed to this repository.

Codex must ask for explicit approval before committing and before pushing.
Permission to edit does not authorize either action. Never push to `main`
without explicit approval for that push.
