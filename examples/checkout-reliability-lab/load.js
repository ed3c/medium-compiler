// Local exercise only: no real payments or publicly exposed API.
import http from 'k6/http';
import { check } from 'k6';

const runId = __ENV.RUN_ID || 'manual-1';
export const options = {
  scenarios: {
    promotion: { executor: 'constant-arrival-rate', rate: 20, timeUnit: '1s',
      duration: '20s', preAllocatedVUs: 20, maxVUs: 60 },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
    checks: ['rate>0.99'],
    dropped_iterations: ['count==0'],
  },
};
export default function () {
  const key = `${runId}-${__VU}-${__ITER}`;
  const request = JSON.stringify({ amount_cents: 1250, currency: 'USD' });
  const params = { headers: { 'Content-Type':'application/json', 'Idempotency-Key':key } };
  const response = http.post('http://127.0.0.1:8080/orders', request, params);
  check(response, {
    '202 accepted': (r) => r.status === 202,
    'order id present': (r) => !!r.json('order_id'),
  });
}
