# Architecture

```text
Untrusted local product JSON ──> strict source_check ──> canonical source digest
                                        │
                                        ▼
                              deterministic proposal
                                        │
                                        ▼
                        independent expected_changes validator
                                        │
                          ┌─────────────┴─────────────┐
                        reject                      validate
                                                       │
                                         exact proposal + source hashes
                                                       │
                                             reviewer approval record
                                                       │
                                           NO DEPLOYMENT PERFORMED
```

The HTML auditor parses local HTML for title, description, canonical, H1 count, missing image alt text, and JSON-LD syntax. The product-schema module produces an exact, minimal Product JSON-LD subset from approved source fields. No crawler or CMS integration exists yet.

## Trust boundaries
- The operator is responsible for the accuracy of source records.
- A SHA-256 digest is a content fingerprint, **not a cryptographic signature**.
- Reviewer IDs are labels, not authenticated identities.
- Never give an AI generator publishing credentials.
- Publishing adapters and optional AI belong to later releases and must be isolated behind independent validation and explicit approvals.