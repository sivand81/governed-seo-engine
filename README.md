# Governed SEO Engine

**Open-source, offline-first SEO governance prototype** by [Consult & Code](https://consultncode.com). MIT licensed.

SEO generation can introduce fabricated product claims. Governed SEO Engine demonstrates a source-grounded workflow: produce metadata from supplied product records, independently validate the exact output against allowed evidence, record SHA-256 fingerprints and human approval, and **never deploy implicitly**.

## What works today

- Offline HTML audit: title, meta description, canonical URL, H1 count, missing image alt text, JSON-LD syntax.
- Deterministic title and description proposals derived from local product data.
- Independent policy validator for bounded source fields, evidence attribution and unauthorized-claim rejection.
- Product JSON-LD generation, exact validation and diff review.
- Content digests, approval records tied to the source and proposal, and negative tests.
- Python standard library implementation; no network access or paid API required.

**Limitations:** This is an early prototype. Source inputs are not externally verified; hashes are not signatures; reviewer IDs are not authenticated. No crawler, autonomous AI, hosted service, CMS publishing, or rollback is included. The older CLI approval path is a demonstration and does not provide the stronger binding offered by `governed_seo.governance.authorize`.

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/sivand81/governed-seo-engine.git
cd governed-seo-engine
python -m unittest discover -s tests -v
python -m examples.demo
python -m governed_seo.cli audit examples/page.html
python -m governed_seo.cli propose examples/product.json
```

The demonstration prints the approved source-bound proposal, Product JSON-LD and a diff, then verifies that a tampered claim is rejected. **Nothing is published to a website.**

## Programmatic example

```python
from governed_seo.governance import expected_changes, manifest, authorize
from governed_seo.product_schema import product_jsonld

source = {"sku": "EX-1", "name": "Sample Black Toner", "brand": "ExampleCo"}
proposal = {"sku": source["sku"], "changes": expected_changes(source)}
checked = manifest(source, proposal)
assert checked["validation"]["approved"]
approval = authorize(source, proposal, checked, reviewer="maintainer")
print(product_jsonld(source))
print(approval["deployment"])  # NOT_PERFORMED
```

## Documentation

- [Architecture and trust boundaries](ARCHITECTURE.md)
- [Security policy and limitations](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Future roadmap through v2.0](ROADMAP.md)

## Contribute

Issues and pull requests are welcome, particularly reproducible SEO audit cases, policy tests, and safe design reviews. Do not post client data, credentials or proprietary enrichment technology.

## License

[MIT](LICENSE). Copyright © 2026 Consult & Code.