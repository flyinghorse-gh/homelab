# DNS Filtering Evaluation and Baseline

Last updated: 2026-10-03

Status: **implemented** with AdGuard Home on the Ubuntu host (ADR-011 to
ADR-013). The sections up to "Gate Before Implementation" are the original
2026-09-27 evaluation and are kept as the record of why; the "Implementation
Record — 2026-10-01 to 2026-10-03" section at the end is the current state.
The Unbound-first recommendation below was superseded by the user's choice.

## Reference and Scope

FUTO's [ad-blocking chapter](https://wiki.futo.org/index.php/Introduction_to_a_Self_Managed_Life:_a_13_hour_%26_28_minute_presentation_by_FUTO_software#Adblocking:_Setting_Up_pfBlockerNG_for_Ad-Blocking_in_pfSense)
uses pfBlockerNG on pfSense, measures a baseline, and retests after filtering.
It later forwards to public AdGuard DNS. That public service is distinct from
self-hosted AdGuard Home. The website was reviewed for this evaluation.

Apply the baseline/filter/test approach to OPNsense. Initial scope is clients
behind the private LAN, `192.168.5.0/24`. Devices on upstream household Wi-Fi
will not automatically receive this filtering. Preserve the shared router,
current Tailscale DNS, management access, and household connectivity.

## Options to Choose Between

| Dimension | OPNsense Unbound blocklists | AdGuard Home |
|---|---|---|
| Placement | Existing OPNsense VM; Unbound historically enabled | Additional service; placement still to be chosen |
| Filtering controls | Lists, allowlists, source-network policies | Lists, custom rules, per-client settings |
| Visibility | OPNsense Unbound reporting | Dedicated filtering dashboard and query log |
| Candidate query path | Client → `192.168.5.1:53` Unbound → recursion or inspected upstream | Client → dedicated AdGuard Home LAN IP:53 → Unbound `192.168.5.1:53` |
| Operational cost in this lab | Fewer service dependencies and one configuration surface | Additional updates, backup, startup, storage, and recovery work |
| Best fit | Start with private-LAN domain filtering and minimal added infrastructure | Prefer a dedicated filtering interface and frequent per-device customization |

