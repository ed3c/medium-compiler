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

Before deploying, read back Workers Free and Zero Trust Free in Billing. Do not
upgrade or activate a paid product. Keep Vercel on Hobby for personal learning.
Budget alerts are notifications, not spending caps. Account credentials and
subscriptions must be verified in the operator’s current session. To deploy:

1. Enable Workers, Queues and Zero Trust on the Cloudflare account.
2. From this directory sign in interactively: npx wrangler@4 login
3. Provision once:
   npx wrangler@4 queues create checkout-reliability-payments
   npx wrangler@4 queues create checkout-reliability-dlq
4. Deploy: npx wrangler@4 deploy
5. Dashboard -> Workers & Pages -> checkout-reliability-sandbox -> Access
   -> Protect this Worker. Preview URLs are disabled. Allow ONLY your own
   Cloudflare account members / exact authorized email.
6. Open the protected workers.dev URL, sign in and run the remote UI.
   It uses native ctx.access identity; no public database API Key or
   manually embedded JWT. Without Worker-Level Access, API returns 403; enabled Access may redirect
   anonymous requests to sign-in before Worker execution.
7. Do not announce deployment completion until the actual URL, Access
   denial test, Queue/DO evidence and source head are read back.

Cloudflare queues Free includes 10,000 operations/day across reads/writes/deletes,
not 10,000 fully settled payments. Verify current quotas before running load.

## Workload guards

One extra instance of the existing CheckoutState class holds a shared UTC-day
budget: 20 new intent reservations and 50 Queue publish reservations. Reservations
precede effects and are not refunded after uncertain failure. They conservatively
overcount work; they are not Cloudflare usage or invoice measurements. A missing
guard refuses admission. Existing pending intents remain readable when the budget
is exhausted; dispatch stops and does not schedule an endless quota retry alarm.
The next day requires an operator replay if no alarm remains scheduled.

Each identity still has a lifetime limit of 30 orders. Each pending order permits
two manual replays. Consumer concurrency is one; batch size one; two Queue retries
then DLQ. Read and write route groups each have a native 20/10-second rate limiter
per identity and Cloudflare location. That limiter is approximate and consumes a
Worker request before refusing with 429; it is not an account-wide financial cap.

No Cron triggers, preview URLs or persistent Workers Logs are enabled. The
workers.dev entry remains protected by Access so the learning UI is usable.
Immediate Tail can capture a bounded acceptance run. Free plan quota refusal,
not these counters, prevents usage overage billing for these products. Existing
paid subscriptions or domain renewals require a separate Billing audit. Do not
create an origin fallback or automatically switch to Paid after quota failure.

On adoption into an existing sandbox, the operator must seed the new daily
budget from the actual prior order and dispatch records before admitting new
work. Use authorized administrative SQLite access, not a public reset endpoint.
Never reset counters merely to make a load test pass.

## Tests

Run from the repository root:
  node --experimental-sqlite --test tests/reliability_logic.test.mjs tests/cloudflare_interface.test.mjs
  python3 -m unittest discover -s tests -p test_reliability_site.py -v

The Node owner/transport adapters are contract tests. Quota controls execute
the actual CheckoutState SQL in Node SQLite; they still do not prove native
Cloudflare DO/Queue behavior.
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
A remote runner requires the operator’s human Access identity because this
Worker accepts an email identity, not an anonymous service identity. Use the
official `cloudflared access login --url <protected-worker-url>` flow. Load the
short-lived application token into process environment `CF_ACCESS_TOKEN` via
`cloudflared access token --app <protected-worker-url>`; never paste tokens into
chat or commit them. `RUN_ID` must be unique. Set `ARRIVALS_PER_SECOND=1` and
`DURATION_SECONDS=4` for the first baseline; do not increase load after a failed
baseline. One VU per finite arrival plus a conservative boundary slot is preallocated
(up to 17); this separates generator capacity from settlement waiting. Both
quota preflights reserve that extra intent and its three dispatches. It does not
increase the arrival rate or window. Polls every two
seconds make observed settlement latency an upper bound that includes polling
and network delay. Admission/settlement/error/drop metrics are separate. The
preflight requires room for all intents and three dispatch reservations each.
That preflight is observational; the atomic admission guard remains decisive.
Export JSON using `EVIDENCE_FILE`. Visitors never receive the operator token.

## P3 restore

Read-only state includes Checkout and Provider PITR bookmarks independently.
They are NOT a joint atomic snapshot. No destructive restore endpoint is
exposed to visitors. A separate owner-authorized isolated Cloudflare
PITR drill must measure actual RPO/RTO, reconcile with independent
Provider charges, and observe restored order state before declaring PASS.
Reading bookmarks or exporting JSON alone is NOT disaster recovery proof.

The isolated drill in `dr/` deploys a separate Worker and two new SQLite DO
namespaces with no workers.dev, preview, route, Queue or Cron trigger. It reuses
the checkout/provider source but restricts the drill to one fixed payment. Its
restore actions are available only through an account service binding, never
through the public lab. Do not deploy `dr/proxy.jsonc`: use it only as a loopback
Wrangler development bridge to the private native Worker. Local DO bindings do
not support native PITR; the remote service binding reaches the deployed DOs.

After verifying Free plans and operator authority:

1. From this directory deploy: `npx wrangler@4 deploy --config dr/wrangler.jsonc`.
2. Start the loopback bridge: `npx wrangler@4 dev --config dr/proxy.jsonc --ip 127.0.0.1 --port 8877`.
3. Run `python3 dr/drive.py /absolute/path/outside/repo/dr-evidence.json` once.
4. Stop the bridge. Read back native version and confirm the private Worker
   has no public URLs, routes, Cron or persistent Logs.

The driver saves every input/readback, creates PENDING plus outbox, captures
independent bookmarks, commits one provider effect and marks PAID. It corrupts
only the isolated checkout amount, prepares native restore to the earlier
checkout bookmark and issues one restart. An uncertain restart is read back,
never repeated blindly. Restored checkout must be PENDING/1250 with pending
outbox while the original provider charge remains. Reconciliation must recover
PAID with the same charge ID. The receipt measures elapsed recovery and reports
zero lost intents only for that one case. It is not a regional service outage,
a joint cross-DO restore, or a production RPO/RTO guarantee. A used run ID or an
existing receipt refuses rerun; select a new isolated run explicitly in config.
Do not reset production data or daily counters for a drill.

References:
- https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/
- https://developers.cloudflare.com/queues/configuration/dead-letter-queues/
- https://developers.cloudflare.com/workers/configuration/cloudflare-access/
