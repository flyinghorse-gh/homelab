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

## Workflow

For infrastructure changes:

1. Inspect current state.
2. Make a backup when appropriate.
3. Explain the planned change.
4. Make one logical change.
5. Verify it.
6. Update documentation.
7. Commit the change to Git.

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
