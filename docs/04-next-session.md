# Next Session Handoff

Last updated: 2026-10-14

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

1. **Explain the `192.168.5.90` lease (in progress, 2026-10-14).** Dnsmasq
   Hosts and Leases tabs were empty (user-reported), so it is not a
   reservation. The PC's Ethernet was unplugged. When back at the wired PC:
   plug in, run `ipconfig /renew "Ethernet 2"`, check the new IP, DHCP server
   and lease times, then confirm the lease in the OPNsense Leases tab. Most
   likely `.90` came from an older pool setting.
2. **Remote filtering (ADR-014) is now tested on two Windows devices** (PC and
   laptop; the laptop was on the home network, not truly remote). Still to do:
   a phone on mobile data, the failure case (host down), and identify the
   unknown device at `192.168.5.165` seen on the WAN side.
3. **Exit node (ADR-015, 2026-10-14):** OPNsense offers an exit node; phone use
   is user-reported. Remaining: test from mobile data and confirm the public IP
   is the home IP (do not paste it). Destination NAT has no user rules
   (2026-10-14). Optionally describe the manual outbound NAT rule for
   `100.64.0.0/10`. The second account keeps the exit-node grant (decided
   2026-10-14). Save a copy of the policy outside Git. Rollback is in ADR-015.
3. **Policy hygiene:** keep a saved copy of the tailnet policy outside Git. The
   repo must never contain account addresses or the OPNsense Tailscale address.
4. **Optional per-client rules** in the AdGuard dashboard once the user decides
   which devices need different treatment.
5. **DNS over TLS: done 2026-10-14 (ADR-016, guide chapter 9).** Remaining:
   repeat the `tcpdump -ni br-wan 'port 53'` capture while browsing to prove no
   plain DNS leaves, check the AdGuard Query Log still shows `NOERROR`, and
   optionally add a threat-intelligence list in AdGuard.
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

Commit `463999b` (DNS filtering docs) was committed and pushed to `origin/main`
with the user's approval on 2026-10-03. The later remote-filtering and
Tailscale-policy updates are **uncommitted**. Inspect `git status` when
resuming. Ask for explicit approval before committing and again before pushing,
including to `main`. Present the diff, the privacy-check result
(`python scripts/docs/check-guide.py`), the site build result, and the push
destination before asking.

## Suggested New-Chat Prompt

> Read AGENTS.md, CLAUDE.md, README.md, docs/01-current-state.md,
> docs/decisions.md, docs/05-dns-filtering.md and docs/04-next-session.md.
> DNS filtering with AdGuard Home is working; continue with the open items in
> the handoff, starting with the DHCP pool and Tailscale port-restriction
> checks. Give me one small step at a time to run and verify. Keep the docs
> current and ask me before committing or pushing.
