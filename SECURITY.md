# Security policy

## Reporting a vulnerability

Please use **GitHub Private Vulnerability Reporting** for this repository. Do not open a public issue for suspected vulnerabilities, exposed credentials, private infrastructure details, or unsafe benchmark fixtures.

Include the affected file or revision, impact, reproduction steps, and any proposed mitigation. Avoid attaching real customer data or active secrets; use a minimal redacted proof.

## Supported version

Security fixes are applied to the current default branch. Historical benchmark artifacts are retained for reproducibility but are not maintained as executable release branches.

## Data and credential handling

This repository is public-data only. Model weights, API keys, access tokens, private corpora, customer data, raw product logs, and internal network addresses must not be committed. Use environment variables and external artifact storage for runtime inputs.
