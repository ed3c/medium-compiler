# Cloudflare Checkout Reliability Sandbox

This is deployable Cloudflare source. It is NOT evidence that the user's Cloudflare
account has installed it or that a distributed load/recovery test passed.

## Architecture

Cloudflare Worker (Access protected) -> CheckoutState SQLite Durable Object
-> Cloudflare Queue (at-least-once) -> ProviderState SQLite Durable Object
-> Provider readback -> Checkout State = PAID.

Two independent Durable Objects mean the provider commit can succeed while
Checkout stays PENDING. There is no cross-object ACID transaction or real money.
Each Access identity has one private pair of objects and a maximum of 30 orders.
Queue delivery, three bounded relay attempts and DLQ prevent unlimited retries.
All inputs are bounded and effects use stable payment keys. The public Vercel
frontend carries no account keys and cannot trigger this Worker anonymously.

## Install: actions performed in your Cloudflare account

Cloudflare is NOT connected to this ChatGPT session. To deploy yourself:

1. Enable Workers, Queues and Zero Trust on the Cloudflare account.
2. From this directory sign in interactively: npx wrangler@4 login
3. Provision once:
   npx wrangler@4 queues create checkout-reliability-payments
   npx wrangler@4 queues create checkout-reliability-dlq
4. Deploy: npx wrangler@4 deploy
5. Dashboard -> Workers & Pages -> checkout-reliability-sandbox -> Access
   -> Protect this Worker -> Production and preview. Allow ONLY your own
   Cloudflare account members / exact authorized email.
6. Open the protected workers.dev URL, sign in and run the remote UI.
   It uses native ctx.access identity; no public database API Key or
   manually embedded JWT. Without Access, API returns 403.
7. Do not announce deployment completion until the actual URL, Access
   denial test, Queue/DO evidence and source head are read back.

Cloudflare queues Free includes 10,000 operations/day across reads/writes/deletes,
not 10,000 fully settled payments. Verify current quotas before running load.

## Tests

Run from the repository root:
  node --test tests/reliability_logic.test.mjs tests/cloudflare_interface.test.mjs
  python3 -m unittest discover -s tests -p test_reliability_site.py -v

The Node fake-owner tests are contract tests, NOT deployed DO/Queue observations.
For local Wrangler testing, configure a dev-only Access identity following
https://developers.cloudflare.com/workers/configuration/cloudflare-access/ .
Never commit real account identity or secrets to the production config.

## P1 actual Cloudflare acceptance

Create order; capture Checkout PENDING and Outbox. Inject lost_reply.
Confirm mock Provider COMMIT happened once while Checkout remained PENDING.
Observe Queue retry, matching Provider readback, PAID state and a single
Charge. Verify duplicate key with changed amount refuses. Test a real Queue
outage/recovery separately. Missing evidence remains NOT_RUN.

## P2 independent bounded load

Run the bundled load-bounded.js with k6 from an independent operator
machine against local Wrangler dev or a separately Access-authenticated
test environment. Default is 2 arrivals/second for 8 seconds.
Measure PAID completion, not just HTTP 202. Observe p95/p99, errors,
Queue backlog, Pending Age, DLQ and operation cost.
Never offer uncontrolled public load generation.
A remote k6 runner may use an operator-only Access service token kept
outside the repository. Visitors do not need this token.

## P3 restore

Read-only state includes Checkout and Provider PITR bookmarks independently.
They are NOT a joint atomic snapshot. No destructive restore endpoint is
exposed to visitors. A separate owner-authorized isolated Cloudflare
PITR drill must measure actual RPO/RTO, reconcile with independent
Provider charges, and observe restored order state before declaring PASS.
Reading bookmarks or exporting JSON alone is NOT disaster recovery proof.

References:
- https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/
- https://developers.cloudflare.com/queues/configuration/dead-letter-queues/
- https://developers.cloudflare.com/workers/configuration/cloudflare-access/
