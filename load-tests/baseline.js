import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    baseline_load: {
      executor: 'constant-vus',
      vus: 5,
      duration: '60s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<1000'],
    checks: ['rate>0.99'],
  },
};

const BASE_URL =
  __ENV.BASE_URL ||
  'http://chay-demo-api.chay-devsecops.svc.cluster.local';

export default function () {
  const health = http.get(`${BASE_URL}/health`);

  check(health, {
    'health returns 200': (r) => r.status === 200,
  });

  const orders = http.get(`${BASE_URL}/api/orders`);

  check(orders, {
    'orders returns 200': (r) => r.status === 200,
  });

  sleep(0.5);
}
