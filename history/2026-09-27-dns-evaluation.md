# 2026-09-27 — DNS Evaluation and Read-Only Baseline

Read the required repository documentation, prior agenda, and relevant DOCX
sections. Reviewed FUTO's ad-blocking chapter and official OPNsense/AdGuard
documentation. Added [comparison and inspection notes](../docs/05-dns-filtering.md).
Unbound is provisionally recommended for fewer additional dependencies; no
architecture decision has been made, so no new accepted ADR was added.

Fresh Windows observations: upstream Wi-Fi active; Ethernet disconnected;
OPNsense LAN route selected through Tailscale. The default resolver
`75.75.75.75` and explicit resolver `192.168.5.1` returned answers for
`example.com`; an explicit AAAA query to OPNsense also succeeded. Sandboxed
timeouts were followed by successful outside-sandbox queries, not classified
as a homelab failure. The user reports the WebGUI opens.

The user subsequently reported OPNsense `26.7.4_1-amd64`, FreeBSD
`15.1-RELEASE-p3`, and OpenSSL `3.5.8` from the WebGUI. Unbound is enabled with
port `53`, interfaces `All`, and DNSSEC unchecked. Recorded as user-observed
settings, not independently retrieved configuration. DHCP backend,
advertised DNS, forwarding/recursion, IPv6 DNS, browser overrides, and a direct
LAN test client remain unverified. Updated current state, network details,
installation history, README, and handoff with these limits.

Only documentation was edited. No infrastructure settings changed, packages
installed, service restarts, commits, or pushes were performed.
