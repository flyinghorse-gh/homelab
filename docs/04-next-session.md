# Next Session Handoff

Last updated: 2026-10-03

## Goal and References

Continue building the homelab with IDE-based Claude/Codex, keeping state and
progress in this repository so new chats can resume without earlier chat
history. The user runs each command or WebGUI step and pastes the results; the
agent cannot reach the server. Work in small steps, explain each check's
purpose, and verify before moving on.

FUTO's [Introduction to a Self Managed Life](https://wiki.futo.org/index.php/Introduction_to_a_Self_Managed_Life:_a_13_hour_%26_28_minute_presentation_by_FUTO_software)
is the guiding reference. Adapt it to the ThinkCentre/Ubuntu/KVM/OPNsense
design and the shared upstream router constraints.

## Where We Are

Network-wide DNS filtering with AdGuard Home on the Ubuntu host is **working
for the one LAN client tested** (wired Windows PC). See
[current state](01-current-state.md#dns-filtering),
[DNS filtering record](05-dns-filtering.md) and ADR-011 to ADR-013. Guide
Chapter 8 documents the verified core.

## Read First

1. `AGENTS.md`, `CLAUDE.md`
2. `README.md`
3. `docs/01-current-state.md` (especially "DNS Filtering")
4. `docs/decisions.md` (ADR-011 to ADR-013)
5. `docs/05-dns-filtering.md` (Implementation Record)
6. `docs/03-network-and-access.md`

## Open Items From DNS Filtering

Smallest first. Each needs inspection, then a small verified change.

1. **Confirm settings the user never reported:** the DHCP ranges tab (the test
   PC was leased `192.168.5.90`, below the recorded `.100`–`.200` pool) and the
   AdGuard log rotation / statistics retention values.
2. **Tailscale port restriction (unresolved):** over Tailscale, ports `53` and
   `3000` to `192.168.5.2` timed out while `22` worked, though `docs/03`
   records an allow-all TAILSCALE rule and an all-ports Grant. Inspect the live
   Tailscale Access controls and the OPNsense TAILSCALE rules before changing
   anything. Decide whether the dashboard should keep using an SSH tunnel or
   get a deliberate, narrow allow rule for port `3000` with a rollback.
3. **Remote devices:** Tailscale clients still use their existing DNS; filtering
   them is a separate decision.
4. **Optional per-client rules** in the AdGuard dashboard once the user decides
   which devices need different treatment.
5. **DNS over TLS (planned):** Unbound would forward to a chosen no-logging
   resolver over TLS, replacing recursive mode. The user asked for as much
   privacy as possible. Compare resolvers' policies first, then change one
   thing, verify, and keep a rollback. Explain that this moves trust from the
   ISP to the resolver and does not hide destination IPs.
6. **Enforcement against bypass (separate decision):** a lookup straight to
   `1.1.1.1` is not filtered. A port-53 firewall rule helps but does not stop
   browser DoH or VPNs. Supply a specific rollback before any firewall change.
7. **Anonymity layer (later chapter):** the user's PC has NordVPN installed.
   A VPN for outbound traffic is separate from the inbound Tailscale tunnel and
   would need its own design, because it is a bigger change to the shared-router
   setup.
8. Test a second LAN client, and later deploy the switch/AP and normal clients
   behind OPNsense. Then re-test DNS from them.

## Other Open Tasks

- Verify sleep settings and BIOS power-loss recovery (VM autostart held across
  one reboot).
- Remove the leftover libvirt `virbr0` network (its `dnsmasq` still listens on
  `192.168.122.1`) after confirming it is unused, and confirm removal of the
  temporary NIC and OPT1 assignment.
- Record current versions, non-secret access identifiers and full host
  inventory. Document the protected backup location and restore procedure and
  run a restore test.
- The Ubuntu Wi-Fi PSK is stored plaintext in a root-only netplan file.
- Confirm whether the repository has been cloned onto Ubuntu.
- Remove `~/agh-download` and any leftover `AdGuardHome.yaml` backup copy on the
  host (it contains a password hash).

## Lessons To Reuse

- Check which interface a Windows test used (`InterfaceAlias`, `Find-NetRoute`).
  With Tailscale connected, `192.168.5.x` traffic goes through the tunnel.
- Multi-line pastes into an SSH session can feed lines to a `sudo` password
  prompt. Run `sudo` commands one at a time.
- In the Dnsmasq DHCP option form, `Option` is IPv4 and `Option6` is IPv6.
- A DHCP option does nothing until **Apply**.
- Do not ask users to paste MAC addresses or password hashes.

## Session Closeout and Git

Update current state, component docs, decisions where needed, dated history,
the guide chapter and this handoff after meaningful work. Record actual checks
and unresolved items; distinguish historical evidence from live observations.

The documentation updates for DNS filtering are **uncommitted**. Inspect `git
status` when resuming. Ask for explicit approval before committing and again
before pushing, including to `main`. Present the diff, the privacy-check result
(`python scripts/docs/check-guide.py`), the site build result, and the push
destination before asking.

## Suggested New-Chat Prompt

> Read AGENTS.md, CLAUDE.md, README.md, docs/01-current-state.md,
> docs/decisions.md, docs/05-dns-filtering.md and docs/04-next-session.md.
> DNS filtering with AdGuard Home is working; continue with the open items in
> the handoff, starting with the DHCP pool and Tailscale port-restriction
> checks. Give me one small step at a time to run and verify. Keep the docs
> current and ask me before committing or pushing.
