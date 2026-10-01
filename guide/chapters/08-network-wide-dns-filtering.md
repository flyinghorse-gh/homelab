# Chapter 8: Network-wide DNS Filtering

!!! warning "Status: outline"
    This chapter describes the next milestone. Implementation in progress.

- **Last verified:** Not yet
- **Tools:** Unbound (built-in), AdGuard Home (alternative)

## Goal

Enable DNS-level ad blocking and malware filtering for all LAN devices.

## Prerequisites

- Chapter 8 complete (verified + backed up) | 2–3 hours for evaluation | 1–2 hours for rollout

## Section 9.1: Understand DNS Filtering

DNS filtering intercepts queries to "example.com?" and checks blocklists:
- If blocked: return null response
- If allowed: forward to upstream DNS

**Blocks:** ads, trackers, malware domains
**Doesn't block:** inline ads on allowed domains

## Section 9.2: Compare Options

**Unbound (built-in to OPNsense):**
- Already installed
- Simple, integrated WebGUI
- Recommended for beginners

**AdGuard Home (separate):**
- Richer features
- More learning curve
- Better for advanced users

**Decision:** Try Unbound first (simplest).

## Section 9.3: Enable Unbound

In OPNsense WebGUI:

1. **Services > Unbound DNS > General**
   - Enable: checked
   - Port: 53
   - Interfaces: All

2. **Services > Unbound DNS > Blocklists**
   - Add blocklists (e.g., StevenBlack hosts list)
   - Update: daily

3. **Services > DHCP > LAN**
   - DNS Servers: 192.168.5.1 (OPNsense)

## Section 9.4: Test Filtering

On LAN device:

```bash
# Test blocked domain (should fail or return nothing)
nslookup ads.example.com 192.168.5.1

# Test normal domain (should work)
nslookup google.com 192.168.5.1
```

## Section 9.5: Monitor

In WebGUI: **Services > Unbound DNS > Statistics**

View blocked vs allowed queries.

## Important Notes

- **IPv6 DNS:** Configure separately if enabled
- **Firewall rule:** Optional—block port 53 to non-OPNsense servers
  (Does not prevent VPN/encrypted DNS bypass)
- **Encrypted DNS:** DoT/DoH is advanced topic

## Rollback

In WebGUI: **Services > Unbound DNS > Enable: unchecked**

## FAQ

??? question "Prevent external DNS?"
    Firewall rule can block port 53, but VPN/DoT/DoH bypass it.
    See docs for encrypted DNS handling if needed.

??? question "Add allowlist if blocked by mistake?"
    **Services > Unbound DNS > Advanced > Local Records**
    Add A record for domain to correct IP.

??? question "Which blocklists?"
    Start conservative: StevenBlack hosts (popular, maintained).
    Add more as needed; avoid too many (overlaps, false positives).

??? question "Block YouTube ads?"
    No. YouTube ads are same domain as content.
    Use browser extensions for in-video ad blocking.

---

**Completed!** Full working homelab with DNS filtering. Monitor, tune blocklists,
explore advanced features per your needs.

For help: see [OPNsense docs](https://docs.opnsense.org/),
[FUTO guide](https://wiki.futo.org/), community forums.