Sources: [OPNsense Unbound](https://docs.opnsense.org/manual/unbound.html),
[AdGuard Home](https://github.com/AdguardTeam/AdGuardHome), and
[AdGuard Home client settings](https://adguard-dns.io/kb/adguard-home/clients/).
Features in current online documentation must be checked against the installed
OPNsense version. Unbound also has reporting and client/source policies; these
are not exclusive to AdGuard Home. Its documented scheduled list refresh uses
an explicit cron task, which would need verification during implementation.

Recommendation, not a decision: start with Unbound, subject to live inspection.
The candidate AdGuard Home design would use a separate LAN service address and
retain OPNsense DHCP. A small Linux VM is one possible placement; none is
documented for this purpose. Inspect host capacity before selecting it. Hosting both
services on the same ThinkCentre does not provide hardware redundancy.

If AdGuard Home is chosen, settle placement, IP reservation, listening ports,
upstream chain, local-name resolution, and boot/recovery behavior first. Avoid
a forwarding loop back from Unbound to AdGuard Home. Direct client queries to
AdGuard Home preserve client visibility better than proxying all clients through
another resolver. Co-location on one OS would require explicit port/bind planning.

Both options block domains, so ads sharing a domain with wanted content remain
a limitation. Neither supplies pfBlockerNG's entire IP-blocking feature set.
Keep IP reputation and DNS enforcement outside this first change. Later bypass
analysis must include IPv6, browser/OS encrypted DNS, and VPNs.

## Fresh Observations — 2026-09-27

Read-only checks ran on the Windows development PC. CIM inspection and DNS
queries required execution outside the sandbox. Sandboxed query timeouts are
not evidence of an infrastructure outage; the outside-sandbox repeats succeeded.

| Check | Observed result | Limit |
|---|---|---|
| Wi-Fi 2 | Up; IPv4 `10.0.0.136`, gateway `10.0.0.1`, DNS `75.75.75.75` and `75.75.76.76` | Upstream household network, not private LAN |
| Ethernet 2 | Disconnected; self-assigned `169.254.12.49`; configured DNS/gateway `192.168.5.1` | These retained settings do not prove a current DHCP lease |
| Route to `192.168.5.1` | Tailscale, destination `192.168.5.0/24` | Tests of this address are over VPN, not direct Ethernet |
| Effective Windows DNS policy | Tailscale-specific name and reverse zones use Tailscale DNS; no catch-all entry shown | Does not audit browser/app DNS behavior |
| Default `nslookup example.com` | `75.75.75.75` answered A and AAAA records | Establishes this tool's resolver, not every application's path |
| Explicit `nslookup example.com 192.168.5.1` | Answered A and AAAA records; server name `OPNsense.home.arpa` | Does not prove which daemon or upstream served the query |
| Explicit AAAA query to `192.168.5.1` | Successful | IPv6 records over IPv4 do not prove IPv6 transport or LAN IPv6 DNS |
| WebGUI | User reports it opens | No authenticated settings inspected by the agent |

Commands used (all read-only):

```powershell
Get-NetIPConfiguration
Get-DnsClientServerAddress
Get-NetAdapter
Get-NetIPInterface
Find-NetRoute -RemoteIPAddress 192.168.5.1
Get-DnsClientNrptPolicy -Effective
nslookup -timeout=2 -retry=1 example.com
nslookup -timeout=2 -retry=1 example.com 192.168.5.1
nslookup -timeout=2 -retry=1 -type=AAAA example.com 192.168.5.1
```

## Remaining Read-Only Inspection

### User-reported WebGUI observations — 2026-09-27

The user read these from the running WebGUI; the agent has not independently
retrieved the settings:

| Field | Reported value |
|---|---|
| OPNsense | `26.7.4_1-amd64` |
| FreeBSD | `15.1-RELEASE-p3` |
| OpenSSL | `3.5.8` |
| Unbound enabled | Yes |
| Listen port | `53` |
| Network interfaces | `All` |
| Enable DNSSEC | Unchecked |

Unbound is the DNS resolver: it answers name-to-address queries. Port 53 is
the standard port for ordinary DNS. Interfaces select where it listens;
firewall rules and resolver access lists separately determine who can query
it. `All` alone does not establish public reachability. DNSSEC validates
signatures for signed DNS data; it does not encrypt queries or block ads.
The unchecked setting means local Unbound validation is not enabled through
this option; upstream validation behavior remains unknown.

Next determine whether Unbound resolves recursively (contacts the DNS hierarchy
itself) or forwards requests to another resolver, called its upstream. This is
separate from selecting the filtering engine. Also inspect current blocklists
before assuming filtering is absent. Nothing needs changing for these checks.

### Pending checks

View settings without Save, Apply, restart, renewal, or configuration changes.
Record selected non-secret fields, not raw router backups or full query logs.

1. Dashboard: Unbound running status (the enable checkbox records configuration,
   not by itself the running process state). Version and General settings
   have been supplied above.
2. Services → Unbound DNS: access lists, blocklist state, Query Forwarding
   (including Use System Nameservers), and DNS-over-TLS entries. Record any
   catch-all destination.
3. System → Settings → General: configured DNS servers, WAN DNS override,
   and whether the firewall uses its local resolver. These settings alone do
   not establish Unbound's upstream; compare with step 2.
4. Identify the active DHCP implementation before choosing its menu. Inspect
   LAN subnet options, DNS servers (option 6), gateway, pool, and relevant
   reservation overrides. Do not assume Kea, Dnsmasq, or ISC from the old guide.
5. Inspect LAN IPv6 assignment, router advertisements/RDNSS, and DHCPv6 DNS
   if enabled. Do not infer IPv6 is disabled from the IPv4 baseline.
6. Confirm a physically connected private-LAN test client while preserving
   the WAN cable and existing recovery access. Inspect its address, DHCP
   server, route, and DNS with `ipconfig /all` and the commands above. A valid
   `192.168.5.x/24` lease and direct LAN route are not yet established here.
7. Compare a normal lookup with an explicit resolver query on that client.
   Inspect browser Secure DNS and VPN settings without changing them. Correlate
   with existing resolver reporting if available; enabling logging is a change.

## Gate Before Implementation

After inspection, obtain the user's architecture choice. Then prepare an
encrypted backup outside Git and a specific rollback based on the observed
settings. Validate one LAN client before broader rollout. For a future Unbound
change, rollback should restore the prior blocklist settings; any accompanying
DHCP change needs its own recorded previous values and lease-transition plan.
For AdGuard Home, plan restoration of prior client/DHCP DNS if its service fails.
Do not introduce a public secondary resolver as a substitute for local recovery.

As of the 2026-09-27 evaluation, no implementation, filter-effectiveness test,
rollback test, DHCP validation, or external-hotspot management retest had been
completed. The record below supersedes that.

## Implementation Record — 2026-10-01 to 2026-10-03

All results below are from output the user pasted (Ubuntu host, OPNsense
WebGUI, Windows PowerShell, AdGuard dashboard). The agent ran none of these
commands. Where a value is inferred, it says so.

### Pre-change inspection (OPNsense WebGUI, read-only)

| Item | Observed |
|---|---|
| Unbound General | Enabled, port `53`, interfaces `All`, DNSSEC unchecked, other boxes unchecked |
| Query Forwarding | Only `home.arpa` → `127.0.0.1:53053` ("Forward default domain to Dnsmasq DHCP"); Use System Nameservers unchecked |
| Unbound Blocklist | Disabled, nothing selected |
| DNS over TLS | Empty |
| Dnsmasq General | Enabled on LAN; DNS listen port `53053`; default domain `home.arpa`; DHCP register firewall rules and Router advertisements checked |
| DHCP ranges | One LAN range (user reported `192.168.5.100`–`.200`) |
| DHCP options | Empty (so clients got `192.168.5.1` for DNS) |

Reading: Unbound resolves recursively and is the resolver for clients; Dnsmasq
supplies DHCP and local `home.arpa` names.

### Host checks (Ubuntu, 2026-10-01)

- `br-lan` `UP` with `192.168.5.2/24`.
- Port `53` listeners before install: libvirt `dnsmasq` on `192.168.122.1` and
  `systemd-resolved` on `127.0.0.53`/`127.0.0.54`. None on `192.168.5.2`.
- `/` had 206 GB free. `resolvectl status` listed no DNS servers on any link.

### Install

1. Encrypted OPNsense backup downloaded, stored outside Git, confirmed to
   contain no readable `<opnsense>` text.
2. AdGuard Home `v0.107.79` (`AdGuardHome_linux_amd64.tar.gz`) downloaded from
   the official GitHub release; `sha256sum -c checksums.txt` returned `OK`.
3. Unpacked to `/opt/AdGuardHome`. Setup wizard started with
   `-h 192.168.5.2 -p 3000`; `ss` showed only `192.168.5.2:3000`.
   Wizard: web `192.168.5.2:3000`, DNS `192.168.5.2:53`.
4. Installed with `./AdGuardHome -s install`; service `active (running)`,
   `enabled`, listeners only on `192.168.5.2`.
5. Upstream set to `192.168.5.1`; Query Log details: `DNS server: 192.168.5.1:53`,
   `NOERROR`, 15 ms.
6. Lists: AdGuard DNS filter (default) + HaGeZi's Pro Blocklist (about 277,000
   rules). `nslookup doubleclick.net 192.168.5.2` → `0.0.0.0`, `::`.
7. A second foreground start of the wizard command while the service ran failed
   with `session_storage ... timeout` and exited. Harmless: the service holds the
   session database.
8. Dashboard password reset by editing the `users:` hash in `AdGuardHome.yaml`
   with the service stopped. A brief `activating` state was seen; the journal
   showed a clean start and a normal `terminated` stop (the service had been
   stopped on purpose), no config error.

### LAN client tests (Windows PC, wired, 2026-10-02)

- Wired lease `192.168.5.90`, DHCP server/gateway/DNS `192.168.5.1` (before the
  DHCP option). `example.com` resolved through Unbound. `doubleclick.net`
  resolved to real addresses: the baseline, unfiltered.
- Early tests to `192.168.5.2` timed out (`Test-NetConnection` reported
  `InterfaceAlias: Tailscale`, source `100.x`): with Tailscale connected the PC
  routed `192.168.5.x` through the tunnel, where ports `53` and `3000` failed
  and `22` worked. With Tailscale disconnected: `InterfaceAlias: Ethernet 2`,
  source `192.168.5.90`, port `53` reachable, `example.com` resolved,
  `doubleclick.net` → `0.0.0.0`/`::`, `ping 192.168.5.1` 0% loss.
- DHCP option `dns-server [6]` = `192.168.5.2` added (the first attempt used
  the `Option6` DHCPv6 field and was rejected), then **Apply**. Before Apply the
  lease still showed DNS `192.168.5.1`. After Apply and renew the DNS was
  `192.168.5.2` and `doubleclick.net` returned `0.0.0.0`/`::`.
- Allowlist cycle: Unblock `doubleclick.net` → real address; delete the allow
  rule → blocked again.
- IPv4 DNS `{192.168.5.2}`, IPv6 DNS `{}`; only a link-local `fe80::` IPv6
  address. `Resolve-DnsName doubleclick.net -Server 1.1.1.1` returned real
  addresses (bypass is possible).

### Reboot check (2026-10-03)

At `uptime` `up 15:56`: `virsh list` showed `opnsense` `running` (Id 1),
`Autostart: enable`; AdGuard Home `active` (PID 1825) with listeners on
`192.168.5.2`; blocked lookup returned `0.0.0.0`/`::`. The reboot happened
about 16 hours earlier, so boot behaviour is inferred from the low IDs.

### Unresolved

- Why ports `53` and `3000` to `192.168.5.2` fail through Tailscale while `22`
  works. `docs/03` describes broad rules, so this contradicts the recorded
  config; inspect the live Grants/Access controls and OPNsense TAILSCALE rules.
- The `192.168.5.90` lease versus the recorded `.100`–`.200` pool.
- Whether log rotation/statistics retention saved a short value.
- A `ping 192.168.5.1` timeout seen once with Tailscale connected was not
  re-run in isolation; with Tailscale off it succeeded.

### Rollback (as designed)

- Undo DHCP: delete/disable the Dnsmasq DHCP option, Apply, renew leases.
- Stop the filter: `sudo systemctl stop AdGuardHome` (then DHCP must be rolled
  back too, or clients lose DNS).
- Remove the service: `sudo /opt/AdGuardHome/AdGuardHome -s uninstall`.
- Restore OPNsense from the encrypted backup if needed. No restore test has
  been run.
