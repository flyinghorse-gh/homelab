# Chapter 6: Dynamic DNS with DuckDNS

!!! success "Status: verified"
    Built and confirmed working on the author's own homelab. Your hardware and
    versions may differ slightly, so check each step's result before moving on.

- **Last verified:** 2026-09-27, on the author's build
- **Service:** DuckDNS (free)

## Goal

Set up Dynamic DNS so your hostname stays updated as your public IP changes.

## Prerequisites

- Chapter 5 complete | DuckDNS account + token from https://duckdns.org | 30 min

## Section 6.1: Create DuckDNS Account

1. Go to https://duckdns.org
2. Sign in (GitHub/Google/email)
3. Create domain: e.g., `<myname>.duckdns.org`
4. Note your token (keep secret; never commit to Git)

## Section 6.2: Install in OPNsense

In WebGUI:

1. **System > Firmware > Plugins**
2. Install `os-ddclient`
3. **Services > Dynamic DNS > Settings**
4. Add entry:
   - Service: DuckDNS
   - Hostname: `<myname>`
   - Token: `<your-token>`
   - Enable: checked

## Section 6.3: Verify

```bash
# From outside your network (different ISP or phone hotspot)
nslookup <myname>.duckdns.org
ping <myname>.duckdns.org  # Should resolve and work
```

## Important Notes

- **Updates IPv4 only.** IPv6 is separate.
- **Does not expose network.** Just keeps hostname updated. Firewall still blocks unwanted inbound.
- **Keep token secret.** If leaked, regenerate at duckdns.org.

## Rollback

In WebGUI: **Services > Dynamic DNS > Delete entry**

## FAQ

??? question "Why DuckDNS?"
    Free, simple, no ads. Alternatives: FreeDNS, Namecheap, etc.

??? question "Failed update?"
    Check: **System > Log Files > Dynamic DNS** for errors.

---

**Next:** [Chapter 7: Secure Remote Access with Tailscale](07-secure-remote-access-with-tailscale.md)
