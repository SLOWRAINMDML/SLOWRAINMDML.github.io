"use strict";

// Everything on the page is drawn from content/games.json (built by tools/build_content.py).
const SLIDE_MS = 7000;
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const TEXT = {
  ko: {
    skip: "게임 목록으로 건너뛰기",
    "nav.games": "게임", "nav.studio": "스튜디오", "nav.contact": "문의", "nav.cta": "게임 둘러보기",
    h1: "SLOWRAIN GAMES 게임",
    loading: "게임을 불러오는 중이에요…",
    strip: "SMALL STUDIO · BIG PLAYGROUNDS",
    "games.title": "오늘은 어떤 세계로 떠나볼까요",
    "filter.all": "전체", "genre.all": "모든 장르",
    empty: "조건에 맞는 게임이 없어요. 다른 장르를 골라 보세요.",
    error: "게임 정보를 불러오지 못했어요.", retry: "다시 불러오기 ↻",
    "studio.title": "천천히 내리는 비처럼,<br>오래 스며드는 재미<span class=\"accent\">.</span>",
    "studio.p1": "슬로우레인게임즈는 한국의 작은 인디 게임 스튜디오입니다. 친구와 깔깔 웃는 로블록스 파티 게임부터 한 수 한 수 고민하는 다크 판타지 전술 RPG, 씨앗 하나에서 세계가 자라나는 모험 RPG까지, 장르는 달라도 “한 판만 더”를 부르는 재미를 만듭니다.",
    "studio.p2": "엉뚱한 상상 하나에서 시작해, 누구나 바로 이해하고 오래 기억하는 놀이로 다듬는 것. 그게 우리가 게임을 만드는 방식이에요.",
    "stats.roblox": "로블록스 게임", "stats.pc": "PC 게임", "stats.since": "시작한 해",
    "contact.title": "문의 · 소식 받기",
    "contact.body": "게임 문의와 협업 제안은 메일로 보내 주세요. 새 게임과 업데이트 소식은 디스코드와 SNS에서 가장 먼저 전해요.",
    "contact.mail": "메일 보내기", "contact.discord": "커뮤니티 참여하기",
    "contact.steam": "Tactics to the devil dungeon 찜하기",
    "contact.roblox": "WISESLOWRAIN 팔로우하기",
    "footer.rights": "All rights reserved.",
    "footer.note": "Roblox와 Steam은 각 소유자의 상표입니다.",
    playRoblox: "Roblox에서 플레이", wishlist: "Steam에서 찜하기", play: "플레이", wish: "찜하기",
    follow: "출시 소식 받기", followShort: "소식 받기",
    details: "자세히 보기", live: "지금 플레이", players: n => `서버 최대 ${n}명`,
    released: d => `${d} 공개`, close: "닫기", pause: "자동 넘김 멈춤", resume: "자동 넘김 재생",
    prev: "이전", next: "다음", openGame: t => `${t} 자세히 보기`,
    tags: { tactics: "전술 RPG", rpg: "RPG", story: "스토리", adventure: "모험", action: "액션", coop: "협동", versus: "대전", cozy: "힐링", puzzle: "퍼즐", rhythm: "리듬" },
  },
  en: {
    skip: "Skip to the games",
    "nav.games": "Games", "nav.studio": "Studio", "nav.contact": "Contact", "nav.cta": "Browse games",
    h1: "SLOWRAIN GAMES",
    loading: "Loading games…",
    strip: "SMALL STUDIO · BIG PLAYGROUNDS",
    "games.title": "Which world will you visit today",
    "filter.all": "All", "genre.all": "All genres",
    empty: "No games match. Try another genre.",
    error: "We couldn't load the games.", retry: "Try again ↻",
    "studio.title": "Like slow rain,<br>fun that soaks in<span class=\"accent\">.</span>",
    "studio.p1": "SLOWRAIN GAMES is a small indie game studio from Korea. From giggly Roblox party games to a dark fantasy tactics RPG where every move counts and an adventure RPG whose world grows from a seed, we make games that keep you saying “just one more round.”",
    "studio.p2": "We start from one silly idea and polish it until anyone gets it right away and remembers it for a long time. That's how we make games.",
    "stats.roblox": "Roblox games", "stats.pc": "PC games", "stats.since": "Since",
    "contact.title": "Contact & news",
    "contact.body": "Send game questions and collaboration ideas by email. New games and updates land first on Discord and social media.",
    "contact.mail": "Send an email", "contact.discord": "Join the community",
    "contact.steam": "Wishlist Tactics to the devil dungeon",
    "contact.roblox": "Follow WISESLOWRAIN",
    "footer.rights": "All rights reserved.",
    "footer.note": "Roblox and Steam are trademarks of their respective owners.",
    playRoblox: "Play on Roblox", wishlist: "Wishlist on Steam", play: "Play", wish: "Wishlist",
    follow: "Get release news", followShort: "Follow",
    details: "Details", live: "Play now", players: n => `Up to ${n} per server`,
    released: d => `Out ${d}`, close: "Close", pause: "Pause slideshow", resume: "Play slideshow",
    prev: "Previous", next: "Next", openGame: t => `More about ${t}`,
    tags: { tactics: "Tactics RPG", rpg: "RPG", story: "Story", adventure: "Adventure", action: "Action", coop: "Co-op", versus: "Versus", cozy: "Cozy", puzzle: "Puzzle", rhythm: "Rhythm" },
  },
};

