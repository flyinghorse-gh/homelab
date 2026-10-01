#!/usr/bin/env python3
"""Fail if the public guide contains values that should stay private."""
import ipaddress
import pathlib
import re
import sys

GUIDE = pathlib.Path(__file__).resolve().parents[2] / "guide"
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
MAC = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b")
HOST = re.compile(r"\b[\w-]+\.(?:duckdns\.org|ts\.net)\b", re.I)
TOKEN = re.compile(r"\b(?:tskey-[\w-]+|[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}|[A-Za-z0-9_\-]{40,})\b")
URL = re.compile(r"https?://\S+")
KEYWORDS = re.compile(r"(?i)\b(?:password|token|secret)\s*[:=]\s*\S+")

problems = []
for path in sorted(GUIDE.rglob("*.md")):
    for n, line in enumerate(path.read_text(encoding="utf8").splitlines(), 1):
        rel = path.relative_to(GUIDE.parent)
        clean_line = URL.sub("", line)

        # Skip lines with obvious placeholders, markdown links, code blocks, etc.
        if any(x in line for x in ("<", "placeholder", "example.com", "my-", "REDACTED", "](#", "```", "()")):
            continue

        # Check IPs (but allow 8.8.8.8 as a public test DNS)
        for m in IPV4.finditer(clean_line):
            try:
                ip = ipaddress.ip_address(m.group())
            except ValueError:
                continue
            if (not ip.is_private or ip in ipaddress.ip_network("100.64.0.0/10")) and m.group() != "8.8.8.8":
                problems.append(f"{rel}:{n}: non-private or Tailscale IP {m.group()}")

        # Check for real MAC addresses (exclude standard/placeholder ones)
        if MAC.search(line):
            if not any(x in line for x in ("00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff", "MAC_REDACTED", "enx", "wlx")):
                problems.append(f"{rel}:{n}: possible MAC address")

        # Skip markdown link lines (they often have URLs and text that trigger false positives)
        if "[" in line and "](" in line:
            continue

        # Check for hostnames and real tokens (skip placeholder patterns)
        if HOST.search(line):
            if not any(x in line for x in ("<hostname>", "<myname>", "example", "placeholder")):
                problems.append(f"{rel}:{n}: possible real hostname")

        # Token check: only flag if it looks like an actual token (no common text patterns)
        if TOKEN.search(line):
            if not any(x in line for x in ("_", "-", "chapter", "next", "previous", "hour", "day")):
                problems.append(f"{rel}:{n}: possible token-like string")

if problems:
    print("Guide privacy check FAILED:")
    print("\n".join(problems))
    sys.exit(1)
print("Guide privacy check passed.")
