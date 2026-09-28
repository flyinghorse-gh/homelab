# Next Session Handoff

Last updated: 2026-09-27

## Goal and References

Continue building the homelab with IDE-based Codex, keeping state and progress
in this repository so new chats can resume without earlier chat history.

FUTO's [Introduction to a Self Managed Life](https://wiki.futo.org/index.php/Introduction_to_a_Self_Managed_Life:_a_13_hour_%26_28_minute_presentation_by_FUTO_software)
is the guiding reference (link supplied by the local DOCX; the website was not
reviewed during this documentation migration). Adapt its steps to the actual
ThinkCentre/Ubuntu/KVM/OPNsense design and shared upstream router constraints.

The next milestone is **network-wide DNS filtering / ad blocking**, adapting
FUTO's pfBlockerNG approach to OPNsense. This follows the user's supplied
ChatGPT web agenda and section 8.3 of the
[Part 1 v6 DOCX](reference/ThinkCentre_OPNsense_Self_Managed_Setup_Part_1_v6.docx).
It supersedes the earlier plan to revisit DOCX Chapter 2. Do not confuse a
new phase of this project with the DOCX's existing chapter numbering.

First compare Unbound blocklists and AdGuard Home. Unbound is the provisional
recommendation because it is already reported enabled; the user has not yet
selected an engine. No filtering configuration or installation has been done.

## Read First

1. `AGENTS.md`
2. `README.md`
3. `docs/01-current-state.md`
4. `docs/02-installation-history.md`
5. `docs/decisions.md`
6. `docs/03-network-and-access.md`
7. This handoff and relevant history entries.
8. DOCX sections 8.2–8.3 and relevant networking sections; consult FUTO for guide
   context when needed rather than assuming its contents.

## DNS Filtering Agenda

1. Compare Unbound blocklists and AdGuard Home with the user before installing
   anything. If AdGuard Home is selected, decide placement, resolver chain,
   listening addresses/ports, and service recovery before changing DNS.
2. Inspect current OPNsense version, Unbound settings, DHCP DNS options, and
   DNS servers actually used by a private LAN client. Check IPv6 DNS settings
   if enabled. Establish a working LAN test client: full switch/AP deployment
   and normal client Internet routing are not yet confirmed.
3. Verify management access and baseline DNS, then create an encrypted backup
   outside Git and record how to revert the proposed DNS/DHCP changes.
4. Configure the chosen resolver for the private LAN with a small, reviewed
   selection of lists. Validate one client before broader rollout. With
   Unbound on OPNsense, the intended DNS endpoint is `192.168.5.1`; if another
   architecture is chosen, document its actual endpoint and query path.
5. Test an intentionally blocked domain, normal resolution, query latency,
   browsing, updates, and important applications. Recheck SSH, Tailscale, and
   DuckDNS. Test allowlisting a false positive and reverting the change.
6. Only after filtering works, separately decide whether to restrict external
   DNS. Account for IPv4/IPv6, VPNs, and encrypted DNS; a port-53 rule alone
   must not be described as preventing all bypass. Supply a specific rollback
   before any firewall enforcement change.
7. Keep remote Tailscale DNS unchanged initially. Remote-device filtering is
   optional and requires a separate decision. IP reputation, GeoIP, and IDS
   are also separate work, not requirements for this first filtering pass.
8. Record chosen architecture, list sources/update behavior, intentional
   exceptions, rules, dated test results, and rollback instructions.

Keep the shared upstream router/network untouched. Do not assume existing
SSH credentials, current reachability, or a tested recovery path. Explain
impact before potentially disruptive changes and verify each logical step.

## Comparison References

Official product documentation checked during agenda reconciliation:

- [OPNsense Unbound](https://docs.opnsense.org/manual/unbound.html): integrated
  blocklists, allowlists, source-network policies, and reporting integration.
  Check the installed release before relying on a particular UI feature.
- [AdGuard Home](https://github.com/AdguardTeam/AdGuardHome): a separate DNS
  filtering service. DNS-level blocking cannot distinguish ads from wanted
  content sharing the same domain; do not promise removal of every ad.

## Other Open Tasks

- Verify host inventory, SSH/service health, sleep settings, VM autostart, and
  BIOS power-loss recovery. These remain open checks, not a mandate to rebuild
  the foundation before comparing DNS options.

- Confirm removal of temporary libvirt/default NIC and OPT1 assignment.
- Confirm physical LAN switch/AP deployment, normal client routing, and
  persistent USB bridge configuration.
- Record current versions, non-secret access identifiers, and full host inventory.
- Document protected backup location and recovery procedure without secrets.
- Confirm whether the repository has been cloned onto Ubuntu.

## Session Closeout and Git

Update current state, component docs, decisions where needed, dated history,
and this handoff after meaningful work. Record actual checks and unresolved
items; distinguish historical evidence from live observations.

Documentation migration commit `ebb717c` was created with approval on
2026-09-27. The user reported pushing it themselves and subsequently authorized
committing and pushing the DNS-agenda correction to `origin/main`. Inspect
`git status` and history when resuming to confirm the synchronization state.
Codex must ask before committing and before pushing, including to `main`.
Present the concrete diff/check results and push destination before asking;
approval to edit files or commit does not imply approval to push.

## Suggested New-Chat Prompt

> Read AGENTS.md, README.md, docs/01-current-state.md,
> docs/02-installation-history.md, docs/decisions.md,
> docs/03-network-and-access.md, and docs/04-next-session.md. Use FUTO as our
> guiding reference and continue with network-wide DNS filtering / ad blocking,
> the next milestone in DOCX section 8.3. Start by comparing Unbound blocklists
> with AdGuard Home and inspecting the private LAN's current DNS path. Do not
> install anything before we choose the architecture.
> Keep docs/progress current and ask me before committing or pushing.
