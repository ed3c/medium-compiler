# Checkout reliability lab

This is a small, **self-contained simulation** accompanying the second Medium article on payment reliability and cross-functional engineering decisions. It is not a real distributed deployment or production payment client. There are no credentials or actual charges.

**Prerequisites:** Python 3.10+ for the `dict | None` typing syntax; optional [Grafana k6](https://github.com/grafana/k6) for local HTTP load tests. Python's standard library is enough for the deterministically tested scenarios.

## Local failure controls

```sh
cd examples/checkout-reliability-lab
python3 -m unittest discover -v
python3 checkout_lab.py --data .demo create cart-42 1250
# Copy order_id from this response before continuing.
python3 checkout_lab.py --data .demo process ORDER_ID --lost-reply
python3 checkout_lab.py --data .demo counts
python3 checkout_lab.py --data .demo process ORDER_ID
python3 checkout_lab.py --data .demo counts
```

In the lost-reply case, `process` exits 2 intentionally; this is a failed communication attempt after the mock provider has committed its charge. Check `provider_charges==1`, `pending_events==1`, `paid==0`, then retry with the **same** identity and check `provider_charges==1`, `pending_events==0`, `paid==1`.

For the worker-crash boundary, run the same scenario from an isolated `.demo2` directory with `--crash-after-reply`. Data survives simulated worker termination. Reprocessing uses provider readback.

## Optional local API load experiment

```sh
python3 http_api.py --data .load --port 8080
# Another terminal; requires separately installed k6:
k6 run -e RUN_ID=trial-001 load.js
```

`load.js` asks for 20 arrivals/second for 20 seconds and specifies performance thresholds; this is not evidence that throughput or latency meets them. Save actual k6 results, HTTP errors, `http://127.0.0.1:8080/counts`, machine characteristics and git SHA. The HTTP adapter only binds `127.0.0.1`, has no authentication and must never be exposed publicly. The mock provider shares this Python process but commits into a second persistent SQLite database; **there is no network boundary between the service and mock provider**. No RabbitMQ, replication, real payment semantics, card processing, or disaster recovery is verified.

## Architectural boundaries and next experiments

- A local transaction creates `orders` and `outbox` together. `PENDING` represents **unresolved** Checkout knowledge; a lost provider reply is *not* proof of provider failure.
- Mock provider charge identity is enforced with its own `UNIQUE(request_key)` and a verified local readback. This does not guarantee how a real payment provider handles idempotency windows, partial refunds, fees, transaction settlement, chargebacks or provider API outages.
- The Outbox table is a pending-work marker here. There is **no separate publisher or message broker** in this stage. `process` directly exercises an event's business effect and its acknowledgement. Later stages should replace this with durable event publication plus idempotent consumers.
- `sqlite3` WAL and single-host threads are not a proof of horizontal scaling, PostgreSQL locking behavior, queue safety or geo-distributed consistency.
- The current tests cover seven deterministic cases, including one burst of 36 concurrent HTTP duplicate requests. They are not full end-to-end payment acceptance or an automated SLO measurement.
- For realistic implementation work, see MIT-licensed [dotnet/eShop](https://github.com/dotnet/eShop), MIT-licensed [temporalio/samples-python](https://github.com/temporalio/samples-python), [RabbitMQ reliability](https://www.rabbitmq.com/docs/reliability), [PostgreSQL isolation](https://www.postgresql.org/docs/current/transaction-iso.html), and [Grafana k6 threshold docs](https://grafana.com/docs/k6/latest/using-k6/thresholds/). Keep their original licenses and test the concrete version you select.

## Outcomes to retain

Capture raw stdout/stderr/exit status, checked-in source SHA, test case and injected failure, mock provider ledger count, Checkout order state, pending event count, and unresolved behavior. A local green suite means these specific checks passed with this implementation, not production readiness.
