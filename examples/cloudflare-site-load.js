// Operator-run static traffic baseline; no dynamic API or payment effects.
import http from "k6/http";
import {check} from "k6";
const target = __ENV.TEST_URL?.replace(/\/$/, "");
const rate = Number(__ENV.ARRIVALS_PER_SECOND || 20), seconds = Number(__ENV.DURATION_SECONDS || 10);
const runId = __ENV.RUN_ID;
if (target !== "https://medium-compiler.ga874199.workers.dev") throw Error("Use the owned Cloudflare static site only");
if (!runId || !/^[A-Za-z0-9-]{1,40}$/.test(runId)) throw Error("Supply a unique RUN_ID");
if (!Number.isInteger(rate) || !Number.isInteger(seconds) || rate < 1 || rate > 1000 || seconds < 1 || seconds > 60 || rate * seconds > 10000)
  throw Error("Finite operator workload: max 10,000 static requests, rate <= 1,000/s, duration <= 60s");
export const options = {
  scenarios: {assets: {executor: "constant-arrival-rate", rate, timeUnit: "1s", duration: seconds + "s",
    preAllocatedVUs: 20, maxVUs: 100, gracefulStop: "10s"}},
  summaryTrendStats: ["min", "med", "p(95)", "p(99)", "max"],
  thresholds: {http_req_failed: ["rate==0"], checks: ["rate==1"], dropped_iterations: ["count==0"]}
};
export default function() {
  const response = http.get(target + "/reliability/", {timeout: "5s", tags: {scope: "static_asset"}});
  check(response, {"Lab asset and isolation headers": r => r.status === 200 &&
    r.body.includes("reliability-ready") && r.headers["Cross-Origin-Opener-Policy"] === "same-origin" &&
    r.headers["Cross-Origin-Embedder-Policy"] === "require-corp"});
}
export function handleSummary(data) {
  return {[__ENV.EVIDENCE_FILE || "stdout"]: JSON.stringify({runId, target,
    scope: "single runner static asset test; no payment, Queue or DO capacity claim",
    requestedRate: rate, seconds, maxScheduledRequests: rate * seconds + 1, metrics: data.metrics}, null, 2) + "\n"};
}
