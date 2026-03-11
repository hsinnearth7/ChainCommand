import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const kpiLatency = new Trend('kpi_latency');

export const options = {
  stages: [
    { duration: '1m', target: 10 },   // ramp up
    { duration: '3m', target: 50 },   // sustained load
    { duration: '1m', target: 100 },  // peak
    { duration: '1m', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    errors: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_KEY = __ENV.API_KEY || 'dev-key-change-me';
const headers = { 'X-API-Key': API_KEY, 'Content-Type': 'application/json' };

export default function () {
  // Health check
  const health = http.get(`${BASE_URL}/api/health`);
  check(health, { 'health 200': (r) => r.status === 200 });

  // KPI endpoint
  const start = Date.now();
  const kpi = http.get(`${BASE_URL}/api/kpi/current`, { headers });
  kpiLatency.add(Date.now() - start);
  check(kpi, { 'kpi 200': (r) => r.status === 200 });
  errorRate.add(kpi.status !== 200);

  // Inventory status
  const inv = http.get(`${BASE_URL}/api/inventory/status`, { headers });
  check(inv, { 'inventory 200': (r) => r.status === 200 });
  errorRate.add(inv.status !== 200);

  // Agents status
  const agents = http.get(`${BASE_URL}/api/agents/status`, { headers });
  check(agents, { 'agents 200': (r) => r.status === 200 });

  // Events
  const events = http.get(`${BASE_URL}/api/events/recent?limit=10`, { headers });
  check(events, { 'events 200': (r) => r.status === 200 });

  sleep(1);
}