const ICON = {
  steam: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.253 0-2.265-1.014-2.265-2.265z"/></svg>',
  roblox: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18.926 23.998 0 18.892 5.075.002 24 5.108ZM15.348 10.09l-5.282-1.453-1.414 5.273 5.282 1.453z"/></svg>',
};

const state = {
  lang: pickLang(), games: [], featured: [], platform: "all", genre: "all",
  current: 0, timer: null, paused: reducedMotion.matches, hover: false, dialogGame: null,
};

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const t = key => TEXT[state.lang][key] ?? TEXT.ko[key] ?? key;
const esc = value => String(value ?? "").replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch]);
const pick = obj => (obj && (obj[state.lang] ?? obj.ko ?? obj.en)) || "";

function pickLang() {
  const saved = localStorage.getItem("slowrain-lang");
  if (saved === "ko" || saved === "en") return saved;
  return (navigator.language || "ko").toLowerCase().startsWith("ko") ? "ko" : "en";
}

function titleHTML(game) {
  const main = pick(game.title);
  const sub = state.lang === "ko" && game.title.en && game.title.en !== main ? `<span class="en-sub">${esc(game.title.en)}</span>` : "";
  return `${esc(main)}${sub}`;
}

function formatDate(iso) {
  if (!iso) return "";
  const date = new Date(`${iso}T00:00:00`);
  return state.lang === "ko"
    ? `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, "0")}.${String(date.getDate()).padStart(2, "0")}`
    : date.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

// A PC game can be headed for several stores (Steam, STOVE); a Roblox game is just "roblox".
const platformsOf = game => game.platforms || [game.platform];
const isPC = game => game.platform !== "roblox";
const PLATFORM_BADGE = {
  steam: `<span class="badge badge--steam">${ICON.steam}STEAM</span>`,
  stove: '<span class="badge badge--stove">STOVE</span>',
  roblox: `<span class="badge badge--roblox">${ICON.roblox}ROBLOX</span>`,
};

function badges(game) {
  const platform = platformsOf(game).map(p => PLATFORM_BADGE[p] || "").join("");
  const status = game.status
    ? `<span class="badge badge--soon">${esc(pick(game.status))}</span>`
    : `<span class="badge badge--live">${esc(t("live"))}</span>`;
  return platform + status;
}

function ctaLabel(game, short) {
  if (game.platform === "roblox") return short ? t("play") : t("playRoblox");
  if (game.url) return short ? t("wish") : t("wishlist");
  return short ? t("followShort") : t("follow");   // no store page yet: point at the news links
}

function ctaIcon(game) {
  if (game.platform === "roblox") return ICON.roblox;
  return game.url ? ICON.steam : "";
}

// Store link, or the on-page contact section for a game without a store page yet.
function ctaAttrs(game) {
  return game.url ? `href="${esc(game.url)}" target="_blank" rel="noopener"` : 'href="#contact" data-to-contact';
}

function ctaButton(game) {
  return `<a class="pixel-button ${isPC(game) ? "steam" : "sky"}" ${ctaAttrs(game)}>${ctaIcon(game)}${esc(ctaLabel(game))} <span aria-hidden="true">${game.url ? "↗" : "↓"}</span></a>`;
}

// ---------- Loading ----------

async function loadGames() {
  $("#content-error").hidden = true;
  try {
    const res = await fetch("./content/games.json", { cache: "no-cache" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    state.games = data.games;
    const byId = new Map(state.games.map(g => [g.id, g]));
    state.featured = (data.featured || []).map(id => byId.get(id)).filter(Boolean);
    if (!state.featured.length) state.featured = state.games.slice(0, 6);
    renderAll();
    openFromHash();
  } catch (error) {
    console.error(error);
    $("#content-error").hidden = false;
    $("#slides").innerHTML = `<div class="slide-loading">${esc(t("error"))}</div>`;
  }
}

function renderAll() {
  applyStaticText();
  renderSlides();
  renderFilters();
  renderGames();
  renderStats();
  if (state.dialogGame) fillDialog(state.dialogGame);
}

function applyStaticText() {
  document.documentElement.lang = state.lang;
  $$("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
  $$("[data-i18n-html]").forEach(el => { el.innerHTML = t(el.dataset.i18nHtml); });
  $$(".lang-switch button").forEach(btn => btn.setAttribute("aria-pressed", String(btn.dataset.lang === state.lang)));
  $("#dialog-close").setAttribute("aria-label", t("close"));
  $$('[data-step="-1"]').forEach(btn => btn.setAttribute("aria-label", t("prev")));
  $$('[data-step="1"]').forEach(btn => btn.setAttribute("aria-label", t("next")));
  updateAutoplayButton();
}

// ---------- Showcase carousel ----------

function renderSlides() {
  const slides = state.featured;
  $("#slides").innerHTML = slides.map((game, i) => `
    <article class="slide${i === state.current ? " active" : ""}" role="group" aria-roledescription="slide"
      aria-label="${i + 1} / ${slides.length}: ${esc(pick(game.title))}" ${i === state.current ? "" : 'aria-hidden="true"'}>
      <img class="slide-art" src="${esc(game.hero || game.cover)}" alt=""${game.heroFocus ? ` style="object-position:${esc(game.heroFocus)}"` : ""} ${i === 0 ? 'fetchpriority="high"' : 'loading="lazy"'}>
      <div class="slide-content">
        <p class="badge-row">${badges(game)}</p>
        ${game.logo
          ? `<h2 class="slide-title"><img class="slide-logo" src="${esc(game.logo)}" alt="${esc(pick(game.title))}"></h2>`
          : `<h2 class="slide-title">${esc(pick(game.title))}${state.lang === "ko" && game.title.en !== game.title.ko ? `<span class="sub">${esc(game.title.en)}</span>` : ""}</h2>`}
        <p class="slide-tagline">${esc(pick(game.tagline))}</p>
        <div class="slide-actions">
          ${ctaButton(game)}
          <button class="pixel-button ghost" type="button" data-open="${esc(game.id)}">${esc(t("details"))}</button>
        </div>
      </div>
    </article>`).join("");

  $("#slide-tabs").innerHTML = slides.map((game, i) => `
    <button class="slide-tab" type="button" role="tab" data-slide="${i}" aria-selected="${i === state.current}">
      <img src="${esc(game.icon || game.cover)}" alt="" loading="lazy"><span>${esc(pick(game.title))}</span><span class="progress"></span>
    </button>`).join("");
  $("#slide-total").textContent = String(slides.length).padStart(2, "0");
  $("#showcase-bar").hidden = slides.length < 2;
  $(".showcase").style.setProperty("--slide-time", `${SLIDE_MS}ms`);
  showSlide(state.current, false);
}

function showSlide(index, focusTab) {
  const count = state.featured.length;
  if (!count) return;
  state.current = (index + count) % count;
  $$(".slide").forEach((el, i) => {
    const active = i === state.current;
    el.classList.toggle("active", active);
    el.toggleAttribute("aria-hidden", !active);
    $$("a, button", el).forEach(ctrl => { ctrl.tabIndex = active ? 0 : -1; });
  });
  $$(".slide-tab").forEach((tab, i) => {
    const active = i === state.current;
    tab.setAttribute("aria-selected", String(active));
    // Restart the progress bar animation.
    const bar = $(".progress", tab);
    bar.style.animation = "none";
    void bar.offsetWidth;
    bar.style.animation = "";
    if (active && focusTab) tab.focus({ preventScroll: true });
    if (active) centerTab(tab);
  });
  $("#slide-current").textContent = String(state.current + 1).padStart(2, "0");
  schedule();
}

// Scroll only the tab strip sideways. scrollIntoView() would also scroll the page,
// pulling a reader back to the top whenever the slideshow advanced.
function centerTab(tab) {
  const strip = $("#slide-tabs");
  const delta = tab.getBoundingClientRect().left - strip.getBoundingClientRect().left - (strip.clientWidth - tab.offsetWidth) / 2;
  strip.scrollBy({ left: delta, behavior: reducedMotion.matches ? "auto" : "smooth" });
}

function schedule() {
  clearTimeout(state.timer);
  const stopped = state.paused || state.hover || document.hidden || state.featured.length < 2;
  $(".showcase").classList.toggle("paused", stopped);
  if (!stopped) state.timer = setTimeout(() => showSlide(state.current + 1), SLIDE_MS);
}

function updateAutoplayButton() {
  const btn = $("#autoplay");
  btn.innerHTML = `<span aria-hidden="true">${state.paused ? "▶" : "Ⅱ"}</span>`;
  btn.setAttribute("aria-label", state.paused ? t("resume") : t("pause"));
}

function bindShowcase() {
  const showcase = $(".showcase");
  showcase.addEventListener("click", event => {
    const step = event.target.closest("[data-step]");
    if (step) showSlide(state.current + Number(step.dataset.step));
    const tab = event.target.closest("[data-slide]");
    if (tab) showSlide(Number(tab.dataset.slide));
  });
  $("#autoplay").addEventListener("click", () => {
    state.paused = !state.paused;
    updateAutoplayButton();
    schedule();
  });
  const slides = $("#slides");
  slides.addEventListener("mouseenter", () => { state.hover = true; schedule(); });
  slides.addEventListener("mouseleave", () => { state.hover = false; schedule(); });
  showcase.addEventListener("focusin", () => { state.hover = true; schedule(); });
  showcase.addEventListener("focusout", () => { state.hover = false; schedule(); });
  showcase.addEventListener("keydown", event => {
    if (event.target.closest("input, textarea")) return;
    if (event.key === "ArrowLeft") showSlide(state.current - 1, event.target.matches(".slide-tab"));
    if (event.key === "ArrowRight") showSlide(state.current + 1, event.target.matches(".slide-tab"));
  });
  let startX = null;
  slides.addEventListener("pointerdown", event => { startX = event.clientX; });
  slides.addEventListener("pointerup", event => {
    if (startX === null) return;
    const dx = event.clientX - startX;
    startX = null;
    if (Math.abs(dx) > 50) showSlide(state.current + (dx < 0 ? 1 : -1));
  });
  document.addEventListener("visibilitychange", schedule);
}

// ---------- Game list ----------

function visibleByPlatform() {
  return state.games.filter(g => state.platform === "all" || platformsOf(g).includes(state.platform));
}

function renderFilters() {
  for (const key of ["all", "steam", "stove", "roblox"]) {
    const n = key === "all" ? state.games.length : state.games.filter(g => platformsOf(g).includes(key)).length;
    $(`[data-count="${key}"]`).textContent = n;
  }
  $$("#platform-filters .filter").forEach(btn => {
    const active = btn.dataset.platform === state.platform;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-pressed", String(active));
  });
  const pool = visibleByPlatform();
  const counts = {};
  pool.forEach(g => g.tags.forEach(tag => { counts[tag] = (counts[tag] || 0) + 1; }));
  if (state.genre !== "all" && !counts[state.genre]) state.genre = "all";
  const order = Object.keys(TEXT.ko.tags).filter(tag => counts[tag]);
  const chip = (key, label, n) => `<button class="chip${state.genre === key ? " active" : ""}" type="button" data-genre="${key}" aria-pressed="${state.genre === key}">${esc(label)}${n ? ` · ${n}` : ""}</button>`;
  $("#genre-chips").innerHTML = chip("all", t("genre.all")) + order.map(tag => chip(tag, t("tags")[tag], counts[tag])).join("");
}

function cardHTML(game, index) {
  const tags = `<div class="tags">${game.tags.map(tag => `<span class="tag">${esc(t("tags")[tag] || tag)}</span>`).join("")}</div>`;
  const play = `<a class="play-link" ${ctaAttrs(game)} aria-label="${esc(ctaLabel(game))}: ${esc(pick(game.title))}">${ctaIcon(game)}${esc(ctaLabel(game, true))} ${game.url ? "↗" : "↓"}</a>`;
  const open = `<button class="card-hit" type="button" data-open="${esc(game.id)}" aria-label="${esc(t("openGame")(pick(game.title)))}"></button>`;
  const delay = `style="animation-delay:${Math.min(index, 12) * 40}ms"`;
  const alt = game.gallery?.[1] && !isPC(game) ? `<img class="alt" src="${esc(game.gallery[1])}" alt="" loading="lazy">` : "";

  if (isPC(game)) {
    const highlights = (pick(game.highlights) || []).slice(0, 3).map(h => `<li>${esc(h)}</li>`).join("");
    return `
      <article class="card card--feature" id="game-${esc(game.id)}" ${delay}>
        ${open}
        <div class="card-media"><picture><source media="(max-width: 680px)" srcset="${esc(game.cover)}"><img src="${esc(game.poster || game.cover)}" alt="" loading="lazy"></picture><p class="badge-row">${badges(game)}</p></div>
        <div class="card-side">
          <h3>${esc(pick(game.title))}</h3>
          <p class="card-tagline">${esc(pick(game.tagline))}</p>
          <ul class="feature-list">${highlights}</ul>
          <div class="card-foot">${tags}${play}</div>
        </div>
      </article>`;
  }
  return `
    <article class="card" id="game-${esc(game.id)}" ${delay}>
      ${open}
      <div class="card-media"><img src="${esc(game.cover)}" alt="" loading="lazy">${alt}<p class="badge-row">${badges(game)}</p></div>
      <div class="card-body">
        ${game.icon ? `<img class="card-icon" src="${esc(game.icon)}" alt="" loading="lazy" width="58" height="58">` : ""}
        <h3>${titleHTML(game)}</h3>
      </div>
      <p class="card-tagline">${esc(pick(game.tagline))}</p>
      <div class="card-foot">${tags}${play}</div>
    </article>`;
}

function renderGames() {
  const list = visibleByPlatform().filter(g => state.genre === "all" || g.tags.includes(state.genre));
  $("#game-grid").innerHTML = list.map(cardHTML).join("");
  $("#empty-state").hidden = list.length > 0;
}

function renderStats() {
  const counts = { pc: state.games.filter(isPC).length, roblox: state.games.filter(g => !isPC(g)).length };
  $$("[data-stat]").forEach(el => { el.textContent = counts[el.dataset.stat]; });
}

function bindFilters() {
  $("#platform-filters").addEventListener("click", event => {
    const btn = event.target.closest("[data-platform]");
    if (!btn) return;
    state.platform = btn.dataset.platform;
    renderFilters();
    renderGames();
  });
  $("#genre-chips").addEventListener("click", event => {
    const btn = event.target.closest("[data-genre]");
    if (!btn) return;
    state.genre = btn.dataset.genre;
    renderFilters();
    renderGames();
  });
}

// ---------- Detail dialog ----------

function media(game) {
  const items = [];
  if (isPC(game)) items.push({ type: "img", src: game.cover });
  (game.videos || []).forEach(video => items.push({ type: "video", src: video.src, poster: video.poster }));
  (game.gallery || []).forEach(src => items.push({ type: "img", src }));
  return items;
}

function showMedia(items, index) {
  const item = items[index];
  $("#dialog-stage").innerHTML = item.type === "video"
    ? `<video src="${esc(item.src)}" poster="${esc(item.poster || "")}" autoplay muted loop playsinline></video>`
    : `<img src="${esc(item.src)}" alt="">`;
  $$("#dialog-thumbs button").forEach((btn, i) => btn.setAttribute("aria-current", String(i === index)));
}

function fillDialog(game) {
  const items = media(game);
  $("#dialog-thumbs").innerHTML = items.length > 1 ? items.map((item, i) => `
    <button type="button" data-media="${i}" class="${item.type === "video" ? "is-video" : ""}" aria-label="${i + 1} / ${items.length}">
      <img src="${esc(item.poster || item.src)}" alt="" loading="lazy">
    </button>`).join("") : "";
  showMedia(items, 0);
  $("#dialog-thumbs").onclick = event => {
    const btn = event.target.closest("[data-media]");
    if (btn) showMedia(items, Number(btn.dataset.media));
  };

  const icon = $("#dialog-icon");
  icon.hidden = !game.icon;
  if (game.icon) icon.src = game.icon;
  $("#dialog-badges").innerHTML = badges(game);
  $("#dialog-title").innerHTML = titleHTML(game);
  $("#dialog-tagline").textContent = pick(game.tagline);

  const facts = isPC(game)
    ? [...pick(game.facts)]
    : [t("players")(game.players), t("released")(formatDate(game.released))];
  facts.push(game.tags.map(tag => t("tags")[tag]).join(" · "));
  $("#dialog-facts").innerHTML = facts.filter(Boolean).map(f => `<li>${esc(f)}</li>`).join("");

  const highlights = pick(game.highlights) || [];
  $("#dialog-highlights").hidden = !highlights.length;
  $("#dialog-highlights").innerHTML = highlights.map(h => `<li>${esc(h)}</li>`).join("");
  $("#dialog-desc").textContent = pick(game.description);
  $("#dialog-actions").innerHTML = ctaButton(game);
}

function openDialog(id, fromHash) {
  const game = state.games.find(g => g.id === id);
  if (!game) return;
  state.dialogGame = game;
  fillDialog(game);
  const dialog = $("#game-dialog");
  if (!dialog.open) dialog.showModal();
  document.body.classList.add("dialog-open");
  $(".dialog-info").scrollTop = 0;
  $(".dialog-shell").scrollTop = 0;
  if (!fromHash) history.replaceState(null, "", `#game-${id}`);
}

function closeDialog() {
  const dialog = $("#game-dialog");
  if (dialog.open) dialog.close();
  document.body.classList.remove("dialog-open");
}

function openFromHash() {
  const hash = decodeURIComponent(location.hash.slice(1));
  if (hash.startsWith("game-")) openDialog(hash.slice(5), true);
}

function bindDialog() {
  const dialog = $("#game-dialog");
  document.addEventListener("click", event => {
    const opener = event.target.closest("[data-open]");
    if (opener) openDialog(opener.dataset.open);
    if (event.target.closest("[data-to-contact]") && dialog.open) {
      event.preventDefault();
      closeDialog();
      history.replaceState(null, "", "#contact");
      requestAnimationFrame(() => $("#contact").scrollIntoView({ behavior: reducedMotion.matches ? "auto" : "smooth" }));
    }
  });
  $("#dialog-close").addEventListener("click", closeDialog);
  dialog.addEventListener("click", event => { if (event.target === dialog) closeDialog(); });
  dialog.addEventListener("close", () => {
    if (dialog.open) return; // reopened before this queued close event ran
    state.dialogGame = null;
    document.body.classList.remove("dialog-open");
    $("#dialog-stage").innerHTML = "";
    if (location.hash.startsWith("#game-")) history.replaceState(null, "", location.pathname + location.search);
  });
  window.addEventListener("hashchange", openFromHash);
}

// ---------- Decoration & misc ----------

function makeRain() {
  if (reducedMotion.matches) return;
  $$(".rain").forEach(layer => {
    const count = layer.classList.contains("rain--studio") ? 26 : 18;
    layer.innerHTML = Array.from({ length: count }, (_, i) => {
      const left = (i * 37 + 11) % 100 + (i % 3) * 1.3;
      const duration = 2.4 + ((i * 7) % 10) / 4;
      const delay = -((i * 13) % 40) / 10;
      return `<i style="left:${left}%;animation-duration:${duration}s;animation-delay:${delay}s"></i>`;
    }).join("");
  });
}

function bindMisc() {
  $$(".lang-switch button").forEach(btn => btn.addEventListener("click", () => {
    state.lang = btn.dataset.lang;
    localStorage.setItem("slowrain-lang", state.lang);
    renderAll();
  }));
  $("#retry").addEventListener("click", loadGames);
  $("#year").textContent = new Date().getFullYear();
  const header = $(".site-header");
  const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 8);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

applyStaticText();
bindShowcase();
bindFilters();
bindDialog();
bindMisc();
makeRain();
loadGames();
