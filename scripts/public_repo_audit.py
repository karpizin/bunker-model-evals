#!/usr/bin/env python3
"""Fail when public-repository invariants are violated."""

from __future__ import annotations

import argparse
import ipaddress
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


MAX_TRACKED_BYTES = 10 * 1024 * 1024
FORBIDDEN_SUFFIXES = {
    ".db",
    ".env",
    ".gguf",
    ".key",
    ".log",
    ".onnx",
    ".pem",
    ".safetensors",
    ".sqlite",
    ".zim",
}
FORBIDDEN_BASENAMES = {"id_dsa", "id_ecdsa", "id_ed25519", "id_rsa"}
TEXT_SKIP = {Path("scripts/public_repo_audit.py")}


@dataclass(frozen=True)
class Finding:
    path: Path
    rule: str
    detail: str


SECRET_PATTERNS = {
    "private-key": re.compile(
        rb"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"
    ),
    "openai-key": re.compile(rb"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}\b"),
    "openrouter-key": re.compile(rb"\bsk-or-v1-[A-Za-z0-9_-]{20,}\b"),
    "github-token": re.compile(
        rb"\b(?:gh[opusr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"
    ),
    "huggingface-token": re.compile(rb"\bhf_[A-Za-z0-9]{30,}\b"),
    "slack-token": re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "google-api-key": re.compile(rb"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "aws-access-key": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
}

MACHINE_PATH_PATTERNS = {
    "personal-macos-path": re.compile(rb"/Users/[A-Za-z0-9._-]+/"),
    "legacy-benchmark-home": re.compile(rb"/home/bunkerai/"),
}

IPV4_PATTERN = re.compile(
    rb"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])"
)


def repository_files(root: Path) -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
    )
    return [Path(raw.decode("utf-8")) for raw in output.split(b"\0") if raw]


def is_private_address(raw: bytes) -> bool:
    try:
        address = ipaddress.ip_address(raw.decode("ascii"))
    except ValueError:
        return False
    return any(
        address in network
        for network in (
            ipaddress.ip_network("10.0.0.0/8"),
            ipaddress.ip_network("172.16.0.0/12"),
            ipaddress.ip_network("192.168.0.0/16"),
        )
    )


def audit_paths(root: Path, paths: Iterable[Path]) -> list[Finding]:
    findings: list[Finding] = []

    for relative in paths:
        absolute = root / relative
        if not absolute.is_file():
            continue

        suffix = relative.suffix.lower()
        if suffix in FORBIDDEN_SUFFIXES or relative.name in FORBIDDEN_BASENAMES:
            findings.append(Finding(relative, "forbidden-artifact", suffix or relative.name))

        size = absolute.stat().st_size
        if size > MAX_TRACKED_BYTES:
            findings.append(Finding(relative, "oversized-file", f"{size} bytes"))

        if relative in TEXT_SKIP or size > MAX_TRACKED_BYTES:
            continue

        data = absolute.read_bytes()
        if b"\0" in data:
            continue

        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(data):
                findings.append(Finding(relative, name, "high-confidence credential signature"))

        for name, pattern in MACHINE_PATH_PATTERNS.items():
            if pattern.search(data):
                findings.append(Finding(relative, name, "machine-specific absolute path"))

        private_addresses = sorted(
            {
                match.group().decode("ascii")
                for match in IPV4_PATTERN.finditer(data)
                if is_private_address(match.group())
            }
        )
        if private_addresses:
            findings.append(
                Finding(relative, "private-network-address", ", ".join(private_addresses))
            )

    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: inferred from this script)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    findings = audit_paths(root, repository_files(root))
    if not findings:
        print("public repository audit: PASS")
        return 0

    print(f"public repository audit: FAIL ({len(findings)} finding(s))")
    for finding in findings:
        print(f"- {finding.path}: {finding.rule}: {finding.detail}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
