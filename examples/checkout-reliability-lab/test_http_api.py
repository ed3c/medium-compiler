import concurrent.futures
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib import request,error
from checkout_lab import Lab
from http_api import Handler

class HttpAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        handler=type("BoundHandler",(Handler,),{"lab":Lab(Path(self.tmp.name))})
        self.server=ThreadingHTTPServer(("127.0.0.1",0),handler)
        thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.base=f"http://127.0.0.1:{self.server.server_port}"

    def post(self,key,amount):
        req=request.Request(self.base+"/orders",
            data=json.dumps({"amount_cents":amount}).encode(),
            headers={"Idempotency-Key":key,"Content-Type":"application/json"},
            method="POST")
        with request.urlopen(req,timeout=10) as response:
            return response.status,json.load(response)

    def test_http_burst_duplicate_and_conflict(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            results=list(pool.map(lambda _:self.post("browser-ran-out-of-time",1299),range(36)))
        self.assertEqual({code for code,_ in results},{202})
        self.assertEqual(len({x["order_id"] for _,x in results}),1)
        with self.assertRaises(error.HTTPError) as result:
            self.post("browser-ran-out-of-time",1399)
        self.assertEqual(result.exception.code,409)
        with request.urlopen(self.base+"/counts") as response:
            counts=json.load(response)
        self.assertEqual(counts,dict(orders=1,paid=0,provider_charges=0,pending_events=1))

if __name__=="__main__":
    unittest.main()
