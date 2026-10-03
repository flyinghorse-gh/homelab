# Glossary

_Terms are added as chapters are written. Each term is defined the first time it
appears in a chapter and collected here._

| Term | Meaning |
|---|---|
| Bridge | A virtual network switch on the host that connects a VM to a physical port. |
| WAN / LAN | The side facing the Internet or upstream router / your private network. |
| DDNS | Dynamic DNS: a name that follows your changing public IP address. |
| DNS | Domain Name System: turns a name like `example.com` into an IP address. |
| Resolver | A DNS server that looks names up for your devices (Unbound on OPNsense). |
| Recursive mode | A resolver looks names up itself instead of forwarding them to another provider. |
| Upstream | The next DNS server a resolver or filter passes a question to. |
| DNS filter | A DNS server that refuses to answer for names on a blocklist. |
| Blocklist / allowlist | Lists of names to refuse / to always allow. |
| DHCP | Gives devices an address and tells them which DNS server to use. |
| DHCP option 6 | The DHCP setting that names the DNS server(s) clients should use. |
| Service | A program managed by the operating system that starts at boot and restarts if it fails. |
| Checksum | A fingerprint of a file, used to confirm a download is intact. |
| SSH tunnel | Carries a port from your PC to the server inside an existing SSH connection. |
| DoT | DNS over TLS: encrypts DNS questions between a resolver and its upstream. |
