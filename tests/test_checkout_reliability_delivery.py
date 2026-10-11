"""Verify the checkout reliability article and its separately executable failure lab."""
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from test_learning_site import site

ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/"examples/checkout-reliability-lab"
SLUG="checkout-reliability-large-traffic"
PARENT="architect-amplifier-payment-decisions"

class CheckoutReliabilityDeliveryTests(unittest.TestCase):
    def test_local_fault_injection_suite(self):
        result=subprocess.run(
            [sys.executable,"-m","unittest","discover","-s",".","-v"],
            cwd=LAB,capture_output=True,text=True,timeout=60,
        )
        self.assertEqual(result.returncode,0,result.stdout+"\n"+result.stderr)
        self.assertIn("Ran 7 tests",result.stderr)
        self.assertIn("OK",result.stderr)

    def test_published_article_and_previous_entry(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"site"
            provenance=site.build(out)
            content=(ROOT/"articles"/f"{SLUG}.md").read_bytes()
            page=(out/"articles"/SLUG/"index.html").read_text()
            previous=(out/"articles"/PARENT/"index.html").read_text()
            index=(out/"articles/index.html").read_text()
            self.assertIn("Checkout Reliability",page)
            self.assertIn("LostReply",page)
            self.assertIn("PostgreSQL",page)
            self.assertIn("RabbitMQ",page)
            self.assertIn("Recovery Point Objective",page)
            self.assertIn("/articles/"+SLUG+"/",index)
            self.assertIn("/articles/"+SLUG+"/",previous)
            self.assertEqual((out/"articles"/SLUG/"article.md").read_bytes(),content)
            record=next(x for x in provenance["articles"] if x["route"]=="/articles/"+SLUG+"/")
            self.assertEqual(record["sha256"],hashlib.sha256(content).hexdigest())
            self.assertFalse((out/"articles"/SLUG/"source.json").exists())

if __name__=="__main__":
    unittest.main()
