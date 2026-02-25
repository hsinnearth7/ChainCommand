import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const demoDir = path.join(__dirname, 'demo');
const BASE = 'http://localhost:8000';

async function captureEndpoint(browser, { id, name, paramFills }) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(`${BASE}/docs`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  const block = page.locator(`#${id}`);
  // Click summary to expand
  await block.locator('.opblock-summary').click();
  await page.waitForTimeout(800);

  // Click "Try it out"
  await block.locator('button.try-out__btn').click();
  await page.waitForTimeout(500);

  // Fill parameters if needed
  if (paramFills) {
    for (const [placeholder, value] of Object.entries(paramFills)) {
      const input = block.locator(`input[placeholder="${placeholder}"]`);
      if (await input.count() > 0) {
        await input.clear();
        await input.fill(value);
      }
    }
  }

  // Click Execute
  await block.locator('button.execute').click();
  await page.waitForTimeout(2500);

  // Scroll the expanded block into view
  await block.scrollIntoViewIfNeeded();
  await page.waitForTimeout(500);

  await page.screenshot({ path: path.join(demoDir, `${name}.png`), fullPage: true });
  console.log(`Captured: ${name}.png`);
  await page.close();
}

(async () => {
  const browser = await chromium.launch();

  // 1. Overview
  const overviewPage = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await overviewPage.goto(`${BASE}/docs`, { waitUntil: 'networkidle' });
  await overviewPage.waitForTimeout(2000);
  await overviewPage.screenshot({ path: path.join(demoDir, 'swagger_overview.png'), fullPage: true });
  console.log('Captured: swagger_overview.png');
  await overviewPage.close();

  // 2-7. Individual endpoints with Try It Out + Execute
  const endpoints = [
    { id: 'operations-dashboard-get_current_kpi_api_kpi_current_get', name: 'swagger_kpi' },
    { id: 'operations-dashboard-get_agents_status_api_agents_status_get', name: 'swagger_agents' },
    { id: 'operations-dashboard-get_recent_events_api_events_recent_get', name: 'swagger_events' },
    { id: 'operations-dashboard-get_inventory_status_api_inventory_status_get', name: 'swagger_inventory' },
    { id: 'operations-dashboard-get_forecast_api_forecast__product_id__get', name: 'swagger_forecast', paramFills: { product_id: 'PRD-0001' } },
    { id: 'operations-control-simulation_status_api_simulation_status_get', name: 'swagger_simulation' },
  ];

  for (const ep of endpoints) {
    await captureEndpoint(browser, ep);
  }

  await browser.close();
  console.log('All screenshots saved to demo/');
})();
