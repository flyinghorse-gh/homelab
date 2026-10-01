# Claude Code Instructions

@AGENTS.md

The rules in `AGENTS.md` apply to Claude exactly as written. Wherever it says
"Codex", read it as Claude too. Safety rules, the infrastructure workflow, and
git approval are not repeated here.

## Reading Order When Resuming

`AGENTS.md`, `README.md`, `docs/01-current-state.md`,
`docs/02-installation-history.md`, `docs/decisions.md`,
`docs/03-network-and-access.md`, `docs/04-next-session.md`.

## Reference

FUTO's "Introduction to a Self Managed Life" is the guiding reference (link in
`README.md`). Adapt it to the ThinkCentre/Ubuntu/KVM/OPNsense design and the
shared-router constraints. Do not copy dedicated-router steps blindly, and do
not reproduce FUTO text. Summarize and link to it.

## Two Kinds of Documentation

1. **Project record** (`docs/01`–`05`, `docs/decisions.md`, `history/`): the
   internal source of truth. It is honest about what is verified and unverified.
2. **Shareable setup guide** (the chapter-based guide, modeled on
   `docs/reference/ThinkCentre_OPNsense_Self_Managed_Setup_Part_1_v6.docx`):
   written so a friend can follow it chapter by chapter and build their own
   homelab. It is published as a GitHub Pages site.

The project record comes first. The guide is derived from it.

## Shareable Guide Rules

- Each chapter covers one milestone: goal, prerequisites, numbered steps, a
  verification step per change, rollback, and an FAQ/troubleshooting section.
- After every major milestone, update the guide in the same session as the
  project record. Add a new chapter or revise the affected one.
- Only document steps that have actually been done and verified. Mark anything
  else as planned. Do not write pending instructions as completed work.
- Use placeholders, never real values: `<LAN_SUBNET>`, `<DUCKDNS_HOSTNAME>`,
  `<TAILNET_NAME>`. Never include tokens, keys, public IPs, MAC addresses,
  Tailscale addresses, or the DuckDNS hostname. Review every guide page for
  this before asking to commit, because the published site is public.
- Explain terms the first time they appear. The audience is beginners.
- Keep chapter numbering stable. Add new chapters at the end rather than
  renumbering.

## Milestone Closeout Checklist

1. Update `docs/01-current-state.md`, the component doc, `docs/decisions.md`,
   and `docs/04-next-session.md`.
2. Add a dated entry under `history/`.
3. Update or add the matching guide chapter and its FAQ.
4. Check the site builds (once the site exists) and all links resolve.
5. Summarize the changes and the verification, then ask for approval before
   committing and again before pushing.

## Working Environment

- Development machine: Windows 11, VS Code, PowerShell. The server is Ubuntu
  over SSH. Commands in docs must say which machine to run them on
  (Windows, Ubuntu host, OPNsense shell, or WebGUI).
- Claude cannot reach the server unless the user provides access. Never claim a
  live check was done when the evidence comes from docs or user reports.
