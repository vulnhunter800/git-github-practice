# AI Bug Recon

A small, Kali-friendly reconnaissance helper for **authorized AI application security assessments**.

It collects candidate subdomains and URLs, highlights URL paths that may belong to AI-related functionality, and writes a JSON report. It does **not** exploit vulnerabilities or attempt authentication bypasses.

## Features

- Accepts one target domain.
- Uses `subfinder` for subdomain discovery when installed.
- Uses `gau` for passive URL collection when installed.
- Optionally probes discovered hosts with ProjectDiscovery `httpx` (`--probe`).
- Highlights candidate AI-related routes using simple keyword heuristics.
- Saves findings as JSON.
- Keeps tool failures visible instead of silently pretending a scan succeeded.

## Requirements

- Python 3.9+
- Kali Linux (recommended) or another Linux environment.
- Optional external tools: `subfinder`, `gau`, and ProjectDiscovery's `httpx`.

> Only run this tool against domains you own or are explicitly authorized to assess. `--probe` makes HTTP requests to discovered hosts. Without `--probe`, the tool only runs the configured discovery/URL collection tools.

## Kali setup

```bash
sudo apt update
sudo apt install -y python3
```

Install the optional ProjectDiscovery tools using their official installation instructions:
- subfinder: https://github.com/projectdiscovery/subfinder
- httpx: https://github.com/projectdiscovery/httpx
- gau: https://github.com/lc/gau

Check that the correct binaries are available:

```bash
subfinder -version
httpx -version
gau --version
```

There is no mandatory third-party Python package.

## Run

From the project root:

```bash
python3 -m recon.main --domain example.com
```

Save to a chosen report path:

```bash
python3 -m recon.main --domain example.com --out reports/example-com.json
```

Optionally probe discovered hosts for HTTP response metadata:

```bash
python3 -m recon.main --domain example.com --probe
```

The example domain is a placeholder. Replace it only with an authorized target.

## Output

The JSON report includes:
- target domain
- UTC timestamp
- tools found / missing
- discovered subdomains
- collected URLs
- candidate AI-related URLs
- optional HTTP probe results
- warnings and tool errors

## Project layout

```text
ai-bug-recon/
├── README.md
├── .gitignore
├── requirements.txt
├── recon/
│   ├── __init__.py
│   ├── main.py
│   ├── runner.py
│   └── analysis.py
├── tests/
│   └── test_analysis.py
├── output/
│   └── .gitkeep
└── reports/
    └── .gitkeep
```

## Git learning exercises

1. `git status` — inspect the new project files.
2. `git add README.md` — stage one file.
3. `git diff --cached` — inspect staged changes.
4. `git add .` — stage the remaining project files.
5. `git commit -m "Add AI Bug Recon starter project"` — create a local snapshot.
6. `git push` — upload the commit to your GitHub repository.

Before staging, inspect the files and ensure you have not added credentials, private keys, or real target data.

## Upcoming Features

- AI-assisted endpoint classification
- Identify potentially sensitive API routes
- Generate structured reconnaissance reports