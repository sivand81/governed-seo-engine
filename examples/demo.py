"""Offline reproducible demonstration: python -m examples.demo (from repository root)."""
import json
from pathlib import Path
from governed_seo.governance import expected_changes, manifest, authorize, validate_change_set
from governed_seo.product_schema import product_jsonld, validate_product_schema, schema_diff

source=json.loads((Path(__file__).parent/'product.json').read_text(encoding='utf-8'))
proposal={'sku':source['sku'],'changes':expected_changes(source)}
record=manifest(source,proposal)
assert record['validation']['approved']
assert validate_product_schema(source,product_jsonld(source))['approved']
print(json.dumps({'manifest':record,'approval':authorize(source,proposal,record,'demo-reviewer'),
                  'product_schema':product_jsonld(source),
                  'schema_diff':schema_diff(source)},indent=2))
proposal['changes']['seo_title']['value']='Guaranteed lowest price'
assert not validate_change_set(source,proposal)['approved']
print('Tampered claim correctly rejected. No deployment performed.')