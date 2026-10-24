import unittest
from governed_seo.core import audit_html, propose, validate, create_run, approve_run, GovernanceError

SOURCE = {"sku": "EX-001", "name": "Example Black Cartridge", "brand": "ExampleCo",
          "color": "Black", "type": "Ink Cartridge"}

class EngineTests(unittest.TestCase):
    def test_clean_audit(self):
        html = '<html><head><title>Page</title><meta name="description" content="Details"><link rel="canonical" href="https://example.org/p"></head><body><h1>Page</h1><img alt="Item" src="a"></body></html>'
        self.assertEqual(audit_html(html)["issues"], [])

    def test_bad_audit(self):
        self.assertIn("missing_title", audit_html("<h1>A</h1><h1>B</h1><img src='x'>")["issues"])

    def test_invalid_json_ld(self):
        self.assertIn("invalid_json_ld", audit_html('<script type="application/ld+json">{broken}</script>')["issues"])

    def test_approved_template(self):
        self.assertTrue(validate(SOURCE, propose(SOURCE))["approved"])

    def test_reject_invented_claim(self):
        p = propose(SOURCE)
        p["changes"]["meta_description"]["value"] = "Guaranteed lowest price and overnight shipping"
        self.assertFalse(validate(SOURCE, p)["approved"])

    def test_reject_unauthorized_field(self):
        p = propose(SOURCE)
        p["changes"]["price"] = {"value": "1", "evidence": []}
        self.assertFalse(validate(SOURCE, p)["approved"])

    def test_reject_changed_sku(self):
        p = propose(SOURCE)
        p["sku"] = "EX-999"
        self.assertFalse(validate(SOURCE, p)["approved"])

    def test_approval_requires_matching_digest(self):
        run = create_run(SOURCE, propose(SOURCE))
        with self.assertRaises(GovernanceError):
            approve_run(run, "incorrect")
        self.assertTrue(approve_run(run, run["source_sha256"])["human_approved"])

    def test_no_deployment(self):
        run = create_run(SOURCE, propose(SOURCE))
        self.assertEqual(run["deployment"], "NOT_PERFORMED")

if __name__ == "__main__":
    unittest.main()