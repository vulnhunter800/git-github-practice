"""Safe wrappers around optional command-line recon tools."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class ToolResult:
    tool: str
    available: bool
    items: list[str]
    error: str | None = None


def tool_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run_lines(command: list[str], tool_name: str, timeout: int = 180) -> ToolResult:
    """Run a tool with a fixed argument list; return stdout lines or an error."""
    if not tool_exists(command[0]):
        return ToolResult(tool_name, False, [], f"{command[0]} not found in PATH")

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if completed.returncode != 0:
            message = (completed.stderr or completed.stdout).strip()
            return ToolResult(
                tool_name, True, [],
                message or f"Exited with status {completed.returncode}",
            )
        lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        return ToolResult(tool_name, True, lines)
    except subprocess.TimeoutExpired:
        return ToolResult(tool_name, True, [], f"Timed out after {timeout} seconds")
    except OSError as exc:
        return ToolResult(tool_name, True, [], str(exc))


def discover_subdomains(domain: str) -> ToolResult:
    return run_lines(["subfinder", "-d", domain, "-silent"], "subfinder")


def collect_urls(domain: str) -> ToolResult:
    return run_lines(["gau", "--subs", domain], "gau")


def probe_hosts(hosts: list[str]) -> ToolResult:
    """Probe discovered hosts with ProjectDiscovery httpx for basic metadata."""
    if not hosts:
        return ToolResult("httpx", tool_exists("httpx"), [])
    command = ["httpx", "-silent", "-status-code", "-title", "-tech-detect"]
    if not tool_exists("httpx"):
        return ToolResult("httpx", False, [], "httpx not found in PATH")
    try:
        completed = subprocess.run(
            command,
            input="\n".join(hosts) + "\n",
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if completed.returncode != 0:
            message = (completed.stderr or completed.stdout).strip()
            return ToolResult("httpx", True, [], message or "httpx returned a non-zero exit code")
        lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        return ToolResult("httpx", True, lines)
    except subprocess.TimeoutExpired:
        return ToolResult("httpx", True, [], "Timed out after 180 seconds")
    except OSError as exc:
        return ToolResult("httpx", True, [], str(exc))
