import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const demoDir = path.join(__dirname, 'demo');

function syntaxHighlightScript() {
  return `
    function syntaxHighlight(json) {
      json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      return json.replace(
        /("(\\\\u[a-zA-Z0-9]{4}|\\\\[^u]|[^\\\\\\\\"])*"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g,
        function (match) {
          let cls = 'number';
          if (/^"/.test(match)) {
            cls = /:$/.test(match) ? 'key' : 'string';
          } else if (/true|false/.test(match)) {
            cls = 'boolean';
          } else if (/null/.test(match)) {
            cls = 'null';
          }
          return '<span class="' + cls + '">' + match + '</span>';
        }
      );
    }
  `;
}

function buildHtml(endpoint, prettyJson) {
  const escapedJson = JSON.stringify(prettyJson);
  return `<!DOCTYPE html>
<html>
<head>
<style>
  body {
    margin: 0; padding: 24px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    background: #1e1e1e;
    color: #d4d4d4;
  }
  .header {
    background: #2d2d2d;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 12px 18px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .method {
    background: #49cc90;
    color: #fff;
    font-weight: bold;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
  }
  .url {
    color: #9cdcfe;
    font-size: 14px;
  }
  .status {
    margin-left: auto;
    color: #49cc90;
    font-weight: bold;
  }
  pre {
    background: #1e1e1e;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 20px;
    overflow-x: auto;
    line-height: 1.5;
  }
  .key { color: #9cdcfe; }
  .string { color: #ce9178; }
  .number { color: #b5cea8; }
  .boolean { color: #569cd6; }
  .null { color: #569cd6; }
</style>
</head>
<body>
  <div class="header">
    <span class="method">GET</span>
    <span class="url">${endpoint}</span>
    <span class="status">200 OK</span>
  </div>
  <pre id="json"></pre>
  <script>
    ${syntaxHighlightScript()}
    document.getElementById('json').innerHTML = syntaxHighlight(${escapedJson});
  </script>
</body>
</html>`;
}

(async () => {
  const browser = await chromium.launch();

  const endpoints = [
    { url: 'http://localhost:8000/', name: 'api_root', path: '/' },
    { url: 'http://localhost:8000/api/kpi/current', name: 'api_kpi_current', path: '/api/kpi/current' },
    { url: 'http://localhost:8000/api/agents/status', name: 'api_agents_status', path: '/api/agents/status' },
    { url: 'http://localhost:8000/api/inventory/status?product_id=PRD-0001', name: 'api_inventory_status', path: '/api/inventory/status?product_id=PRD-0001' },
    { url: 'http://localhost:8000/api/events/recent?limit=5', name: 'api_events_recent', path: '/api/events/recent?limit=5' },
    { url: 'http://localhost:8000/api/simulation/status', name: 'api_simulation_status', path: '/api/simulation/status' },
    { url: 'http://localhost:8000/api/forecast/PRD-0001?horizon=7', name: 'api_forecast', path: '/api/forecast/PRD-0001?horizon=7' },
  ];

  for (const ep of endpoints) {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

    // Fetch raw JSON
    const resp = await page.goto(ep.url, { waitUntil: 'networkidle' });
    const rawText = await resp.text();
    let parsed;
    try { parsed = JSON.parse(rawText); } catch { parsed = rawText; }
    const pretty = JSON.stringify(parsed, null, 2);

    // Render styled page
    const html = buildHtml(ep.path, pretty);
    await page.setContent(html);
    await page.waitForTimeout(500);

    await page.screenshot({ path: path.join(demoDir, `${ep.name}.png`), fullPage: true });
    console.log(`Captured: ${ep.name}.png`);
    await page.close();
  }

  await browser.close();
  console.log('Done');
})();
