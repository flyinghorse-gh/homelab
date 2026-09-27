# Architecture Decisions

This file records decisions that should survive individual chat sessions.

---

## ADR-001 — Git Repository Is the Project Source of Truth

Date: 2026-09-27

Decision:

The private `homelab` Git repository will be the durable source of truth for
project documentation, scripts, configuration templates, and infrastructure
history.

Reason:

Chat sessions and individual development machines should not be required to
reconstruct the environment.

---

## ADR-002 — Secrets Must Not Be Stored in Git

Date: 2026-09-27

Decision:

Passwords, private keys, authentication tokens, recovery codes, and sensitive
configuration backups will not be committed to Git.

---

## ADR-003 — Infrastructure Changes Are Incremental

Date: 2026-09-27

Decision:

Potentially disruptive infrastructure changes will be made one logical layer
at a time.

Each change should include:

1. Current-state inspection
2. Backup when appropriate
3. Change
4. Verification
5. Documentation

Reason:

This reduces the likelihood of losing access to the server or network and
makes troubleshooting easier.

---

## ADR-004 — Management Interfaces Stay Off the Public Internet

Date: 2026-09-27

Decision:

Administrative interfaces such as OPNsense management should not be directly
exposed to the WAN.

Remote management should use a controlled private-access mechanism.
