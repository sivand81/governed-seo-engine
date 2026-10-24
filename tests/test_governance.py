import copy
import unittest
from governed_seo.governance import (source_check, expected_changes, validate_change_set,
    manifest, authorize, digest, PolicyError)
from governed_seo.product_schema import product_jsonld, validate_product_schema, schema_diff

S={'sku':'S-1','name':'Sample Toner','brand':'Acme','color':'Black','type':'Toner','model':'M-1'}

def proposal(s=S):return {'sku':s['sku'],'changes':expected_changes(s)}

class GovernanceTests(unittest.TestCase):
    def test_valid(self):self.assertTrue(validate_change_set(S,proposal())['approved'])
    def test_missing_source(self):
        with self.assertRaises(PolicyError):source_check({'name':'a'})
    def test_unknown_source(self):
        with self.assertRaises(PolicyError):source_check(dict(S,price='1'))
    def test_source_wrong_type(self):
        with self.assertRaises(PolicyError):source_check(dict(S,color=1))
    def test_source_controls(self):
        with self.assertRaises(PolicyError):source_check(dict(S,name='bad\nline'))
    def test_long_source(self):
        with self.assertRaises(PolicyError):source_check(dict(S,name='x'*513))
    def test_missing_field(self):
        p=proposal();del p['changes']['seo_title'];self.assertFalse(validate_change_set(S,p)['approved'])
    def test_extra_field(self):
        p=proposal();p['changes']['price']='0';self.assertFalse(validate_change_set(S,p)['approved'])
    def test_extra_top_level(self):
        p=proposal();p['admin']=True;self.assertFalse(validate_change_set(S,p)['approved'])
    def test_false_claim(self):
        p=proposal();p['changes']['seo_title']['value']='Guaranteed delivery';self.assertFalse(validate_change_set(S,p)['approved'])
    def test_fake_evidence(self):
        p=proposal();p['changes']['seo_title']['evidence']=['sku'];self.assertFalse(validate_change_set(S,p)['approved'])
    def test_bad_sku(self):
        p=proposal();p['sku']='wrong';self.assertFalse(validate_change_set(S,p)['approved'])
    def test_non_dict(self):self.assertFalse(validate_change_set(S,[] )['approved'])
    def test_manifest(self):self.assertEqual(manifest(S,proposal())['deployment'],'NOT_PERFORMED')
    def test_approval(self):
        p=proposal();m=manifest(S,p);self.assertEqual(authorize(S,p,m,'reviewer1')['reviewer'],'reviewer1')
    def test_changed_proposal(self):
        p=proposal();m=manifest(S,p);p['changes']['seo_title']['value']='Tampered'
        with self.assertRaises(PolicyError):authorize(S,p,m,'reviewer1')
    def test_changed_source(self):
        p=proposal();m=manifest(S,p)
        with self.assertRaises(PolicyError):authorize(dict(S,color='Red'),p,m,'reviewer1')
    def test_changed_manifest(self):
        p=proposal();m=manifest(S,p);m['validation']['approved']=False
        with self.assertRaises(PolicyError):authorize(S,p,m,'reviewer1')
    def test_bad_reviewer(self):
        with self.assertRaises(PolicyError):authorize(S,proposal(),manifest(S,proposal()),'')
    def test_rejected_approval(self):
        p=proposal();p['changes']['seo_title']['value']='bad'
        with self.assertRaises(PolicyError):authorize(S,p,manifest(S,p),'reviewer1')
    def test_schema(self):self.assertTrue(validate_product_schema(S,product_jsonld(S))['approved'])
    def test_schema_fake_rating(self):
        x=product_jsonld(S);x['aggregateRating']={'ratingValue':5}
        self.assertFalse(validate_product_schema(S,x)['approved'])
    def test_schema_diff(self):
        d=schema_diff(S,{'@type':'Product','offers':{'price':'1'}})
        self.assertIn('offers',d['existing_only_fields'])
    def test_schema_bad_existing(self):
        with self.assertRaises(PolicyError):schema_diff(S,[])
    def test_deterministic_digest(self):self.assertEqual(digest({'a':1,'b':2}),digest({'b':2,'a':1}))

if __name__=='__main__':unittest.main()