# Cloudflare Checkout Reliability Sandbox

This is deployable Cloudflare source. It is NOT evidence that the user's Cloudflare
account has installed it or that a distributed load/recovery test passed.

## Architecture

Cloudflare Worker (Access protected) -> CheckoutState SQLite Durable Object
-> Cloudflare Queue (at-least-once) -> ProviderState SQLite Durable Object
-> Provider readback -> Checkout State = PAID.

Two independent Durable Objects mean the provider commit can succeed while
Checkout stays PENDING. There is no cross-object ACID transaction or real money.
Each Access identity has one private pair of objects. Order counts are not capped
by the application; platform quotas apply across the Cloudflare account.
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

Cloudflare Workers Free is the required plan. The application no longer imposes
20 orders/day, 50 dispatches/day, 30 orders/identity, two lifetime manual replays,
or the 20/10-second route limiter. Queue consumer concurrency uses native
autoscaling instead of a fixed one-consumer cap. This does not increase the
account's Free quotas or demonstrate payment capacity.

Outbox partial indexes contain only undelivered keys and retry-eligible entries.
Pending COUNT scans the active index; the next alarm reads the first due-index
entry. Relay orders by next_attempt_at/key and joins only selected Orders.
Completed history is excluded from these indexes, not deleted. Pending/backlog
work can still increase reads; index inserts/removals add writes and the first
index creation scans existing rows. Manual recovery uses the pending index,
including published work whose Provider outcome must be read back.

Only pending work can be manually replayed, using the original payment key.
Each relay processes at most 15 entries; each entry has three automatic publish
attempts. A durable 30-second claim excludes routine concurrent relays; successful
Queue acknowledgement persists `published=1`. Create dispatches only its own key;
later Creates and alarms skip acknowledged entries. Recovery persists an alarm
before external awaits and reads the Provider before retrying an unknown publish.
Manual recovery reads all selected Provider evidence before resetting absent
entries; an epoch prevents stale completions from overwriting newer claims.
Lease expiry does not terminate an older send: unknown outcomes can still produce
same-key duplicate messages. This is not exactly-once publication or payment.
Queue batch size is one with two retries and a DLQ. These bounds stop
automatic failure loops; they are not lifetime usage caps. After platform quota
refusal, orders remain PENDING. Read back provider effects before recovery.
Manual replay does not reset Cloudflare usage or imply that a timeout failed.

No Cron triggers, preview URLs or persistent Workers Logs are enabled. The
workers.dev entry remains protected by Access. Only the authorized owner can
operate this sandbox; visitors cannot trigger remote load. Free plan quota
refusal is the relevant usage fee boundary. Existing paid subscriptions or
domain renewals require a separate Billing audit. Do not create an origin
fallback or automatically switch to Paid after quota failure.

The application cannot verify the account plan or estimate remaining platform
quota. Its JSON evidence reports this uncertainty. Read current usage from
Cloudflare; internal order counts are not invoice measurements. Old budget
records remain stored as history but no longer govern admission or dispatch.

## Scoped readback

`POST /api/state` requires exactly one explicit selection:
`{"key":"payment-key"}`, `{"runId":"unique-run"}`, or `{"full":true}`.
Missing, invalid or ambiguous selections refuse with HTTP 400; there is no
fallback to a full ledger. The response uses `checkout-remote-evidence@3` and
records `selection`; its invariant applies only to the selected rows.

For a new run, include `runId` in each `/api/create` payload. The immutable
payment key remains the provider idempotency identity. A different supplied
Run ID for an existing key refuses with 409; retry without a Run ID preserves
its saved association. Run IDs are indexed, exact metadata in Orders and
Charges, not key prefixes. Old rows remain unassigned and readable by key or
explicit full selection. Outbox run reads use the matching Orders keys.
Two new indexes add write/storage work; they avoid scanning unrelated runs.
The first constructor after deployment adds nullable columns and indexes to
existing objects. Old rows are not assigned a guessed Run ID. A rollback to the
old Provider implementation must first adapt its positional INSERT to explicit
columns; restoring Worker code does not remove the new SQLite column.

Payment polling reads only its key. Runner setup and teardown read only their
run. The UI defaults to Payment Readback; full ledger and independent PITR
bookmarks require a manual button. Add `includeBookmarks:true` for an explicit
bookmark request; bookmarks still do not establish a joint atomic snapshot.
Parallel Checkout/Provider reads also are not a cross-DO atomic snapshot. The
runner repeats same-key readback if PAID evidence is temporarily incomplete.

`readbackUsage` reports fully consumed native SQLite cursor `rowsRead` for
only the three readback SELECTs. Missing adapter measurements are null, never
estimated from response length. These counters exclude initialization,
Create/Queue/alarm SQL, writes, other Workers and account usage. Compare
Cloudflare usage separately and retain the exact observation window.

## Tests

Run from the repository root:
  node --experimental-sqlite --test tests/reliability_logic.test.mjs tests/cloudflare_interface.test.mjs
  node --test tests/scoped_readback_runtime.test.mjs
  python3 -m unittest discover -s tests -p test_reliability_site.py -v

The Node owner/transport adapters are contract tests. Recovery controls execute
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
official `cloudflared access login --quiet <protected-worker-url>` flow. The
URL is a positional argument; use the installed CLI help, not an unsupported
`--url` flag. A zero exit or an HTTP 200 after a login redirect does not prove
authorized API readback. Require the API JSON response for the original Run ID.
If a session expires, renew it and inspect existing Run/Payment Keys before
restarting a load; keep failed evidence and do not create replacement identities.
Load the short-lived application token into process environment `CF_ACCESS_TOKEN` via
`cloudflared access token --app <protected-worker-url>`; never paste tokens into
chat or commit them. `RUN_ID` must be unique. Set `ARRIVALS_PER_SECOND=1` and
`DURATION_SECONDS=4` for the first baseline; do not increase load after a failed
baseline. Allowed finite windows are 4, 8, 30 or 60 seconds at 1 or 2 arrivals/s,
with at most 60 scheduled intents plus a boundary slot. The longer windows are
operator-only sustained-load observations, not a daily capacity guarantee.
One VU per finite arrival plus a conservative boundary slot is preallocated
(up to 61); this separates generator capacity from settlement waiting. The boundary slot does not increase the arrival rate or window. Polls every two
seconds make observed settlement latency an upper bound that includes polling
and network delay. Admission/settlement/error/drop metrics are separate. Before remote execution, read back Billing and set
`CONFIRM_FREE_PLAN="Workers Free"` only after verification. This operator
confirmation is not an API check or a Cloudflare quota reservation. Platform
usage must be checked separately; do not increase load to exhaust Free quotas.
Export JSON using `EVIDENCE_FILE`. The runner reports readback request counts,
native SQL cursor rows read and response bytes alongside PAID latency.
Visitors never receive the operator token.

## P3 restore

Explicit `includeBookmarks:true` state requests include Checkout and Provider PITR bookmarks independently.
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
Do not reset production data or platform usage for a drill.

References:
- https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/
- https://developers.cloudflare.com/queues/configuration/dead-letter-queues/
- https://developers.cloudflare.com/workers/configuration/cloudflare-access/
