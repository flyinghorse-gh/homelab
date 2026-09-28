# Homelab Agent Instructions

This repository documents and manages a personal homelab.

## Before Making Changes

Always read:

1. `docs/01-current-state.md`
2. `docs/decisions.md`
3. Any documentation related to the component being changed.

Do not assume undocumented infrastructure exists.

## Safety Rules

- Never expose a management interface directly to the public Internet.
- Never commit passwords, API keys, private keys, authentication tokens,
  recovery codes, or other secrets.
- Never perform destructive disk, firewall, routing, SSH, or network changes
  without explaining the impact first.
- For potentially disruptive changes, provide a rollback procedure.
- Prefer one small change at a time.
- Verify each infrastructure change before continuing.
- Preserve working remote access whenever modifying SSH, firewall, routing,
  VPN, or network configuration.
- Do not assume a change succeeded until it has been verified.
- Preserve the shared upstream router and household connectivity. No
  bridge/passthrough mode or public port forwards are part of the current design.

## Workflow

For infrastructure changes:

1. Inspect current state.
2. Make a backup when appropriate.
3. Explain the planned change.
4. Make one logical change.
5. Verify it.
6. Update documentation.
7. Summarize the changes and verification, then request explicit approval
   before committing and before pushing.

## Git Approval

- Codex must ask for explicit user approval before creating a commit or pushing.
- Editing permission does not authorize a commit or push. Commit approval does
  not authorize a push; the user may explicitly approve both together.
- Approval applies only to the stated action and scope. Before push approval,
  identify the destination branch and commits to be pushed.
- Never push to `main` on your own. Leave changes uncommitted until approved.

## Reference and Session Continuity

- Use FUTO's "Introduction to a Self Managed Life" as the guiding reference.
  Adapt it to the documented ThinkCentre/Ubuntu/KVM/OPNsense architecture and
  shared-router constraints; do not blindly copy dedicated-router instructions.
- The Part 1 v6 DOCX records prior work and local adaptations. The Markdown
  documents are the ongoing source of truth, not earlier chat history.
- Read `docs/04-next-session.md` when resuming work and keep it current.
- Distinguish reference-reported results from fresh live verification. Do not
  invent milestone dates or mark instructions as completed work.

## Documentation

After a meaningful infrastructure change:

- Update `docs/01-current-state.md`.
- Update the relevant component documentation.
- Record significant architecture decisions in `docs/decisions.md`.
- Add verification commands/results where useful.
- Add a dated history entry for major work.

## Secrets

Sensitive values belong outside Git.

Examples:

- passwords
- `.env` files containing secrets
- SSH private keys
- Tailscale auth keys
- API tokens
- Cloudflare tokens
- recovery codes
- unencrypted firewall/router backups
