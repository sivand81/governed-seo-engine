# Security Policy

## Scope and trust boundaries
This is an offline-first prototype, not a hosted service or production publishing agent. Inputs are local files. Source records are *asserted* evidence and must be verified by the operator; the tool cannot independently confirm their truth.

The independent validator rejects unapproved fields and changes that do not match its source-derived contract. Source and proposal digests detect accidental or unauthorized changes when checked against trusted prior values. They are **not digital signatures**, identity verification, or protection against an attacker who can rewrite all local files.

Human approval records do not deploy changes. Do not supply production credentials or client data to examples, tests, public issues, or pull requests.

## Reporting
For vulnerabilities, avoid posting exploitable details publicly. Contact the repository maintainer privately through GitHub's private vulnerability reporting if enabled, or request a private channel in a minimal issue.

## Limitations
No network crawler, sandboxed AI runtime, authenticated approval system, production CMS publishing, or rollback is implemented in this release.