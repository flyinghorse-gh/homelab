# 2026-09-27 — DNS Filtering Agenda Clarification

The user supplied the next agenda from their prior ChatGPT web conversation:
network-wide DNS filtering/ad blocking, adapting FUTO to OPNsense. This matches
Part 1 v6 section 8.3 and supersedes the initial DOCX Chapter 2 handoff.

Updated README, current state, installation history, decisions, and the next
session prompt. The earlier migration log preserves the original plan as
history. Unbound is a provisional recommendation; Unbound versus AdGuard Home
remains an open decision. Added LAN/DNS inspection, conservative rollout,
verification, allowlisting, and rollback to the agenda. DNS enforcement and
remote Tailscale DNS are separate later decisions.

Consulted official OPNsense Unbound and AdGuard Home documentation; links are
in the handoff. No filtering was installed or enabled, no live infrastructure
checks were performed. The user subsequently authorized committing and pushing
this correction to `origin/main`; inspect Git history for the resulting commit.
The user reported pushing the earlier migration commit `ebb717c` themselves.
