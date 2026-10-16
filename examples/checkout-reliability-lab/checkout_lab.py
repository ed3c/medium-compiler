"""Local, deterministic payment-failure lab; NO real payment operations."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import json
import sqlite3
import uuid
from pathlib import Path

@contextmanager
def connect(path: Path):
    db = sqlite3.connect(path, timeout=10, isolation_level=None)
    try:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA journal_mode=WAL")
        with db:
            yield db
    finally:
        db.close()

class Conflict(ValueError):
    pass

class LostReply(TimeoutError):
    pass

class Lab:
    def __init__(self, root: Path):
        self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)
        self.shop=self.root/"shop.sqlite3"
        self.provider=self.root/"provider.sqlite3"
        self.initialize()

    def initialize(self):
        with connect(self.shop) as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS orders (
              order_id TEXT PRIMARY KEY,
              request_key TEXT NOT NULL UNIQUE,
              amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
              currency TEXT NOT NULL CHECK (currency = 'USD'),
              status TEXT NOT NULL CHECK (status IN ('PENDING', 'PAID'))
            );
            CREATE TABLE IF NOT EXISTS outbox (
              event_id TEXT PRIMARY KEY,
              order_id TEXT NOT NULL UNIQUE REFERENCES orders(order_id),
              delivered INTEGER NOT NULL DEFAULT 0 CHECK(delivered IN (0,1))
            );
            """)
        with connect(self.provider) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS charges (
                 request_key TEXT PRIMARY KEY,
                 amount_cents INTEGER NOT NULL,
                 currency TEXT NOT NULL,
                 provider_charge_id TEXT NOT NULL UNIQUE
            )""")

    def create(self, request_key: str, amount_cents: int, currency: str = "USD") -> dict:
        if not request_key or len(request_key)>200 or type(amount_cents) is not int or amount_cents<=0 or currency!="USD":
            raise ValueError("A stable key, positive integer cents and USD are required")
        with connect(self.shop) as db:
            db.execute("BEGIN IMMEDIATE")
            old=db.execute("SELECT * FROM orders WHERE request_key=?",(request_key,)).fetchone()
            if old:
                if old["amount_cents"]!=amount_cents or old["currency"]!=currency:
                    raise Conflict("same key with different payment content")
                return dict(old)
            order_id=str(uuid.uuid4())
            db.execute("INSERT INTO orders VALUES(?,?,?,?,?)",(order_id,request_key,amount_cents,currency,"PENDING"))
            db.execute("INSERT INTO outbox(event_id,order_id) VALUES(?,?)",(str(uuid.uuid4()),order_id))
            return dict(db.execute("SELECT * FROM orders WHERE order_id=?",(order_id,)).fetchone())

    def provider_charge(self, request_key: str, amount_cents: int, currency: str, lose_reply: bool=False) -> dict:
        """Commit to a separate mock store before possibly losing the reply."""
        with connect(self.provider) as db:
            db.execute("BEGIN IMMEDIATE")
            old=db.execute("SELECT * FROM charges WHERE request_key=?",(request_key,)).fetchone()
            if old:
                if old["amount_cents"]!=amount_cents or old["currency"]!=currency:
                    raise Conflict("provider key used for a different amount")
                charge=dict(old)
            else:
                charge={"request_key":request_key,"amount_cents":amount_cents,
                        "currency":currency,"provider_charge_id":str(uuid.uuid4())}
                db.execute("INSERT INTO charges VALUES(?,?,?,?)",tuple(charge.values()))
        if lose_reply:
            raise LostReply("provider committed, but the response was lost")
        return charge

    def provider_readback(self, request_key: str) -> dict | None:
        with connect(self.provider) as db:
            row=db.execute("SELECT * FROM charges WHERE request_key=?",(request_key,)).fetchone()
            return dict(row) if row else None

    def process(self, order_id: str, lose_reply: bool=False, crash_after_reply: bool=False) -> dict:
        """Directly simulate an at-least-once event effect; no broker exists in this lab."""
        with connect(self.shop) as db:
            row=db.execute("SELECT * FROM orders WHERE order_id=?",(order_id,)).fetchone()
            if row is None: raise KeyError(order_id)
            order=dict(row)
            if order["status"]=="PAID": return order
        charge=self.provider_readback(order["request_key"])
        if charge is None:
            charge=self.provider_charge(order["request_key"],order["amount_cents"],order["currency"],lose_reply)
        if charge["amount_cents"]!=order["amount_cents"] or charge["currency"]!=order["currency"]:
            raise Conflict("provider readback contradicts order")
        if crash_after_reply:
            raise RuntimeError("worker stopped after provider effect, before local commit")
        with connect(self.shop) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE orders SET status='PAID' WHERE order_id=? AND status='PENDING'",(order_id,))
            db.execute("UPDATE outbox SET delivered=1 WHERE order_id=?",(order_id,))
            return dict(db.execute("SELECT * FROM orders WHERE order_id=?",(order_id,)).fetchone())

    def state(self,order_id: str) -> dict:
        with connect(self.shop) as db:
            row=db.execute("SELECT * FROM orders WHERE order_id=?",(order_id,)).fetchone()
            if row is None: raise KeyError(order_id)
            return dict(row)

    def counts(self) -> dict:
        with connect(self.shop) as db,connect(self.provider) as provider:
            orders=db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            paid=db.execute("SELECT COUNT(*) FROM orders WHERE status='PAID'").fetchone()[0]
            pending_events=db.execute("SELECT COUNT(*) FROM outbox WHERE delivered=0").fetchone()[0]
            charges=provider.execute("SELECT COUNT(*) FROM charges").fetchone()[0]
            keys={r[0] for r in provider.execute("SELECT request_key FROM charges")}
            if any(r[0] not in keys for r in db.execute("SELECT request_key FROM orders WHERE status='PAID'")):
                raise AssertionError("Paid order lacks provider charge")
            return dict(orders=orders,paid=paid,provider_charges=charges,pending_events=pending_events)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--data",type=Path,default=Path(".checkout-lab"))
    sub=parser.add_subparsers(dest="cmd",required=True)
    new=sub.add_parser("create")
    new.add_argument("key")
    new.add_argument("amount_cents",type=int)
    worker=sub.add_parser("process")
    worker.add_argument("order_id")
    worker.add_argument("--lost-reply",action="store_true")
    worker.add_argument("--crash-after-reply",action="store_true")
    state=sub.add_parser("state")
    state.add_argument("order_id")
    sub.add_parser("counts")
    args=parser.parse_args()
    lab=Lab(args.data)
    try:
        if args.cmd=="create": result=lab.create(args.key,args.amount_cents)
        elif args.cmd=="process": result=lab.process(args.order_id,args.lost_reply,args.crash_after_reply)
        elif args.cmd=="state": result=lab.state(args.order_id)
        else: result=lab.counts()
    except (Conflict,LostReply,RuntimeError,ValueError) as exc:
        print(json.dumps({"status":"UNKNOWN_OR_REFUSED","cause":str(exc)}))
        raise SystemExit(2)
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
