// Final screens for the homepage from a local, offline server (no API keys): 390x844 @3x.
const { chromium } = require('/Users/slowrain/ima2-work/vfx-capture/node_modules/playwright-core');
(async () => {
  const room = process.argv[2];
  const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, locale: 'ko-KR', isMobile: true, hasTouch: true });
  await ctx.addInitScript(() => localStorage.setItem('trpg_consent', '2026-11-09.2'));
  const page = await ctx.newPage();
  page.setDefaultTimeout(8000);
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const vis = async (re) => { const b = page.getByRole('button', { name: re }).first(); return (await b.count()) && (await b.isVisible()) ? b : null; };
  const buttons = async () => (await page.$$eval('button:visible, a.btn:visible', bs => bs.map(b => b.textContent.trim()).filter(Boolean))).join(' | ');
  await page.goto(`http://127.0.0.1:8790/r/${room}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);
  // appearance: a few clicks on the arrows for a distinct look
  const arrows = page.locator('#builder button:has-text("▶")');
  for (const [row, n] of [[1, 2], [2, 3], [3, 5], [5, 1]]) for (let k = 0; k < n; k++) await arrows.nth(row).click();
  await page.fill('input[placeholder="예: 아리아"]', '리아');
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'final/1_builder.png' });
  await (await vis(/다음: 직업 고르기/)).click(); await page.waitForTimeout(500);
  await page.getByRole('button', { name: '도적', exact: true }).click(); await page.waitForTimeout(300);
  await page.getByRole('button', { name: '풋내기 도둑' }).click(); await page.waitForTimeout(300);
  await (await vis(/자리에 앉기/)).click(); await page.waitForTimeout(1000);
  for (let i = 0; i < 30; i++) {
    const ok = page.locator('.reveal-ok:visible').first();
    if (await ok.count()) { await ok.click(); await page.waitForTimeout(300); continue; }
    const place = await vis(/지도에 올리기/);
    if (place) { const input = page.locator('#builder input:visible').first(); if (await input.count()) await input.fill(['버들골 방앗간', '늙은 참나무', '대장장이 오르반'][i % 3]); await place.click(); await page.waitForTimeout(500); continue; }
    const rest = await vis(/남은 표 한 번에 굴리기/); if (rest) { await rest.click(); await page.waitForTimeout(1000); continue; }
    break;
  }
  await (await vis(/빈자리 \d+개 모두/)).click(); await page.waitForTimeout(1200);
  await page.locator('#waiting').scrollIntoViewIfNeeded();
  await page.evaluate(() => document.querySelector('#waiting').scrollIntoView({ block: 'start' }));
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'final/2_party.png' });
  await (await vis(/^모험 시작$/)).click(); await page.waitForTimeout(4500);
  const say = async (text, wait = 2500) => { await page.fill('#text', text); await page.keyboard.press('Enter'); await page.waitForTimeout(wait); };
  await say('다들 준비됐지? 해 지기 전에 광장부터 한 바퀴 돌아보자.');
  await say('우물 안을 자세히 들여다본다', 3500);
  const look = await vis(/살펴보기: 우물/); if (look) { await look.click(); await page.waitForTimeout(3500); }
  const talk = await vis(/말 걸기:/); if (talk) { await talk.click(); await page.waitForTimeout(3500); }
  await page.screenshot({ path: 'final/3_scene.png' });
  console.log('scene:', await buttons());
  const roll = await vis(/d20 굴리기/);
  if (roll) { await roll.click(); await page.waitForTimeout(1300); await page.screenshot({ path: 'final/3b_roll.png' }); await page.waitForTimeout(3500); await page.screenshot({ path: 'final/3c_after_roll.png' }); }
  for (let i = 0; i < 3; i++) { const p = await vis(/그대로 받기/); if (p) { await p.click(); await page.waitForTimeout(2000); } }
  await say('/fight 붉은 모자 2 숲', 4500);
  await page.screenshot({ path: 'final/4_fight.png' });
  for (let i = 0; i < 3; i++) { const skip = await vis(/턴 넘기기/); if (skip) { await skip.click(); await page.waitForTimeout(3500); } }
  await page.screenshot({ path: 'final/5_fight_later.png' });
  console.log('fight:', await buttons());
  console.log(errors.join('\n') || 'no errors');
  await browser.close();
})();
