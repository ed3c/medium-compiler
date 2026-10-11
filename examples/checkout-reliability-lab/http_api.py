"""Loopback-only HTTP adapter for repeatable k6 exercises; NOT production."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from checkout_lab import Lab, Conflict

class Handler(BaseHTTPRequestHandler):
    lab: Lab

    def send_json(self,code,data):
        payload=json.dumps(data,sort_keys=True).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        if urlparse(self.path).path!="/orders":
            self.send_json(404,{"error":"not found"})
            return
        key=self.headers.get("Idempotency-Key","")
        try:
            length=int(self.headers.get("Content-Length","0"))
            if length>4096 or length<1:
                raise ValueError("Invalid Content-Length")
            request=json.loads(self.rfile.read(length))
            order=self.lab.create(key,request["amount_cents"],request.get("currency","USD"))
            self.send_json(202,{"order_id":order["order_id"],"status":order["status"]})
        except Conflict as exc:
            self.send_json(409,{"error":str(exc)})
        except (ValueError,KeyError,TypeError) as exc:
            self.send_json(400,{"error":str(exc)})

    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/counts":
            self.send_json(200,self.lab.counts())
            return
        if path.startswith("/orders/"):
            try:
                self.send_json(200,self.lab.state(path.rsplit("/",1)[-1]))
                return
            except KeyError:
                pass
        self.send_json(404,{"error":"not found"})

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--data",type=Path,default=Path(".checkout-lab"))
    parser.add_argument("--port",type=int,default=8080)
    args=parser.parse_args()
    handler=type("BoundHandler",(Handler,),{"lab":Lab(args.data)})
    server=ThreadingHTTPServer(("127.0.0.1",args.port),handler)
    print(f"http://127.0.0.1:{args.port} (loopback only, no auth)",flush=True)
    server.serve_forever()

if __name__=="__main__":
    main()
