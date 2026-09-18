import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    autoscaling_load: {
      executor: 'constant-vus',
      vus: 40,
      duration: '3m',
    },
  },

  thresholds: {
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
  },
};

const BASE_URL =
  __ENV.BASE_URL ||
  'http://chay-demo-api.chay-devsecops.svc.cluster.local';

const payload = JSON.stringify({
  product_id: 'hpa-load-test',
  quantity: 1,
  mode: 'normal',
});

const params = {
  headers: {
    'Content-Type': 'application/json',
  },
};

export default function () {
  const response = http.post(
    `${BASE_URL}/api/orders`,
    payload,
    params
  );

  check(response, {
    'order created under load': (r) => r.status === 201,
  });
}
