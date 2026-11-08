# Security Policy

The **YT-downloader** open source project takes security and user privacy seriously. We welcome responsible disclosure of vulnerabilities.

---

## 🔒 Supported Versions

Only the latest release receives active security patches and updates.

| Version | Supported | Notes |
| :--- | :--- | :--- |
| **v1.0.x** | ✅ Yes | Current stable release |
| < v1.0.0 | ❌ No | Deprecated / pre-release builds |

---

## 🛡️ Reporting a Vulnerability

If you discover a potential security vulnerability in **YT-downloader**, please **DO NOT report it via public GitHub Issues**. Instead, follow one of these confidential reporting methods:

1. **GitHub Private Vulnerability Reporting (Recommended)**:
   - Navigate to the **[Security Advisories](https://github.com/anujkantx/yt-downloader/security/advisories)** tab of this repository.
   - Click **"Report a vulnerability"** to submit a private draft report.
   - Only repository maintainers can view your submission.

2. **Direct Contact**:
   - Contact the maintainer directly via GitHub profile: [@anujkantx](https://github.com/anujkantx).

---

## 📋 What to Include in Your Report

To help us triage and resolve the issue quickly, please provide:
* A detailed description of the vulnerability and its potential impact.
* Clear step-by-step reproduction instructions or a minimal Proof of Concept (PoC).
* Operating system and Python version tested.
* Any proposed fixes or mitigations (if available).

---

## ⏱️ Response Protocol

* **Acknowledgment**: We aim to acknowledge receipt of vulnerability reports within **48 hours**.
* **Triage & Patching**: Confirmed security issues will be patched in a priority fix branch and tested across our automated CI suite.
* **Coordinated Disclosure**: Once a security patch is published in a new GitHub release, public credit and release notes will be shared in accordance with responsible disclosure practices.

---

## 🔐 Code Governance & Merge Restrictions

To protect the integrity of the project:
* **No Direct Pushes to `main`**: All code modifications require a Pull Request.
* **Mandatory Review**: Every PR must be reviewed and approved by the maintainer ([@anujkantx](https://github.com/anujkantx)) as defined in `.github/CODEOWNERS`.
* **Automated CI Validation**: All automated tests (`pytest`) and code linters (`ruff`) must pass 100% before any code can be merged into production.
