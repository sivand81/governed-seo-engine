"""Offline SEO auditing and source-grounded product metadata proposals."""
from __future__ import annotations
from html.parser import HTMLParser
import hashlib
import json

ALLOWED_FIELDS = {"seo_title", "meta_description"}
SOURCE_FIELDS = {"sku", "brand", "name", "color", "type", "manufacturer", "model"}
MAX_LENGTHS = {"seo_title": 65, "meta_description": 160}

class GovernanceError(ValueError):
    pass

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.description = None
        self.canonical = None
        self.h1_count = 0
        self.images_without_alt = 0
        self.json_ld = []
        self._script = False
        self._script_text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "img" and not (a.get("alt") or "").strip():
            self.images_without_alt += 1
        elif tag == "meta" and (a.get("name") or "").lower() == "description":
            self.description = a.get("content", "")
        elif tag == "link" and "canonical" in (a.get("rel") or "").lower().split():
            self.canonical = a.get("href", "")
        elif tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._script = True
            self._script_text = []

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self._script:
            self._script_text.append(data)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self._script:
            self._script = False
            raw = "".join(self._script_text).strip()
            try:
                self.json_ld.append({"valid_json": True, "value": json.loads(raw)})
            except json.JSONDecodeError:
                self.json_ld.append({"valid_json": False})

def audit_html(html: str) -> dict:
    p = PageParser()
    p.feed(html)
    issues = []
    if not p.title.strip(): issues.append("missing_title")
    if not (p.description or "").strip(): issues.append("missing_meta_description")
    if not p.canonical: issues.append("missing_canonical")
    if p.h1_count != 1: issues.append("h1_count_not_one")
    if p.images_without_alt: issues.append("images_missing_alt")
    if any(not s["valid_json"] for s in p.json_ld): issues.append("invalid_json_ld")
    return {"title": p.title.strip(), "description": p.description,
            "canonical": p.canonical, "h1_count": p.h1_count,
            "images_without_alt": p.images_without_alt,
            "json_ld_blocks": len(p.json_ld), "issues": issues}

def normalize_source(source: dict) -> dict:
    if not isinstance(source, dict):
        raise GovernanceError("Source must be an object")
    if not all(isinstance(k, str) and isinstance(v, str) for k, v in source.items()):
        raise GovernanceError("Source keys and values must be strings")
    if not source.get("sku", "").strip() or not source.get("name", "").strip():
        raise GovernanceError("Source requires sku and name")
    return {k: v.strip() for k, v in source.items() if k in SOURCE_FIELDS}

def propose(source: dict) -> dict:
    src = normalize_source(source)
    title = src["name"][:MAX_LENGTHS["seo_title"]].rstrip()
    detail = [src[k] for k in ("brand", "color", "type") if src.get(k) and src[k].casefold() not in src["name"].casefold()]
    description = f"{src['name']}. " + (f"Details: {', '.join(detail)}." if detail else "View product details.")
    return {"sku": src["sku"], "changes": {
        "seo_title": {"value": title, "evidence": ["name"]},
        "meta_description": {"value": description[:160].rstrip(), "evidence": ["name"] + [k for k in ("brand","color","type") if k in src]}
    }}

def validate(source: dict, proposal: dict) -> dict:
    src = normalize_source(source)
    errors = []
    if proposal.get("sku") != src["sku"]: errors.append("sku_mismatch")
    changes = proposal.get("changes")
    if not isinstance(changes, dict): return {"approved": False, "errors": ["invalid_changes"]}
    if set(changes) != ALLOWED_FIELDS: errors.append("unexpected_or_missing_fields")
    expected = propose(src)["changes"]
    for field, change in changes.items():
        if field not in ALLOWED_FIELDS:
            continue
        if not isinstance(change, dict) or not isinstance(change.get("value"), str) or not isinstance(change.get("evidence"), list):
            errors.append(f"{field}:invalid_format")
            continue
        if len(change["value"]) > MAX_LENGTHS[field]: errors.append(f"{field}:too_long")
        if change != expected[field]: errors.append(f"{field}:not_source_derived")
    return {"approved": not errors, "errors": errors}

def create_run(source: dict, proposal: dict) -> dict:
    src = normalize_source(source)
    result = validate(src, proposal)
    digest = hashlib.sha256(json.dumps(src, sort_keys=True).encode()).hexdigest()
    return {"version": "0.1.0", "source_sha256": digest,
            "sku": src["sku"], "proposal": proposal, "validation": result,
            "deployment": "NOT_PERFORMED", "requires_human_approval": True}

def approve_run(run: dict, expected_sha256: str) -> dict:
    """Approval record only. Does NOT deploy or alter a website."""
    if not run.get("validation", {}).get("approved"):
        raise GovernanceError("Cannot approve a rejected proposal")
    if run.get("source_sha256") != expected_sha256:
        raise GovernanceError("Source digest mismatch")
    approved = dict(run)
    approved["human_approved"] = True
    approved["deployment"] = "NOT_PERFORMED"
    return approved