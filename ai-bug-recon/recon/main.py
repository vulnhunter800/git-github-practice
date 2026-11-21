"""Command-line entry point for AI Bug Recon."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from recon.analysis import find_candidate_ai_urls
from recon.runner import collect_urls, discover_subdomains, probe_hosts, tool_exists


DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$"
)


def validate_domain(value: str) -> str:
    domain = value.strip().lower().rstrip(".")
    if not DOMAIN_RE.fullmatch(domain):
        raise argparse.ArgumentTypeError("Enter a valid domain, e.g. example.com (no scheme or path).")
    return domain


def host_from_url(value: str) -> str | None:
    parsed = urlparse(value if "://" in value else f"https://{value}")
    return parsed.hostname


def in_scope(host: str | None, domain: str) -> bool:
    return bool(host and (host == domain or host.endswith("." + domain)))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-bug-recon",
        description="Collect authorized target recon data and highlight possible AI routes.",
    )
    parser.add_argument("--domain", required=True, type=validate_domain, help="Authorized target domain")
    parser.add_argument("--out", default=None, help="JSON report path (default: reports/<domain>.json)")
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Actively make HTTP requests to discovered hosts using ProjectDiscovery httpx.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    domain = args.domain
    output_path = Path(args.out) if args.out else Path("reports") / f"{domain}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[*] AI Bug Recon starting for: {domain}")
    print("[!] Use only on assets you own or are authorized to assess.")

    subdomains_result = discover_subdomains(domain)
    urls_result = collect_urls(domain)

    subdomains = sorted({
        item.lower().strip(".")
        for item in subdomains_result.items
        if in_scope(item.strip(), domain)
    })

    urls = sorted({
        item for item in urls_result.items
        if in_scope(host_from_url(item), domain)
    })

    ai_urls = find_candidate_ai_urls(urls)

    probe_result = None
    if args.probe:
        hosts = [f"https://{host}" for host in subdomains]
        probe_result = probe_hosts(hosts)

    tools = {
        "subfinder": {
            "available": subdomains_result.available,
            "error": subdomains_result.error,
        },
        "gau": {
            "available": urls_result.available,
            "error": urls_result.error,
        },
    }
    if probe_result is not None:
        tools["httpx"] = {
            "available": probe_result.available,
            "error": probe_result.error,
        }

    report = {
        "project": "AI Bug Recon",
        "target": domain,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "authorization_notice": "Run only against assets you own or are explicitly authorized to assess.",
        "tools": tools,
        "subdomains": subdomains,
        "urls": urls,
        "candidate_ai_urls": ai_urls,
        "http_probe_results": probe_result.items if probe_result else [],
        "counts": {
            "subdomains": len(subdomains),
            "urls": len(urls),
            "candidate_ai_urls": len(ai_urls),
            "http_probe_results": len(probe_result.items) if probe_result else 0,
        },
    }

    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"[+] Subdomains: {len(subdomains)}")
    print(f"[+] URLs: {len(urls)}")
    print(f"[+] Candidate AI URLs: {len(ai_urls)}")
    if not subdomains_result.available:
        print(f"[!] subfinder: {subdomains_result.error}")
    if not urls_result.available:
        print(f"[!] gau: {urls_result.error}")
    if probe_result and probe_result.error:
        print(f"[!] httpx: {probe_result.error}")
    print(f"[+] Report saved: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
