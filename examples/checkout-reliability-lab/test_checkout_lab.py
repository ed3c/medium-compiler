import concurrent.futures
import tempfile
import unittest
from pathlib import Path
from checkout_lab import Lab, Conflict, LostReply

class FailureTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.lab=Lab(Path(self.tmp.name))

    def test_duplicate_requests_return_one_order_and_outbox_event(self):
        def create(_):
            return self.lab.create("one-cart-42",1250)["order_id"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            ids=list(pool.map(create,range(60)))
        self.assertEqual(len(set(ids)),1)
        self.assertEqual(self.lab.counts(),dict(orders=1,paid=0,provider_charges=0,pending_events=1))

    def test_same_key_different_amount_is_refused(self):
        self.lab.create("cart-42",1250)
        with self.assertRaises(Conflict):
            self.lab.create("cart-42",2500)
        self.assertEqual(self.lab.counts()["orders"],1)

    def test_lost_reply_does_not_repeat_external_charge(self):
        order=self.lab.create("cart-lost",1250)
        with self.assertRaises(LostReply):
            self.lab.process(order["order_id"],lose_reply=True)
        self.assertEqual(self.lab.state(order["order_id"])["status"],"PENDING")
        self.assertEqual(self.lab.counts()["provider_charges"],1)
        self.lab.process(order["order_id"])
        self.lab.process(order["order_id"])
        self.assertEqual(self.lab.counts(),dict(orders=1,paid=1,provider_charges=1,pending_events=0))

    def test_worker_crash_between_effect_and_local_commit(self):
        order=self.lab.create("cart-worker-crash",325)
        with self.assertRaises(RuntimeError):
            self.lab.process(order["order_id"],crash_after_reply=True)
        self.assertEqual(self.lab.counts()["pending_events"],1)
        self.lab.process(order["order_id"])
        self.assertEqual(self.lab.counts()["provider_charges"],1)
        self.assertEqual(self.lab.state(order["order_id"])["status"],"PAID")

    def test_two_worker_attempts_share_one_provider_charge(self):
        order=self.lab.create("cart-double-worker",499)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            statuses=[x["status"] for x in pool.map(self.lab.process,[order["order_id"]]*2)]
        self.assertEqual(statuses,["PAID","PAID"])
        self.assertEqual(self.lab.counts()["provider_charges"],1)

    def test_invariants_are_scoped_not_proof_of_real_provider(self):
        order=self.lab.create("a",100)
        self.lab.process(order["order_id"])
        self.assertEqual(self.lab.counts()["paid"],1)
        self.assertEqual(self.lab.counts()["provider_charges"],1)

if __name__=="__main__":
    unittest.main()
