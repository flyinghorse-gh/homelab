# Chapter 8: Network-wide DNS Filtering

!!! success "Status: verified (core filtering)"
    The filtering steps below were built and confirmed on the author's own
    homelab. Encrypted upstream DNS and enforcement against devices that
    ignore your DNS server are **not** covered here; they are listed as planned
    work at the end. Your versions may differ slightly, so check each step's
    result before moving on.

- **Last verified:** 2026-10-03, on the author's build
- **Tools:** AdGuard Home (on the Ubuntu host), OPNsense Unbound, OPNsense Dnsmasq DHCP

## Goal

Block ad, tracker and telemetry domains for every device on your private LAN,
with a dashboard that lets you turn blocking off, add exceptions, and (later)
set rules per device.

## How it works

**DNS** (Domain Name System) turns a name like `example.com` into an IP
address. Every device asks a **DNS server** before it connects to a site. A
**DNS filter** is a DNS server that refuses to answer for names on a
**blocklist**, so the device never reaches the ad or tracker server.

The path you will build:

```text
LAN device → AdGuard Home (Ubuntu host) → Unbound (OPNsense) → the internet
```

- **AdGuard Home** is the filter. It runs on the Ubuntu host as a service and
  has the dashboard.
- **Unbound** is the DNS resolver already running on OPNsense. In this build it
  looks names up itself (called *recursive* mode) and does not forward them to
  another provider. AdGuard Home passes allowed questions to it.
- **DHCP** is the service that gives devices their address and tells them
  which DNS server to use. You will change that one setting.

