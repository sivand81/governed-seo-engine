"""Independent policy validator and tamper-evident approval records.

Not a truth oracle: trusted inputs must be verified upstream.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import re
from typing import Any

FIELDS = frozenset({'seo_title', 'meta_description'})
SOURCE_KEYS = frozenset({'sku', 'name', 'brand', 'color', 'type', 'manufacturer', 'model'})
LIMITS = {'seo_title': 65, 'meta_description': 160}
POLICY_VERSION = '2026-10-v1'

class PolicyError(ValueError):
    pass

def canonical(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')

def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()

def source_check(source: dict) -> dict:
    if not isinstance(source, dict) or set(source) - SOURCE_KEYS:
        raise PolicyError('Unknown source fields or invalid source')
    if not all(isinstance(k, str) and isinstance(v, str) and len(v) <= 512 for k,v in source.items()):
        raise PolicyError('Source must contain bounded string values')
    if not source.get('sku','').strip() or not source.get('name','').strip():
        raise PolicyError('Source requires sku and name')
    if any(any(ord(c)<32 for c in v) for v in source.values()):
        raise PolicyError('Control characters forbidden')
    return {k:v.strip() for k,v in source.items()}

def expected_changes(source: dict) -> dict:
    """Independent contract for permitted text; deliberately deterministic."""
    s=source_check(source)
    name=s['name']
    title=name[:65].rstrip()
    details=[(k,s[k]) for k in ('brand','color','type') if s.get(k) and s[k].casefold() not in name.casefold()]
    desc=name+'. '+('Details: '+', '.join(v for _,v in details)+'.' if details else 'View product details.')
    return {
      'seo_title': {'value':title, 'evidence':['name']},
      'meta_description': {'value':desc[:160].rstrip(), 'evidence':['name']+[k for k,_ in details]}
    }

def validate_change_set(source: dict, proposal: dict) -> dict:
    try: s=source_check(source)
    except (PolicyError, TypeError) as e: return {'approved':False,'errors':[f'invalid_source:{e}']}
    errors=[]
    if not isinstance(proposal,dict): return {'approved':False,'errors':['invalid_proposal']}
    if set(proposal)!={'sku','changes'}: errors.append('unexpected_proposal_fields')
    if proposal.get('sku')!=s['sku']: errors.append('sku_mismatch')
    changes=proposal.get('changes')
    if not isinstance(changes,dict): return {'approved':False,'errors':errors+['invalid_changes']}
    if set(changes)!=FIELDS: errors.append('unexpected_or_missing_fields')
    expected=expected_changes(s)
    for field in FIELDS:
        if field not in changes: continue
        change=changes[field]
        if not isinstance(change,dict) or set(change)!={'value','evidence'}:
            errors.append(f'{field}:invalid_shape'); continue
        if not isinstance(change['value'],str) or not isinstance(change['evidence'],list):
            errors.append(f'{field}:invalid_types'); continue
        if len(change['value'])>LIMITS[field]: errors.append(f'{field}:too_long')
        if change!=expected[field]: errors.append(f'{field}:not_source_derived')
    return {'approved':not errors,'errors':sorted(errors)}

def manifest(source:dict, proposal:dict) -> dict:
    s=source_check(source)
    validation=validate_change_set(s,proposal)
    return {'policy_version':POLICY_VERSION,'source_sha256':digest(s),
            'proposal_sha256':digest(proposal),'validation':validation,
            'deployment':'NOT_PERFORMED','requires_human_approval':True}

def authorize(source:dict, proposal:dict, saved_manifest:dict, reviewer:str) -> dict:
    if not isinstance(reviewer,str) or not re.fullmatch(r'[A-Za-z0-9_.@-]{2,100}',reviewer):
        raise PolicyError('Reviewer identifier required')
    actual=manifest(source,proposal)
    if not hmac.compare_digest(digest(saved_manifest),digest(actual)):
        raise PolicyError('Manifest or inputs have changed')
    if not actual['validation']['approved']:
        raise PolicyError('Rejected changes cannot be authorized')
    approval={'manifest_sha256':digest(actual),'reviewer':reviewer,
              'source_sha256':actual['source_sha256'],
              'proposal_sha256':actual['proposal_sha256'],
              'policy_version':POLICY_VERSION,'deployment':'NOT_PERFORMED'}
    approval['record_sha256']=digest(approval)
    return approval