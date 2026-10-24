# Contributing

Contributions are welcome. Please open an issue describing a bug, reproducible case, or proposed enhancement before substantial changes.

## Development
Requires Python 3.10+ and no paid API.
Run from the repository root:

```bash
python -m unittest discover -s tests -v
python -m examples.demo
python -m governed_seo.cli audit examples/page.html
python -m governed_seo.cli propose examples/product.json
```

Include tests for behavior changes. Security-sensitive changes require adversarial negative tests. Do not include client records, secrets, or proprietary third-party catalog software. All contributions are subject to the MIT license.

## Design principles
Evidence first; no invented claims; deterministic validation independent of optional generation; explicit human approval; no implicit deployment; local/offline by default.