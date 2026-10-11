# The Sale That Exposed a Missing Payment State: Learning Distributed-System Reliability by Breaking a Checkout

[The previous article](https://medium-compiler.vercel.app/articles/architect-amplifier-payment-decisions/) ended with a checkout team choosing to examine its payment state before arguing about Microservices. Now suppose that team has another problem. A promotion is six weeks away. Product wants faster releases, Operations wants fewer failed checkouts, and Finance wants to know why some customers report a charge without a completed order.

The engineer in the room can implement an API quickly. That is not the difficult part. The difficult part is defining what must remain true when the customer refreshes the page, the worker restarts, the network loses a reply, or a campaign sends far more requests than yesterday.

The team agrees to build a small failure laboratory before changing the production architecture. It will use open-source Python code, preserve a separate mock provider ledger, and make the tests executable without credentials or real funds. The local lab can establish specific state-machine properties. It cannot certify a production payment integration or demonstrate that a distributed cluster will handle a particular number of requests per second.

## The business risk comes before the system diagram

The product manager asks whether the team can deploy a new checkout service by Friday. Finance asks a different question: if a payment succeeds but the order remains pending, how many support cases and manual reconciliations will follow? An engineer proposes adding more workers. That may reduce queue delay, but it cannot repair an incorrect retry protocol.

The team writes a decision in ordinary language: a customer's single intended purchase must not turn into two provider charges because of an application retry. A charged purchase must have a recoverable order identity. The system must not claim that money moved merely because a request was sent.

Those commitments require **measurable invariants**, not a preferred framework:

- Identity: one logical payment has one stable `Idempotency-Key` within the provider's defined scope and retention window. Reusing that key with a different amount must be rejected.
- No invented success: a network `Timeout` is `UNKNOWN`, not `FAILED` or `PAID`. Only authoritative provider evidence can settle the external effect.
- No lost intent: the Order and its `Outbox` event are stored in one local database transaction. A crash after that commit must not erase the pending work.
- Safe redelivery: repeating an event or restarting a worker must not create a second logical charge. The provider's idempotency contract or trusted readback is part of this claim.
- Recovery: incomplete work must remain discoverable, and an operator must be able to reconcile it without guessing which effects happened.

There are two different meanings of "exactly once" here. A database `UNIQUE` constraint can make the local intake create one Order for the same request key. It cannot force an unrelated payment provider to perform only one external effect. The provider needs a compatible identity contract; a worker needs a way to check what happened after an ambiguous reply. If neither exists, promising an exactly-once charge would be false.

## The crash between two commits

At the start of a purchase, Checkout commits the Order and a pending Outbox event together. A worker later sends a charge request. The payment provider has its own transaction. These are not one ACID transaction: the two databases cannot simply roll back together.

```text
Customer → Checkout DB [Order + Outbox]  COMMIT A
                            │
                            ▼
                        Worker
                            │  stable Idempotency-Key
                            ▼
                Mock Provider Ledger       COMMIT B
                            │
                    reply or lost reply
                            ▼
            Checkout reads provider evidence
                            │
                     PAID / PENDING
```

A worker may die after `COMMIT B` but before recording the result in Checkout. The Order still says `PENDING`; the provider has already written the charge. Treating that state as a failed payment and generating a new key can charge the customer again.

**Transactional Outbox** solves a narrower problem. It ensures that the local Order and the intention to publish work do not split during `COMMIT A`. It does not atomically bind the later provider effect to that commit. An Outbox relay can publish the same event twice if it loses its acknowledgement. The consumer must tolerate redelivery. RabbitMQ likewise documents redelivery on consumer failures and possible duplicates following publisher recovery.

A reliable worker first looks for the provider's prior result using the stable logical key. If there is no authoritative result, it submits a charge using the same key. If the reply is lost, it preserves uncertainty and checks again. It marks the Order `PAID` only after the provider's recorded charge matches the amount and currency. Unknown is a useful state: it prevents an irreversible guess.

## Run the smallest test before adding infrastructure

The companion code lives in the [open-source checkout failure lab](https://github.com/ed3c/medium-compiler/tree/main/examples/checkout-reliability-lab). It uses only Python's standard library. Two SQLite files simulate the Checkout and Provider stores. `checkout_lab.py` implements the Order, Outbox, mock charge, readback, and bounded state transition. `test_checkout_lab.py` injects lost replies, duplicate requests and worker crashes. Neither store contains card details; the provider is deliberately fake.

```bash
git clone https://github.com/ed3c/medium-compiler.git
cd medium-compiler/examples/checkout-reliability-lab
python3 -m unittest discover -v
```

There is no secret, hosted service or Docker requirement for this first exercise. The test suite covers the following paths, not the entire payments domain.

Duplicate checkout requests. Sixty concurrent attempts use the same business key. The Order table's `UNIQUE` constraint and a transaction serialize intake. The expected result is one Order and one Outbox event. Reusing the key with a different amount raises a conflict instead of returning a misleading success.

Provider commits but the reply vanishes. The mock provider saves its charge, then raises `LostReply`. Checkout must remain `PENDING` while the provider ledger shows one charge. Processing the pending work again reads that charge and marks the Order `PAID`, without inserting a second charge. The negative control is a new key on retry: that would be a different payment operation and must not be used for the same purchase.

Worker dies between effects. A fault after provider commit but before Checkout state commit leaves the Outbox event pending. Redelivery reads the existing provider charge. The local state becomes `PAID` only after the second attempt sees supporting evidence.

Two workers race. Two local worker attempts can process the same Order. Both may observe an unresolved payment; the provider ledger's unique key prevents two mock charges. This proves the lab's chosen constraint, not that every real payment provider implements equivalent behavior.

For a single lost-reply experiment, run:

```bash
python3 checkout_lab.py --data .demo create cart-42 1250
# Copy order_id from the JSON response.
python3 checkout_lab.py --data .demo process ORDER_ID --lost-reply
python3 checkout_lab.py --data .demo counts
python3 checkout_lab.py --data .demo process ORDER_ID
python3 checkout_lab.py --data .demo counts
```

The first `process` exits with a nonzero code after the provider ledger commits. The first count should show one provider charge, one pending event, and no Paid order. The second process reconciles the charge and consumes the pending event. An operator learns more from that state transition than from an endpoint returning `200 OK` in the happy path.

## Then move from correctness to load

The team now asks whether its implementation can survive a burst. It must not confuse two measurements. **Correctness** asks whether a repeated logical operation violates an invariant. **Capacity** asks how throughput, latency and error rate change as demand rises. A green correctness test does not imply a particular capacity.

The local HTTP adapter exposes the create-order endpoint for a burst test:

```bash
python3 http_api.py --data .load --port 8080
# In another terminal, with Grafana k6 installed:
k6 run -e RUN_ID=campaign-a load.js
```

The included k6 workload requests **20 arrivals per second for 20 seconds**. This is a *configured target*, not a measured capacity claim. It checks API status and presence of an Order ID. Its proposed failure thresholds are `http_req_failed < 1%`, `p95 < 500 ms`, and zero dropped iterations. Run the test again with a new `RUN_ID` to avoid confusing a repeated business key with a new checkout. If the threshold fails, save the raw result and explain whether CPU, SQLite writer contention, I/O or the client caused the problem; do not delete the failing threshold just to get green output.

After a clean arrival test, send another burst in which many callers deliberately reuse the **same** key. The system should still create one logical Order. Next, use different keys and measure throughput. The two runs expose different failure surfaces: duplicate suppression versus write capacity. Track actual request rate, p50/p95/p99, failed and dropped iterations, pending Outbox age, duplicate conflicts, and the number of unresolved payments.

The local HTTP adapter has no authentication and binds only to `127.0.0.1`. It is not a payment gateway and should not be deployed publicly. SQLite protects this small test; it is not a substitute for a production database, replication, a real broker, provider rate limits, or distributed failure testing. Our environment ran the Python tests; the Docker-based components and the k6 load run are separate exercises whose results must be collected on your own machine.

## What changes with PostgreSQL, RabbitMQ and multiple replicas?

The next lab replaces the two-file approximation with real service boundaries. PostgreSQL stores Orders and Outbox events in one transaction. An Outbox Relay polls pending rows, for example with `SELECT ... FOR UPDATE SKIP LOCKED`, and publishes to RabbitMQ. Consumers acknowledge only after they have safely handled a message. Every message carries a stable Order ID and Event ID, not a newly generated payment key.

The failure matrix becomes more demanding. Kill the API just after database commit: the Outbox entry must remain. If RabbitMQ stops while orders arrive, pending events should accumulate and later drain after recovery. Crash the relay after publish but before its sent marker: duplicate events must be harmless. Kill a consumer after a successful provider effect: readback must resolve the Order without a second charge. Expire the provider's idempotency window in a controlled test: the application must not assume the key remains protected forever. Restore PostgreSQL from a backup and reconcile state from provider evidence before reopening writes.

This upgrade is not free. PostgreSQL row locks, indexes, isolation levels and pool capacity create contention. RabbitMQ introduces publisher confirms, consumer acknowledgement and queue backpressure. An Outbox Relay requires monitoring, and an expanding queue can hide a broken consumer while the HTTP API keeps returning `202 Accepted`. Adding workers helps only when the bottleneck is parallelizable and the downstream can accept the traffic.

Use mature open-source repositories as **comparative reference implementations**, not as unverified proof of your own system: [Microsoft eShop](https://github.com/dotnet/eShop) (MIT) for a multi-service commerce architecture, [Temporal Python samples](https://github.com/temporalio/samples-python) (MIT) for durable-workflow and retry concepts, [PostgreSQL documentation](https://www.postgresql.org/docs/current/transaction-iso.html) for isolation, [RabbitMQ reliability](https://www.rabbitmq.com/docs/reliability) for delivery semantics, and [Grafana k6](https://grafana.com/docs/k6/latest/using-k6/thresholds/) for load-test criteria. k6's repository is AGPL-3.0; the lab calls the external CLI and does not copy its source. Study and reuse each component under its own license.

The exit criterion for this second lab is not "Docker Compose starts." It is an **independently replayable failure trace** showing the exact inputs, source revision, failure injection, provider-side effect count, recovered Order state, broker backlog and observed load metrics. This article does not claim those multi-service experiments have already run.

## Explain the decision to Product and Finance

If a promotion brings more customers, code generation lets the team ship an endpoint faster. But Finance is paying for reversals, Support is investigating missing orders, and Operations is paged when a backlog grows. The right engineering question is which intervention changes those costs without creating a larger failure surface.

Suppose an internal proposal says, "Split Payment into five Microservices." The engineer responds with an alternative: "First make the payment identity durable and add reconciliation. Measure duplicate-charge incidents and unresolved-payment age. Extract the service only if release coupling or independent scaling remains a demonstrated constraint." This is a commercial argument grounded in system behavior, not an objection to new technology.

A practical decision record includes an estimate with explicit unknown inputs:

```text
Monthly loss to investigate = incidents × support minutes × loaded cost/minute
Potential benefit         = avoidable loss + recovered customer value
Engineering cost          = build + infrastructure + on-call + ongoing tests
Choose a plan              = compare benefit, risk, and cost at the same scope
```

There is no honest ROI percentage until incidents, costs and affected customers are measured. A faster API that doubles manual reconciliation work may harm the business. Likewise, a technically elegant migration may miss the promotion deadline without reducing any customer-facing risk.

This same meeting can be conducted in English with colleagues in Singapore, Bangkok or elsewhere. International communication is a practical engineering capability, not just vocabulary study. The engineer must state the risk, the uncertain evidence, the option and the next test without hiding behind architecture terminology:

> We have confirmed that a lost payment reply can leave an order pending while the mock provider has recorded a charge. We have not tested that failure against the production provider. Before we scale the workers, we need to verify the provider's idempotency window and readback API. I recommend a scoped failure test and an alert for unresolved payments older than our agreed recovery target.

That message does not claim production evidence based on a local test. It tells Product what can be decided now, Finance what risk is still open, and Operations what to monitor. The same structure works in an interview: explain the business objective, state an invariant, walk through a failed runtime path, show the test, and say what the evidence does **not** establish.

## When is the system ready for the next sale?

A full production readiness decision needs more than the seven passing local tests. The team must agree on a real provider contract, payment-state reconciliation, backup restoration, Recovery Point Objective (RPO), Recovery Time Objective (RTO), alerting, operational ownership and acceptance under measured peak traffic. None of those can be inferred from Python unit tests or a single laptop load run.

The learning sequence is deliberate: reproduce duplicate requests; create a charge with a lost reply; recover from a worker crash; verify atomic Outbox intent; add a broker and watch duplicates; apply load and observe queue age; restore a backup; explain the risk in English to someone making a business decision. Each stage has an observable artifact. Each unresolved condition remains visible.

The engineer who can write the endpoint is useful. The engineer who can tell a team exactly which failures the system tolerates, which it cannot yet tolerate, and which business promise those boundaries protect can make much larger decisions without guessing.
