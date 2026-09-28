# Next Session Handoff

Last updated: 2026-09-27

## Goal and References

Continue building the homelab with IDE-based Codex, keeping state and progress
in this repository so new chats can resume without earlier chat history.

FUTO's [Introduction to a Self Managed Life](https://wiki.futo.org/index.php/Introduction_to_a_Self_Managed_Life:_a_13_hour_%26_28_minute_presentation_by_FUTO_software)
is the guiding reference (link supplied by the local DOCX; the website was not
reviewed during this documentation migration). Adapt its steps to the actual
ThinkCentre/Ubuntu/KVM/OPNsense design and shared upstream router constraints.

The user explicitly chose **Chapter 2 of the
[Part 1 v6 DOCX](reference/ThinkCentre_OPNsense_Self_Managed_Setup_Part_1_v6.docx):
"Ubuntu Host and Virtualization Foundation"** for the next chat. This is a
review/resumption point, not evidence that later chapters are unfinished.
The reference already reports milestones through Chapter 7 complete and lists
DNS filtering as a later FUTO milestone; do not skip to it automatically.

## Read First

1. `AGENTS.md`
2. `README.md`
3. `docs/01-current-state.md`
4. `docs/02-installation-history.md`
5. `docs/decisions.md`
6. `docs/03-network-and-access.md`
7. This handoff and relevant history entries.
8. DOCX Chapter 2 before working through its steps; consult FUTO for guide
   context when needed rather than assuming its contents.

## Chapter 2 Starting Checklist

Begin with read-only inspection. Establish the actual connection method and
verify access before running host commands. Do not assume this Windows
workspace already has usable SSH credentials or a working route to Ubuntu.

| DOCX section | Recorded state | Next action |
|---|---|---|
| 2.1 KVM/QEMU/libvirt | Working; prior libvirt account issue resolved | Inspect installed packages/versions, service health, and VM inventory |
| 2.2 Headless access | SSH enabled and previously verified remotely | Check service state and current SSH access |
| 2.3 Sleep and autostart | Masking described; VM autostart reported enabled | Inspect target states and persistent VM autostart configuration |
| 2.4 Power-cut recovery | BIOS setting instructed, not confirmed | Determine current BIOS setting and plan any recovery test safely |

Useful inspection commands include `systemctl is-enabled ssh`,
`systemctl is-enabled sleep.target suspend.target hibernate.target hybrid-sleep.target`,
`virsh --version`, `sudo virsh list --all`, and `sudo virsh dominfo opnsense`.
Masked targets can return a nonzero exit code; interpret their reported states.
Also collect hostname, OS version, CPU/RAM, disks, and network state as needed
to close the documented inventory gaps. No such live checks were run during
the documentation migration.

Do not rerun package installation, service restarts, interface changes, VM
creation, or masking commands simply because they appear in the guide.
Explain impact and supply rollback for potentially disruptive changes. A
reboot/power-loss test can interrupt routing and remote access; plan it with
the user and a verified recovery path before execution.

## Pending Beyond Chapter 2

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

The user approved staging and creating a local documentation-migration commit
on 2026-09-27. Pushing was not authorized. Inspect `git status` and history in
the next chat to establish the current commit and synchronization state.
Codex must ask before committing and before pushing, including to `main`.
Present the concrete diff/check results and push destination before asking;
approval to edit files or commit does not imply approval to push.

## Suggested New-Chat Prompt

> Read AGENTS.md, README.md, docs/01-current-state.md,
> docs/02-installation-history.md, docs/decisions.md,
> docs/03-network-and-access.md, and docs/04-next-session.md. Use FUTO as our
> guiding reference and resume at Chapter 2 of the Part 1 v6 DOCX, "Ubuntu Host
> and Virtualization Foundation". Start by inspecting what already exists.
> Keep docs/progress current and ask me before committing or pushing.