**What this does not do.** DNS filtering blocks by domain. It cannot remove an
ad served from the same domain as the content you want (for example, most
YouTube ads). It does not make you anonymous: sites still see your public IP,
and your internet provider still sees which IP addresses you connect to. A
device or app that uses its own DNS server also skips the filter (see
[Planned](#planned-not-yet-done)).

## Prerequisites

- Chapters 1–5 complete (OPNsense is routing and a LAN client gets a lease).
- A way to reach the Ubuntu host over SSH.
- A LAN client you can connect by cable for testing. Plan about 3 hours.

## Choose the filter

Both options below block domains. I chose AdGuard Home because the goal was an
easy on/off switch and per-device rules.

| | Unbound blocklists (built into OPNsense) | AdGuard Home |
|---|---|---|
| Nothing new to install | Yes | No, one extra service |
| Easy on/off | Checkbox plus Apply in the WebGUI | One toggle in a dashboard |
| Per-device rules | Limited: restrict blocking to chosen source addresses, same lists for all | Yes: separate lists and rules per device |
| Query log per device | Basic reporting | Searchable log |

If you only want simple, always-on blocking, Unbound's built-in blocklist is
a reasonable, smaller choice. The rest of this chapter follows AdGuard Home.

!!! note "Where to run it"
    There was no AdGuard Home plugin available in the OPNsense plugin list of
    the author's version (`26.7`), even with community plugins enabled. Running
    it on the Ubuntu host also keeps third-party software off the firewall.

## Section 8.1: Inspect the current DNS setup (read-only)

**Where:** OPNsense WebGUI. Change nothing and do not click Apply.

1. **Services → Unbound DNS → General:** note whether Unbound is enabled, its
   port (`53`), and its interfaces.
2. **Services → Unbound DNS → Query Forwarding:** on the author's stock install
   the only entry was a rule sending the local `home.arpa` names to Dnsmasq on
   port `53053`, and "Use System Nameservers" was unchecked. That means Unbound
   resolves recursively.
3. **Services → Unbound DNS → Blocklist** and **DNS over TLS:** both were empty
   and disabled.
4. **Services → Dnsmasq DNS & DHCP → General:** Dnsmasq handles DHCP on the
   LAN and listens for DNS on `53053`, so it does not clash with Unbound.
5. **DHCP ranges** and **DHCP options:** the LAN range exists and the options
   table is empty, so clients are handed the OPNsense address as their DNS
   server by default.

**Verify:** you know whether DNS is recursive or forwarding, and that no
blocklist or custom DHCP DNS option exists yet.

**Rollback:** none, nothing changed.

## Section 8.2: Take a backup first

**Where:** OPNsense WebGUI.

1. **System → Configuration → Backups.**
2. Tick **Encrypt this configuration file**, set a password, and store the
   password in a password manager.
3. Click **Download configuration** and save the file **outside** your Git
   repository.

**Verify:** the file exists. Check it is really encrypted, in Windows
PowerShell:

```powershell
Select-String -Path "<BACKUP_FILE>" -Pattern "<opnsense>" -SimpleMatch
```

No output means no readable configuration text, so the file is encrypted. If a
line is printed, delete that copy and repeat with encryption ticked.

**Rollback:** not applicable; this only creates a backup.

## Section 8.3: Check the host is ready

**Where:** Ubuntu host over SSH. Run these one at a time. If `sudo` asks for a
password, a multi-line paste can feed later lines into the password prompt.

```bash
ip -br addr show br-lan
sudo ss -tulpn | grep ':53 '
df -h /
```

**Verify:**

- `br-lan` is `UP` with the host's LAN address.
- Nothing is listening on port `53` at that LAN address. Ubuntu's own resolver
  listens on loopback addresses such as `127.0.0.53`, which does not conflict.
- There is plenty of free disk space.

**Rollback:** none, read-only.

## Section 8.4: Download and verify AdGuard Home

**Where:** Ubuntu host.

```bash
uname -m
mkdir -p ~/agh-download && cd ~/agh-download
curl -fLO https://github.com/AdguardTeam/AdGuardHome/releases/latest/download/AdGuardHome_linux_amd64.tar.gz
curl -fLO https://github.com/AdguardTeam/AdGuardHome/releases/latest/download/checksums.txt
sha256sum --ignore-missing -c checksums.txt
```

`uname -m` should print `x86_64` (use the matching archive name if it does
not). A **checksum** is a fingerprint that shows the file was not corrupted or
swapped.

**Verify:** the last command prints `AdGuardHome_linux_amd64.tar.gz: OK`. If it
says `FAILED`, stop and do not use the file.

**Rollback:** `rm -rf ~/agh-download`.

## Section 8.5: Unpack it and run the setup wizard on the LAN address only

AdGuard Home's first-run wizard listens on **every** network interface by
default. If the host also has a connection to your upstream network, that
would expose the setup page there. Bind it to the LAN address instead.

**Where:** Ubuntu host. Replace `<HOST_LAN_IP>` with the host's LAN address
(the one on `br-lan`).

```bash
sudo tar -xzf ~/agh-download/AdGuardHome_linux_amd64.tar.gz -C /opt
/opt/AdGuardHome/AdGuardHome --version
sudo /opt/AdGuardHome/AdGuardHome -h <HOST_LAN_IP> -p 3000
```

The last command keeps running in that terminal. In a **second** SSH session:

```bash
sudo ss -tlnp | grep 3000
```

**Verify:** the listener shows `<HOST_LAN_IP>:3000`. If it shows `0.0.0.0` or
`*`, press Ctrl+C in the first session and stop here.

Now open the wizard. If your PC can reach the host directly on the LAN, browse
to `http://<HOST_LAN_IP>:3000`. Otherwise use an SSH tunnel from your PC (see
the troubleshooting note below), then browse to `http://localhost:3000`.

In the wizard:

- **Admin web interface:** `<HOST_LAN_IP>`, port `3000`.
- **DNS server:** `<HOST_LAN_IP>`, port `53`.
- Choose an admin username and a strong password, and save it in a password
  manager.
- Skip any suggestion to point your devices at it; that comes later.

**Verify:** the dashboard loads, and in the second session
`sudo ss -tulpn | grep AdGuard` lists only `<HOST_LAN_IP>` addresses.

**Rollback:** Ctrl+C in the first session, then
`sudo rm /opt/AdGuardHome/AdGuardHome.yaml` to discard the wizard's settings.

## Section 8.6: Run it as a service

A **service** starts at boot and restarts if it crashes. The wizard saved the
LAN binding into the config file, so the service needs no extra flags.

**Where:** Ubuntu host. First press Ctrl+C in the wizard session.

```bash
cd /opt/AdGuardHome
sudo ./AdGuardHome -s install
sudo systemctl status AdGuardHome --no-pager
sudo ss -tulpn | grep AdGuard
systemctl is-enabled AdGuardHome
```

**Verify:** `active (running)`, listeners only on `<HOST_LAN_IP>` (DNS port
`53` over UDP and TCP, dashboard port `3000`), and `enabled`.

!!! warning "Do not run the wizard command again"
    With the service running, starting the foreground command a second time
    fails with a `session_storage ... timeout` error. That is harmless: the
    service already holds the database. Manage it with `systemctl`.

**Rollback:** `sudo /opt/AdGuardHome/AdGuardHome -s uninstall`.

## Section 8.7: Point AdGuard Home at Unbound

**Where:** AdGuard dashboard → **Settings → DNS settings**.

1. **Upstream DNS servers:** replace the contents with one line:
   `<OPNSENSE_LAN_IP>`
2. **Fallback DNS servers:** clear any entries. A fallback would quietly send
   queries to a public resolver if Unbound failed.
3. Leave **Bootstrap DNS servers** alone; it is only used to look up the names
   of encrypted upstreams, and yours is an IP address.
4. Click **Test upstreams**, then **Apply**.

**Verify:** on the Ubuntu host:

```bash
nslookup example.com <HOST_LAN_IP>
```

It returns an address. In the dashboard **Query Log**, click the row: the
details show **DNS server: `<OPNSENSE_LAN_IP>:53`** and response code
`NOERROR`.

**Rollback:** restore the previous upstream line, or
`sudo systemctl stop AdGuardHome`. No device uses it yet.

## Section 8.8: Turn on blocklists and keep logs short

**Where:** AdGuard dashboard.

1. **Filters → DNS blocklists:** keep the default **AdGuard DNS filter**.
   Add **HaGeZi's Pro Blocklist** (ads, trackers, telemetry; the author's
   copy loaded roughly 277,000 rules). Start with one extra list: stacking
   many lists adds false positives for little extra blocking. The larger
   "Pro++" and "Ultimate" variants block more but break more.
2. **Settings → General settings:** set the query-log rotation and statistics
   retention to a short period such as 24 hours. Leave **Browsing security**
   and **Parental control** off, because those send queries to AdGuard's
   servers.

**Verify:** on the Ubuntu host:

```bash
nslookup doubleclick.net <HOST_LAN_IP>
```

A blocked name returns `0.0.0.0` (and `::`), and the Query Log shows it as
blocked. A normal name such as `example.com` still resolves.

**Rollback:** untick or remove the list under **Filters → DNS blocklists**.

## Section 8.9: Test from a real LAN client

Do this **before** changing DHCP, so you know the whole path works.

**Where:** a PC connected by cable to the LAN port, with its other
connections (Wi-Fi, VPN) off.

1. Confirm the lease and path:

   ```powershell
   ipconfig /all
   Find-NetRoute -RemoteIPAddress <HOST_LAN_IP> | Select-Object InterfaceAlias, NextHop
   ```

   The address is in your LAN subnet and the interface alias is the wired
   adapter.
2. Ask AdGuard directly:

   ```powershell
   Resolve-DnsName example.com -Server <HOST_LAN_IP>
   Resolve-DnsName doubleclick.net -Server <HOST_LAN_IP>
   ```

**Verify:** the first returns addresses; the second returns `0.0.0.0` and `::`.

!!! warning "Disconnect Tailscale on the test PC"
    If the PC runs Tailscale and accepts subnet routes, Windows can send
    LAN-address traffic through the Tailscale tunnel instead of the cable. On
    the author's build that produced timeouts to the host on ports 53 and 3000
    while the same tests worked once Tailscale was off. Always check which
    interface a test used (`InterfaceAlias`) before drawing conclusions.

**Rollback:** re-enable the PC's other connections. No server settings changed.

## Section 8.10: Hand AdGuard Home out through DHCP

!!! danger "This affects every device on the LAN"
    Devices will use AdGuard Home on the host as their only DNS server. If the
    host or the service is down, DNS stops for them. A second DNS server would
    keep working but would let devices skip the filter, so this build uses one.

**Where:** OPNsense WebGUI → **Services → Dnsmasq DNS & DHCP → DHCP options**.

1. Click **+**.
2. **Interface:** LAN. **Type:** Set.
3. **Option:** `dns-server [6]`. **Leave Option6 empty.** The form has two
   dropdowns: *Option* is for IPv4, *Option6* is for IPv6 and rejects an IPv4
   address with "Only IPv6 addresses are allowed".
4. **Value:** `<HOST_LAN_IP>`. Leave Tag empty and Force unchecked.
5. **Save**, then click **Apply**. Without Apply nothing changes.

**Verify** on the test PC:

```powershell
ipconfig /release
ipconfig /renew
ipconfig /all
Resolve-DnsName doubleclick.net
```

The wired adapter's DNS server is `<HOST_LAN_IP>`, and `doubleclick.net`
returns `0.0.0.0`. If it still returns real addresses, run
`ipconfig /flushdns` and test again.

**Rollback:** delete the option (or untick Enable) in **DHCP options**, click
**Apply**, then `ipconfig /renew` on the client. A single PC can also be
recovered by setting its DNS to `<OPNSENSE_LAN_IP>` by hand.

## Section 8.11: Check everyday use and practise an exception

1. Browse sites you actually use (search, video, shopping or banking). Logins
   and pages should work; ads and trackers should disappear.
2. In the **Query Log**, find a blocked entry, open its `⋮` menu and choose
   **Unblock**. Run `ipconfig /flushdns` and look the name up again: it now
   returns a real address.
3. Undo it: **Filters → Custom filtering rules**, delete the allow line
   (it looks like `@@||name^`), **Apply**, flush the cache, and confirm it is
   blocked again.

**Verify:** the exception worked and the re-block worked.

**Rollback:** removing the rule in step 3 is the rollback.

## Section 8.12: Check IPv6 and reboot recovery

1. **IPv6.** Router advertisements can hand out an IPv6 DNS server that skips
   the filter. On the test PC:

   ```powershell
   Get-DnsClientServerAddress -InterfaceAlias "<WIRED_ADAPTER>"
   Get-NetIPAddress -InterfaceAlias "<WIRED_ADAPTER>" -AddressFamily IPv6
   ```

   On the author's LAN the IPv6 DNS list was empty and the PC had only a
   link-local `fe80::` address, so no IPv6 path skips AdGuard. Recheck if your
   LAN gets routed IPv6.
2. **Reboot.** Reboot the Ubuntu host with `sudo reboot`. Impact: the OPNsense
   VM goes down with it, so the LAN has no routing, DHCP or DNS for a few
   minutes. After it returns:

   ```bash
   uptime
   virsh list --all
   virsh dominfo opnsense | grep -i autostart
   systemctl is-active AdGuardHome
   sudo ss -tulpn | grep AdGuard
   nslookup doubleclick.net <HOST_LAN_IP>
   ```

**Verify:** the `opnsense` VM is `running` and autostart is `enable`, AdGuard
Home is `active` with listeners on `<HOST_LAN_IP>`, and the blocked name still
returns `0.0.0.0`. On the author's build these all held, though the check was
run about 16 hours after the reboot rather than minutes after it. A low
process ID for AdGuard Home and a low VM ID were the evidence it started at
boot.

**Rollback:** if the host does not return, connect a monitor and keyboard. If
only AdGuard failed, `sudo systemctl restart AdGuardHome`. If only the VM
failed, `virsh start opnsense`.

## Planned (not yet done)

These are intentionally outside this chapter's verified scope:

- **Encrypted upstream DNS (DNS over TLS).** Today Unbound resolves on its own
  over ordinary DNS, so your internet provider can see that traffic. Encrypting
  it moves trust to whichever resolver you pick. Choose one with a no-logging
  policy you accept.
- **Stopping devices from skipping the filter.** An app or device that uses its
  own DNS server (a lookup straight to a public resolver still returned real
  addresses on the author's PC) bypasses AdGuard Home. A firewall rule that
  limits port `53` helps but does not stop encrypted DNS inside a browser or a
  VPN. This needs a separate, deliberate rule with a rollback.
- **Per-device rules**, once you decide which devices need different treatment.
- **Anonymity.** A VPN or Tor for outbound traffic is a separate chapter. A
  VPN only moves trust from your provider to the VPN company.

## Troubleshooting and FAQ

??? question "The dashboard will not open from my PC"
    First check whether your remote-access tool is sending LAN traffic through
    its tunnel (see the Tailscale warning in 8.9). If your access rules allow
    only some ports, a dashboard on port `3000` can time out even though SSH
    works. A safe workaround that changes no firewall rule is an SSH tunnel
    from your PC: `ssh -L 3000:<HOST_LAN_IP>:3000 <USER>@<HOST_LAN_IP>`, then
    browse to `http://localhost:3000` while it stays open.

??? question "I forgot the AdGuard Home password"
    The dashboard has no password-reset page. Edit the config file instead.
    Make a hash with `htpasswd -nBC 10 <USERNAME>` (install `apache2-utils`
    first), copy only the part after the colon, stop the service
    (`sudo systemctl stop AdGuardHome`), put the hash after `password:` in the
    `users:` section of `/opt/AdGuardHome/AdGuardHome.yaml` keeping the
    indentation, then start the service. Stop the service first, because it
    rewrites the file when it shuts down. Delete any backup copy of the file
    afterwards, since it contains a password hash. Never paste that file into
    chat or Git.

??? question "The service says 'activating' and the page will not load"
    Read the log: `sudo journalctl -u AdGuardHome -n 25 --no-pager`. Use that
    exact form; plain `journalctl` opens the whole system log. If the log shows
    a clean start followed by `received signal terminated`, someone stopped the
    service; start it with `sudo systemctl start AdGuardHome`. A config-file
    error will name the file; restore your backup copy.

??? question "A site I need is broken"
    Open the Query Log, find the blocked entry, and use **Unblock** for that
    name only. Prefer one small exception over removing a whole list.

??? question "Why not give clients two DNS servers for safety?"
    Devices use either server, so a second one that is not AdGuard Home lets
    them skip the filter. The cost of one server is that DNS stops if the host
    does.

??? question "Does this stop my internet provider seeing what I visit?"
    No. See the limits at the top and the planned items above.

??? question "Can I block YouTube ads this way?"
    No. They come from the same domains as the video. Use a browser extension.
