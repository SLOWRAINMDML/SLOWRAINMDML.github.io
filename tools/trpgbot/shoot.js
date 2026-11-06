// Real web client (repo/web) fed with real Table snapshots through a stand-in WebSocket.
const { chromium } = require('/Users/slowrain/ima2-work/vfx-capture/node_modules/playwright-core');
const fs = require('fs');
(async () => {
  const data = JSON.parse(fs.readFileSync('/tmp/trpgbot/demo/views.json', 'utf8'));
  const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const errors = [];
  fs.mkdirSync('/tmp/trpgbot/ui', { recursive: true });
  for (const shot of data.shots) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, locale: 'ko-KR', isMobile: true, hasTouch: true });
    const page = await ctx.newPage();
    page.on('pageerror', e => errors.push(`${shot.name}: ${e.message}`));
    page.on('console', m => { if (m.type() === 'error') errors.push(`${shot.name}: ${m.text()}`); });
    await page.addInitScript(([shot, looks]) => {
      localStorage.setItem('trpg_table_token', 'demo');
      class DemoSocket {
        constructor() {
          this.readyState = 1;
          setTimeout(() => this.onmessage && this.onmessage({ data: JSON.stringify({
            t: 'init', playbooks: [], options: { looks }, history: shot.history,
            started: true, lobby: [], you: shot.you, build: null, my_look: null, rules: {}, pack: 'demo', replay: null, view: shot.view,
          }) }), 30);
        }
        send(raw) {
          const msg = JSON.parse(raw);
          if (msg.t === 'rejoin') setTimeout(() => this.onmessage({ data: JSON.stringify({
            t: 'update', outputs: [], started: true, lobby: [], you: shot.you, build: null, my_look: null, rules: {}, pack: 'demo', replay: null, view: shot.view,
          }) }), 30);
        }
        close() {}
      }
      DemoSocket.OPEN = 1;
      window.WebSocket = DemoSocket;
    }, [shot, data.looks]);
    await page.goto('http://127.0.0.1:8766/index.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2500);
    await page.screenshot({ path: `/tmp/trpgbot/ui/${shot.name}.png` });
    await ctx.close();
  }
  await browser.close();
  console.log(errors.join('\n') || 'no errors');
})();
