import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://localhost:8000/docs', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);

  // Find all opblock elements (each endpoint row)
  const opblocks = await page.locator('.opblock').all();
  console.log(`Found ${opblocks.length} opblocks`);

  for (let i = 0; i < opblocks.length; i++) {
    const id = await opblocks[i].getAttribute('id');
    const summary = await opblocks[i].locator('.opblock-summary-description').textContent().catch(() => '');
    const path = await opblocks[i].locator('.opblock-summary-path').textContent().catch(() => '');
    console.log(`  [${i}] id="${id}" path="${path}" desc="${summary}"`);
  }

  // Try clicking the first endpoint summary
  const firstSummary = page.locator('.opblock-summary').first();
  console.log('\nClicking first opblock-summary...');
  await firstSummary.click();
  await page.waitForTimeout(1000);

  // Check if it expanded
  const expanded = await page.locator('.opblock.is-open').count();
  console.log(`Expanded blocks after click: ${expanded}`);

  await browser.close();
})();
