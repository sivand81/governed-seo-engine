"""Minimal source-linked Product JSON-LD and exact-diff validation."""
from .governance import source_check, digest, PolicyError

def product_jsonld(source:dict) -> dict:
    s=source_check(source)
    result={'@context':'https://schema.org','@type':'Product', 'sku':s['sku'],'name':s['name']}
    if s.get('brand'): result['brand']={'@type':'Brand','name':s['brand']}
    if s.get('color'): result['color']=s['color']
    if s.get('model'): result['model']=s['model']
    if s.get('manufacturer'): result['manufacturer']={'@type':'Organization','name':s['manufacturer']}
    return result

def schema_diff(source:dict, existing:dict|None=None) -> dict:
    target=product_jsonld(source)
    if existing is not None and not isinstance(existing,dict):
        raise PolicyError('Existing schema must be a JSON object')
    old=existing or {}
    changed={k:{'before':old.get(k),'after':v} for k,v in target.items() if old.get(k)!=v}
    removed=sorted(set(old)-set(target))
    return {'source_sha256':digest(source_check(source)), 'proposed':target,
            'changes':changed, 'existing_only_fields':removed,
            'warning':'Review existing-only fields; no automatic deletion or deployment'}

def validate_product_schema(source:dict, candidate:dict) -> dict:
    try: expected=product_jsonld(source)
    except (PolicyError,TypeError) as e: return {'approved':False,'errors':[str(e)]}
    if candidate!=expected:
        return {'approved':False,'errors':['schema_differs_from_source_derived_contract']}
    return {'approved':True,'errors':[]}