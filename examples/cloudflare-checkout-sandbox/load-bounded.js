// Controlled operator-side smoke load, NOT a public browser load button.
// Run only against local wrangler dev with Access test identity OR your own
// Access-protected sandbox with an operator-owned service token.
import http from "k6/http";
import {check,sleep} from "k6";
const url=__ENV.TEST_URL||"http://127.0.0.1:8787";
const runId=__ENV.RUN_ID||"local-smoke";
if(!/^https?:\/\/(?:127\.0\.0\.1:8787|localhost:8787)(?:\/)?$/.test(url)
   && !(__ENV.CF_ACCESS_CLIENT_ID&&__ENV.CF_ACCESS_CLIENT_SECRET))
  throw Error("Remote targets require operator-owned Cloudflare Access service credentials");
export const options={
  scenarios:{bounded:{executor:"constant-arrival-rate",rate:2,timeUnit:"1s",duration:"8s",
    preAllocatedVUs:2,maxVUs:4}},
  thresholds:{"http_req_failed":["rate<0.10"],"http_req_duration":["p(95)<1500"],
    "checks":["rate>0.90"],"dropped_iterations":["count==0"]}
};
export default function(){
  const key=runId+"-"+__VU+"-"+__ITER;
  const headers={"Content-Type":"application/json"};
  if(__ENV.CF_ACCESS_CLIENT_ID&&__ENV.CF_ACCESS_CLIENT_SECRET){
    headers["CF-Access-Client-Id"]=__ENV.CF_ACCESS_CLIENT_ID;
    headers["CF-Access-Client-Secret"]=__ENV.CF_ACCESS_CLIENT_SECRET;
  }
  const r=http.post(url+"/api/create",JSON.stringify({key,amount:1250,fault:"none"}),{headers});
  check(r,{"intent admitted":v=>v.status===202,"accepted != paid":v=>v.json("message").includes("pending")});
  sleep(0.05);
}
