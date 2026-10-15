# Chapter 9: Encrypted Upstream DNS with Quad9

!!! success "Status: verified"
    Built and confirmed on the author's own homelab. A packet capture showed
    encrypted DNS leaving the WAN. One check (that no plain DNS leaves) used a
    short quiet window, so repeat it while browsing, as described below. Your
    OPNsense version may label fields slightly differently.

- **Last verified:** 2026-10-14, on the author's build
- **Tools:** OPNsense Unbound, a packet capture on the Ubuntu host

## Goal

Stop your internet provider from reading the website names your home network
looks up, and keep the blocking from Chapter 8 working.

## How it works

At the end of Chapter 8, the path was:

```text
LAN device → AdGuard Home → Unbound (OPNsense) → root and site name servers
```

The last hop leaves your house as ordinary DNS, which anyone on the line, such
as your internet provider, can read. **DNS over TLS (DoT)** wraps a DNS
question in the same encryption websites use. Unbound can send every question
to one resolver over DoT instead of asking the internet itself:

```text
LAN device → AdGuard Home → Unbound (OPNsense) ══TLS══> Quad9
```

A **resolver** is the DNS server that answers for you. You are choosing whom to
trust: before, nobody saw your lookups except your provider as they passed;
now your provider sees only an encrypted connection to Quad9, and Quad9 sees
the lookups. Quad9 is a Swiss non-profit whose published policy says it does
not store the IP addresses or query names of the people asking. That is its
stated policy; you cannot verify it yourself.

**What this does not do.** Your provider can still see the IP addresses of the
sites you connect to, and often the site name in the connection set-up. This is
not anonymity. Hiding destinations needs a VPN, which just moves trust to the
VPN company.

## Prerequisites

- Chapter 8 complete, with filtering verified.
- An encrypted OPNsense configuration backup, stored outside your Git folder.
- Plan about 30 minutes.

## Choose the resolver

| Choice | Result |
|---|---|
| Quad9 on `dns.quad9.net` | Free. Blocks known malware domains by default. Used here. |
| Quad9 `dns11` variant | Also sends part of your network address to servers (called ECS). Avoid for privacy. |
| A resolver you rent and run yourself | More control, costs money and needs a public port to secure. A bigger change; not covered here. |
| Mullvad DNS | Its own page announces it ends on 2026-11-02, so do not build on it. |

Check the provider's current policy before relying on it. Services change.

## Steps

### 1. Back up OPNsense (WebGUI)

1. **System → Configuration → Backups**.
2. Tick **Encrypt this configuration file** and set a passphrase.
3. **Download configuration**, then store the file outside your Git folder.

**Verify:** the file exists in your protected storage. Do not paste it or its
passphrase anywhere.

### 2. Add Quad9 as the DoT upstream (WebGUI)

1. **Services → Unbound DNS → DNS over TLS**.
2. Add an entry: **Server IP** `9.9.9.9`, **Port** `853`, **Verify CN**
   `dns.quad9.net`, description `Quad9 DoT`.
3. Add a second entry: `149.112.112.112`, port `853`, CN `dns.quad9.net`.
4. **Save**, then **Apply**.

Leave **Query Forwarding** alone. Its `home.arpa` rule sends local names to
Dnsmasq and must stay. *Verify CN* makes Unbound check the server's certificate
name, so a stranger cannot pretend to be Quad9.

### 3. Verify

**Windows PowerShell:**

```powershell
Resolve-DnsName example.com -Type A
Resolve-DnsName doubleclick.net -Type A
Resolve-DnsName github.com -Type A
```

Expect normal addresses for the first and third, and `0.0.0.0` for
`doubleclick.net` (blocked by AdGuard). The author reported all three passed.

**Ubuntu host**, one command at a time. They only watch the WAN bridge:

```bash
sudo timeout 20 tcpdump -ni br-wan 'port 853' -c 5
sudo timeout 20 tcpdump -ni br-wan 'port 53' -c 5
```

While each runs, open a few sites you have not visited recently on a LAN
device. On the author's build the first capture showed OPNsense's WAN address
exchanging TCP packets with `9.9.9.9` on port `853`. The second showed
**0 packets**, but the window may have been quiet, so repeat it while
browsing; any packets there are plain DNS leaving.

**Cross-check from outside:** run the extended test at a DNS leak test site
from a device that uses your DNS. The author saw only three resolvers, all on
the Quad9 operator's network, and none from the internet provider. If your
provider or your own address appears, Unbound is not using DoT, or that device
is not using your DNS.

## Rollback

On **Services → Unbound DNS → DNS over TLS**, delete both entries and
**Apply**. Unbound goes back to resolving by itself. If something else broke,
restore the backup from step 1.

## Planned (not yet done)

- A second plain-DNS capture while browsing to firmly show nothing leaks.
- Extra malware and threat lists in AdGuard Home that stay on your hardware.
- Stopping devices from using their own DNS (see Chapter 8, Planned).

## Troubleshooting and FAQ

??? question "Nothing resolves after Apply"
    Delete both DoT entries and Apply to return to recursive mode. Then check
    that **Verify CN** is exactly `dns.quad9.net` and that the WAN can reach
    port `853` (some networks block it).

??? question "Does this hide my browsing from my provider?"
    It hides the website names in DNS lookups. The provider still sees the
    IP addresses you connect to. Use a VPN for more, and understand that it
    shifts trust to the VPN company.

??? question "Why not run my own resolver that talks to the internet?"
    Unbound already does. Its questions to the internet's name servers cannot
    be encrypted because those servers mostly do not support DoT. To hide them,
    the traffic must go through an encrypted tunnel to another machine, either a
    resolver such as Quad9 or a server you rent.

??? question "Why is blocking still happening?"
    AdGuard Home still sits in front. This chapter only changes what Unbound
    does after AdGuard Home passes a question on.

---

**Previous:** [Chapter 8: Network-wide DNS Filtering](08-network-wide-dns-filtering.md)
