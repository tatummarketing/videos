# WebSockets HyperFrames Composition — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a HyperFrames composition that overlays narration-synced branded graphics on the `websockets.mp4` talking-head video.

**Architecture:** A single `index.html` composition with inline CSS and a GSAP timeline. The bed video plays full-frame while timed glass cards appear on the right side keyed to the speaker's narration. All timing is declared via `data-*` attributes; animation via a paused GSAP timeline registered on `window.__timelines['main']`.

**Tech Stack:** HyperFrames (`hyperframes@0.8.27`), GSAP 3.14.2, Google Fonts (Poppins + Geist Mono), inline SVG icons.

**Spec:** `docs/superpowers/specs/2026-11-10-websockets-hyperframes-design.md`

## Global Constraints

- Canvas: 1920×1080, 25fps
- Root `data-duration`: 48 (44.96s video + ~3s outro)
- Fonts: Poppins (400/500/600/700), Geist Mono (400/500/600) — loaded via Google Fonts CDN
- Animation: GSAP 3.14.2 — only animate `opacity`, `x`, `y`, `scale` (never `left`/`top`/layout props)
- Determinism: no `Date.now()`, `Math.random()`, or network fetches inside the composition
- Seek-safety: timeline must be paused; registered on `window.__timelines['main']`
- Every timed element needs `class="clip"` + `data-start` + `data-duration` + `data-track-index`
- Outro CSS default: `visibility: hidden` (framework activates it)
- Force avatar visible at t=0: `tl.set('#avatar-video', { opacity: 1 }, 0)`
- After exit fades on clip boundaries: add hard kill `tl.set(..., { visibility: 'hidden' })`
- `npm run check` must pass with 0 errors before done
- Timestamps are estimates — fine-tune during preview by watching the video

---

### Task 1: Project Scaffold + Assets

**Files:**
- Create: `websockets-hyperframe/meta.json`
- Create: `websockets-hyperframe/hyperframes.json`
- Create: `websockets-hyperframe/package.json`
- Create: `websockets-hyperframe/assets/` (directory with copied assets)

**Interfaces:**
- Consumes: nothing
- Produces: complete project directory with all asset files in place; config files matching the patterns used by `waas-pricing-hyperframe/` and `smart-wallets-launch/`

- [ ] **Step 1: Create the project directory and asset subdirectories**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos
mkdir -p websockets-hyperframe/assets/chains
```

- [ ] **Step 2: Copy assets from existing projects**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos

# Bed video — symlink to avoid duplicating 34MB
ln -s ../../websockets.mp4 websockets-hyperframe/assets/websockets.mp4

# Logos from waas-pricing-hyperframe
cp waas-pricing-hyperframe/assets/tatum-logo-light.svg websockets-hyperframe/assets/
cp waas-pricing-hyperframe/assets/tatum-logo-white.svg websockets-hyperframe/assets/

# Chain SVGs from smart-wallets-launch
cp smart-wallets-launch/assets/chains/solana.svg websockets-hyperframe/assets/chains/
cp smart-wallets-launch/assets/chains/ethereum.svg websockets-hyperframe/assets/chains/
cp smart-wallets-launch/assets/chains/polygon.svg websockets-hyperframe/assets/chains/
cp smart-wallets-launch/assets/chains/arbitrum.svg websockets-hyperframe/assets/chains/
cp smart-wallets-launch/assets/chains/bnb-smart-chain.svg websockets-hyperframe/assets/chains/
```

Note: `tatum-icon.png` is not available in the repo. Use `tatum-logo-white.svg` scaled to 36px in the lower-third brand slot as a fallback. Robinhood has no SVG logo — use a text-only pill in the chain grid.

- [ ] **Step 3: Create `meta.json`**

```json
{
  "id": "websockets-hyperframe",
  "name": "Tatum WebSockets",
  "createdAt": "2026-11-10T00:00:00.000Z"
}
```

- [ ] **Step 4: Create `hyperframes.json`**

```json
{
  "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
  "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
  "paths": {
    "blocks": "compositions",
    "components": "compositions/components",
    "assets": "assets"
  }
}
```

- [ ] **Step 5: Create `package.json`**

```json
{
  "name": "websockets-hyperframe",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "npx --yes hyperframes@0.8.27 preview",
    "check": "npx --yes hyperframes@0.8.27 check",
    "render": "npx --yes hyperframes@0.8.27 render",
    "publish": "npx --yes hyperframes@0.8.27 publish"
  }
}
```

- [ ] **Step 6: Verify the scaffold**

```bash
ls -R /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos/websockets-hyperframe/
# Expected:
# assets/chains/arbitrum.svg
# assets/chains/bnb-smart-chain.svg
# assets/chains/ethereum.svg
# assets/chains/polygon.svg
# assets/chains/solana.svg
# assets/tatum-logo-light.svg
# assets/tatum-logo-white.svg
# assets/websockets.mp4 (symlink)
# hyperframes.json
# meta.json
# package.json

# Verify symlink resolves
file websockets-hyperframe/assets/websockets.mp4
# Expected: ... symbolic link to ...
```

- [ ] **Step 7: Commit**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos
git add websockets-hyperframe/
git commit -m "scaffold: websockets-hyperframe project with assets and config"
```

---

### Task 2: Base Composition — Video, Corner Logo, Lower-Third, Intro Title

**Files:**
- Create: `websockets-hyperframe/index.html`

**Interfaces:**
- Consumes: assets from Task 1 (`assets/websockets.mp4`, `assets/tatum-logo-light.svg`, `assets/tatum-logo-white.svg`)
- Produces: a structurally valid HyperFrames composition with the bed video playing, corner logo visible, lower-third animating in/out (0.6s–4s), intro title animating in/out (0.4s–4.2s), and a placeholder outro shell. Timeline registered on `window.__timelines['main']`. All overlay card DOM is empty at this stage.

This task builds the full HTML document skeleton, all base-layer CSS, the video/audio clip elements, and the GSAP animations for the lower-third and intro title. It also includes the empty (hidden) outro `<section>` so the composition is structurally complete for linting.

- [ ] **Step 1: Create `index.html` with the DOCTYPE, head, fonts, GSAP, and reset CSS**

Write the opening of the file. Key values:
- `<meta name="viewport" content="width=1920, height=1080" />`
- Google Fonts: `Poppins:wght@400;500;600;700` and `Geist+Mono:wght@400;500;600`
- GSAP: `https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js`
- `html, body` and `#root`: all `width: 1920px; height: 1080px; overflow: hidden;`
- `background: #111` on `#root`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Tatum — WebSockets</title>
    <link
      href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body, #root {
        width: 1920px; height: 1080px; overflow: hidden;
        font-family: 'Poppins', sans-serif;
      }
      #root { position: relative; background: #111; }
```

- [ ] **Step 2: Add CSS for video layer, corner logo, lower-third, and intro title**

Append the following CSS inside the `<style>` block. These are the base layers — everything before the overlay cards.

```css
      /* ---------- video layer ---------- */
      .video-layer { position: absolute; inset: 0; z-index: 0; }
      .video-layer video {
        width: 1920px; height: 1080px;
        object-fit: cover; display: block;
      }

      /* ---------- corner logo ---------- */
      .corner-logo {
        position: absolute; top: 32px; left: 32px;
        z-index: 30; width: 196px; height: auto;
      }
      .corner-logo img { width: 100%; height: auto; display: block; }

      /* ---------- lower third ---------- */
      .lower-third {
        position: absolute; left: 48px; bottom: 56px; z-index: 15;
        display: flex; align-items: stretch;
        opacity: 0; visibility: hidden;
        border-radius: 14px; overflow: hidden;
        box-shadow: 0 12px 40px -10px rgba(0, 0, 0, 0.35);
      }
      .lt-body {
        padding: 16px 24px 16px 20px;
        background: rgba(8, 10, 13, 0.82);
        backdrop-filter: blur(12px);
      }
      .lt-name { font-size: 28px; font-weight: 600; color: #ffffff; white-space: nowrap; }
      .lt-role {
        margin-top: 3px; font-family: 'Geist Mono', monospace;
        font-size: 15px; font-weight: 500;
        letter-spacing: 0.12em; text-transform: uppercase; color: #a19afe;
      }
      .lt-logo {
        display: flex; align-items: center; padding: 0 22px 0 4px;
        background: rgba(8, 10, 13, 0.82); backdrop-filter: blur(12px);
      }
      .lt-logo img { width: 36px; height: auto; display: block; }

      /* ---------- intro title ---------- */
      .intro-text {
        position: absolute; left: 56px; top: 100px; z-index: 12;
        display: flex; flex-direction: column;
        opacity: 0; visibility: hidden;
      }
      .intro-eyebrow {
        font-family: 'Geist Mono', monospace; font-size: 16px; font-weight: 500;
        letter-spacing: 0.18em; text-transform: uppercase; color: #ffffff;
      }
      .intro-accent {
        margin-top: 8px; font-size: 44px; font-weight: 700;
        line-height: 1.06; letter-spacing: -0.02em; color: #ffffff;
      }
      .intro-product {
        margin-top: 4px; font-size: 28px; font-weight: 600;
        line-height: 1.15; color: #a19afe;
      }
```

- [ ] **Step 3: Add CSS for the overlay card shell (shared styles) and outro**

These styles are needed even though the overlay card HTML content comes in Task 3. Define the shared card container and the outro so the DOM is structurally complete.

```css
      /* ---------- overlay card (shared) ---------- */
      .overlay-panel {
        position: absolute; right: 64px; top: 50%; transform: translateY(-50%);
        z-index: 10; opacity: 0; visibility: hidden;
      }
      .card {
        width: 420px; padding: 26px 28px 28px;
        border-radius: 16px;
        background: rgba(16, 17, 46, 0.92);
        border: 1px solid rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(14px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.45);
      }
      .card-eyebrow {
        font-family: 'Geist Mono', monospace; font-size: 13px; font-weight: 500;
        letter-spacing: 0.18em; text-transform: uppercase; color: #a19afe;
      }
      .card-title {
        margin-top: 6px; font-size: 26px; font-weight: 600;
        line-height: 1.2; color: #ffffff;
      }
      .card-scene { margin-top: 20px; }

      /* --- feature rows (beats 3, 6) --- */
      .feature-list { display: flex; flex-direction: column; gap: 10px; }
      .feature-row {
        display: flex; align-items: center; gap: 14px;
        padding: 12px 14px; border-radius: 12px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        opacity: 0;
      }
      .feature-icon {
        width: 40px; height: 40px; flex-shrink: 0; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        background: rgba(79, 55, 253, 0.35); color: #d5d3fe;
      }
      .feature-icon svg { width: 22px; height: 22px; }
      .feature-name { font-size: 16px; font-weight: 600; color: #ffffff; }
      .feature-desc { margin-top: 1px; font-size: 12.5px; font-weight: 400; color: #9595a1; }

      /* --- use-case pills (beat 4) --- */
      .pill-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
      }
      .pill {
        display: flex; align-items: center; gap: 12px;
        padding: 14px 16px; border-radius: 12px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        opacity: 0;
      }
      .pill-icon {
        width: 36px; height: 36px; flex-shrink: 0; border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        background: rgba(79, 55, 253, 0.35); color: #d5d3fe;
      }
      .pill-icon svg { width: 20px; height: 20px; }
      .pill-label { font-size: 15px; font-weight: 600; color: #ffffff; }

      /* --- chain grid (beat 5) --- */
      .chain-grid {
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;
      }
      .chain-cell {
        display: flex; flex-direction: column; align-items: center; gap: 8px;
        padding: 14px 8px; border-radius: 12px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        opacity: 0;
      }
      .chain-cell img { width: 44px; height: 44px; }
      .chain-cell span { font-size: 13px; font-weight: 500; color: #ffffff; }

      /* --- checklist (beat 6) --- */
      .check-row {
        display: flex; align-items: center; gap: 14px;
        padding: 12px 14px; border-radius: 12px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        opacity: 0;
      }
      .check-icon {
        width: 36px; height: 36px; flex-shrink: 0; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        background: rgba(44, 205, 154, 0.2); color: #2ccd9a;
      }
      .check-icon svg { width: 20px; height: 20px; }
      .check-text { font-size: 16px; font-weight: 500; color: #ffffff; }
      .check-desc { margin-top: 1px; font-size: 12.5px; font-weight: 400; color: #9595a1; }

      /* --- connection visual (beat 2) --- */
      .ws-url {
        font-family: 'Geist Mono', monospace; font-size: 16px;
        font-weight: 500; color: #3BC7FF;
      }
      .ws-status {
        display: inline-flex; align-items: center; gap: 8px;
        margin-top: 8px;
      }
      .ws-dot {
        width: 10px; height: 10px; border-radius: 50%;
        background: #34d399;
      }
      .ws-status-label {
        font-family: 'Geist Mono', monospace; font-size: 14px;
        font-weight: 600; letter-spacing: 0.12em; color: #34d399;
      }
      .ws-events { margin-top: 14px; display: flex; flex-direction: column; gap: 8px; }
      .ws-event-pill {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 6px 14px; border-radius: 8px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-family: 'Geist Mono', monospace; font-size: 13px;
        font-weight: 500; color: #9595a1;
        opacity: 0;
      }
      .ws-event-pill .arrow { color: #3BC7FF; }

      /* --- JSON snippet (beat 3) --- */
      .json-snippet {
        margin-top: 14px; padding: 10px 14px; border-radius: 10px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        font-family: 'Geist Mono', monospace; font-size: 13px;
        color: #9595a1; white-space: pre; opacity: 0;
      }

      /* ---------- outro ---------- */
      .scene-end {
        position: absolute; inset: 0; z-index: 40;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        background: #080a0d; visibility: hidden;
      }
      .end-grid {
        position: absolute; inset: 0;
        background-image:
          linear-gradient(to right, rgba(255,255,255,0.035) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(255,255,255,0.035) 1px, transparent 1px);
        background-size: 96px 96px;
        mask-image: radial-gradient(ellipse 80% 70% at 50% 50%, rgba(0,0,0,1) 0%, transparent 100%);
      }
      .end-logo { position: relative; width: 320px; height: auto; opacity: 0; }
      .end-cta-stage {
        position: relative; margin-top: 36px; height: 50px;
        width: 100%; text-align: center;
      }
      .end-cta {
        position: absolute; left: 0; right: 0;
        font-size: 34px; font-weight: 600; line-height: 1.25;
        color: #ffffff; text-align: center; opacity: 0;
      }
      .end-cta .accent {
        background: linear-gradient(100deg, #ffffff 10%, #a19afe 55%, #4f37fd 95%);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent; color: transparent;
      }
    </style>
```

- [ ] **Step 4: Write the `<body>` HTML — video layer, corner logo, lower-third, intro title**

```html
  </head>
  <body>
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="48"
      data-width="1920"
      data-height="1080"
    >
      <!-- Bed video -->
      <div class="video-layer">
        <video
          id="avatar-video"
          class="clip"
          data-start="0"
          data-duration="44.96"
          data-track-index="0"
          src="assets/websockets.mp4"
          muted
          playsinline
          preload="auto"
        ></video>
      </div>
      <audio
        id="avatar-audio"
        class="clip"
        data-start="0"
        data-duration="44.96"
        data-track-index="1"
        src="assets/websockets.mp4"
      ></audio>

      <!-- Corner logo -->
      <div class="corner-logo">
        <img src="assets/tatum-logo-light.svg" alt="Tatum" />
      </div>

      <!-- Lower third -->
      <div class="lower-third" id="lowerThird">
        <div class="lt-body">
          <p class="lt-name">Mohit Thakkar</p>
          <p class="lt-role">Solutions Engineer</p>
        </div>
        <div class="lt-logo">
          <img src="assets/tatum-logo-white.svg" alt="Tatum" width="36" height="36" />
        </div>
      </div>

      <!-- Intro title -->
      <div class="intro-text" id="intro">
        <p class="intro-eyebrow">Tatum WebSockets</p>
        <p class="intro-accent">Real-time blockchain</p>
        <p class="intro-product">streaming, zero polling</p>
      </div>
```

- [ ] **Step 5: Write the `<body>` HTML — overlay card panels (beats 2–6)**

Each beat is a separate `.overlay-panel` container. All start hidden (`opacity: 0; visibility: hidden` from CSS). The GSAP timeline (Task 3) will animate them in/out.

```html
      <!-- Beat 2: Persistent Connection (4.5s–9s) -->
      <div class="overlay-panel" id="beat2">
        <div class="card">
          <p class="card-eyebrow">WebSocket Subscriptions</p>
          <h2 class="card-title">Persistent connection</h2>
          <div class="card-scene">
            <p class="ws-url">wss://tatum.io/ws</p>
            <div class="ws-status">
              <span class="ws-dot"></span>
              <span class="ws-status-label">CONNECTED</span>
            </div>
            <div class="ws-events">
              <span class="ws-event-pill ws-event-1"><span class="arrow">→</span> NEW BLOCK</span>
              <span class="ws-event-pill ws-event-2"><span class="arrow">→</span> TX CONFIRMED</span>
              <span class="ws-event-pill ws-event-3"><span class="arrow">→</span> LOG EVENT</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Beat 3: Subscription Types (9s–16s) -->
      <div class="overlay-panel" id="beat3">
        <div class="card">
          <p class="card-eyebrow">Event Types</p>
          <h2 class="card-title">Subscribe to everything</h2>
          <div class="card-scene">
            <div class="feature-list">
              <div class="feature-row" id="row-blocks">
                <span class="feature-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" stroke-linejoin="round" />
                    <path d="M3.27 6.96L12 12.01l8.73-5.05M12 22.08V12" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
                <div>
                  <p class="feature-name">Blocks</p>
                  <p class="feature-desc">New block headers as they're mined</p>
                </div>
              </div>
              <div class="feature-row" id="row-tx">
                <span class="feature-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path d="M5 12h14M12 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
                <div>
                  <p class="feature-name">Transactions</p>
                  <p class="feature-desc">Pending and confirmed txs</p>
                </div>
              </div>
              <div class="feature-row" id="row-accounts">
                <span class="feature-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path d="M19 7V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v1" stroke-linecap="round" />
                    <path d="M5 7h14v12a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V7z" stroke-linejoin="round" />
                    <path d="M9 11h6" stroke-linecap="round" />
                  </svg>
                </span>
                <div>
                  <p class="feature-name">Accounts</p>
                  <p class="feature-desc">Balance and state changes</p>
                </div>
              </div>
              <div class="feature-row" id="row-contracts">
                <span class="feature-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path d="M16 18l6-6-6-6M8 6l-6 6 6 6" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
                <div>
                  <p class="feature-name">Smart Contract Events</p>
                  <p class="feature-desc">Logs and emitted events</p>
                </div>
              </div>
            </div>
            <div class="json-snippet" id="jsonSnippet">{ "type": "newHeads", "chain": "ethereum" }</div>
          </div>
        </div>
      </div>

      <!-- Beat 4: Use Cases (16.8s–22s) -->
      <div class="overlay-panel" id="beat4">
        <div class="card">
          <p class="card-eyebrow">Integration</p>
          <h2 class="card-title">Easy integration</h2>
          <div class="card-scene">
            <div class="pill-grid">
              <div class="pill" id="pill-wallets">
                <span class="pill-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path d="M19 7V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v1" stroke-linecap="round" />
                    <path d="M5 7h14v12a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V7z" stroke-linejoin="round" />
                    <path d="M9 11h6" stroke-linecap="round" />
                  </svg>
                </span>
                <span class="pill-label">Wallets</span>
              </div>
              <div class="pill" id="pill-dashboards">
                <span class="pill-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path d="M4 18V8m5.5 10V6M15 18v-7m5 7V4" stroke-linecap="round" />
                  </svg>
                </span>
                <span class="pill-label">Dashboards</span>
              </div>
              <div class="pill" id="pill-defi">
                <span class="pill-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
                <span class="pill-label">DeFi Apps</span>
              </div>
              <div class="pill" id="pill-monitoring">
                <span class="pill-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                </span>
                <span class="pill-label">Monitoring</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Beat 5: Supported Chains (22s–27s) -->
      <div class="overlay-panel" id="beat5">
        <div class="card">
          <p class="card-eyebrow">Supported Chains</p>
          <h2 class="card-title">Multi-chain support</h2>
          <div class="card-scene">
            <div class="chain-grid">
              <div class="chain-cell" id="chain-solana">
                <img src="assets/chains/solana.svg" alt="Solana" />
                <span>Solana</span>
              </div>
              <div class="chain-cell" id="chain-ethereum">
                <img src="assets/chains/ethereum.svg" alt="Ethereum" />
                <span>Ethereum</span>
              </div>
              <div class="chain-cell" id="chain-polygon">
                <img src="assets/chains/polygon.svg" alt="Polygon" />
                <span>Polygon</span>
              </div>
              <div class="chain-cell" id="chain-arbitrum">
                <img src="assets/chains/arbitrum.svg" alt="Arbitrum" />
                <span>Arbitrum</span>
              </div>
              <div class="chain-cell" id="chain-bsc">
                <img src="assets/chains/bnb-smart-chain.svg" alt="BSC" />
                <span>BSC</span>
              </div>
              <div class="chain-cell" id="chain-robinhood">
                <span style="font-size: 32px; line-height: 44px;">🪶</span>
                <span>Robinhood</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Beat 6: Production Tips (27s–38s) -->
      <div class="overlay-panel" id="beat6">
        <div class="card">
          <p class="card-eyebrow">Production Tips</p>
          <h2 class="card-title">Connection resilience</h2>
          <div class="card-scene">
            <div class="feature-list">
              <div class="check-row" id="check-reconnect">
                <span class="check-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M20 6L9 17l-5-5" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
                <div>
                  <p class="check-text">Reconnect on drop</p>
                  <p class="check-desc">Auto-retry with exponential backoff</p>
                </div>
              </div>
              <div class="check-row" id="check-restore">
                <span class="check-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M20 6L9 17l-5-5" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
                <div>
                  <p class="check-text">Restore subscriptions</p>
                  <p class="check-desc">Re-subscribe after reconnection</p>
                </div>
              </div>
              <div class="check-row" id="check-backfill">
                <span class="check-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M20 6L9 17l-5-5" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
                <div>
                  <p class="check-text">Backfill missed events</p>
                  <p class="check-desc">Replay gaps via REST fallback</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Outro -->
      <section id="end" class="clip scene-end" data-start="45" data-duration="3" data-track-index="3">
        <div class="end-grid" aria-hidden="true"></div>
        <img class="end-logo" src="assets/tatum-logo-white.svg" alt="Tatum" />
        <div class="end-cta-stage">
          <p class="end-cta end-cta-1">Stream real-time <span class="accent">blockchain data</span></p>
          <p class="end-cta end-cta-2">docs.tatum.io</p>
        </div>
      </section>
    </div>
```

- [ ] **Step 6: Write the `<script>` — timeline setup + lower-third + intro title animations**

```html
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });

      /* ---- element refs ---- */
      const lowerThird = document.getElementById('lowerThird');
      const introText = document.getElementById('intro');
      const cornerLogo = document.querySelector('.corner-logo');
      const videoLayer = document.querySelector('.video-layer');
      const sceneEnd = document.getElementById('end');

      /* ---- initial states ---- */
      tl.set('#avatar-video', { opacity: 1 }, 0);
      gsap.set(lowerThird, { opacity: 0, visibility: 'hidden', x: -36 });
      gsap.set('.lt-name, .lt-role', { opacity: 0, x: -14 });
      gsap.set('.lt-logo img', { opacity: 0, x: -10 });
      gsap.set(introText, { opacity: 0, visibility: 'hidden' });
      gsap.set('.intro-eyebrow, .intro-accent, .intro-product', { opacity: 0, y: 20 });

      /* ---- lower third: in at 0.6s, out at 4s ---- */
      tl.set(lowerThird, { visibility: 'visible' }, 0.6);
      tl.to(lowerThird, { opacity: 1, x: 0, duration: 0.42, ease: 'power3.out' }, 0.6);
      tl.to('.lt-name', { opacity: 1, x: 0, duration: 0.32, ease: 'power2.out' }, 0.8);
      tl.to('.lt-role', { opacity: 1, x: 0, duration: 0.32, ease: 'power2.out' }, 0.95);
      tl.to('.lt-logo img', { opacity: 1, x: 0, duration: 0.32, ease: 'power2.out' }, 1.1);
      tl.to(lowerThird, { opacity: 0, x: -28, duration: 0.38, ease: 'power2.in' }, 4.0);
      tl.set(lowerThird, { visibility: 'hidden' }, 4.38);

      /* ---- intro title: in at 0.4s, out at 4.2s ---- */
      tl.set(introText, { visibility: 'visible', opacity: 1 }, 0.4);
      tl.to('.intro-eyebrow', { opacity: 1, y: 0, duration: 0.2, ease: 'power2.out' }, 0.45);
      tl.to('.intro-accent', { opacity: 1, y: 0, duration: 0.24, ease: 'power3.out' }, 1.3);
      tl.to('.intro-product', { opacity: 1, y: 0, duration: 0.22, ease: 'power3.out' }, 2.5);
      tl.to(introText, { opacity: 0, y: -10, duration: 0.32, ease: 'power2.in' }, 4.2);
      tl.set(introText, { visibility: 'hidden' }, 4.52);

      /* ---- overlay beats will be added in Task 3 ---- */

      /* ---- placeholder end so timeline has full duration ---- */
      tl.to({}, { duration: 0.1 }, 47.9);

      window.__timelines['main'] = tl;
    </script>
  </body>
</html>
```

- [ ] **Step 7: Run lint to verify structural validity**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos/websockets-hyperframe
npx --yes hyperframes@0.8.27 lint --verbose
```

Expected: 0 errors (warnings about Google Fonts are OK). If errors appear about missing `class="clip"` or `data-*` attributes, fix them before proceeding.

- [ ] **Step 8: Commit**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos
git add websockets-hyperframe/index.html
git commit -m "feat: base composition with video, logo, lower-third, intro title, and full DOM structure"
```

---

### Task 3: GSAP Timeline — Overlay Card Beats 2–6

**Files:**
- Modify: `websockets-hyperframe/index.html` (the `<script>` block — add overlay beat animations)

**Interfaces:**
- Consumes: DOM elements from Task 2 (`#beat2` through `#beat6`, all `.feature-row`, `.pill`, `.chain-cell`, `.check-row` elements, `#jsonSnippet`, `.ws-event-pill`)
- Produces: complete GSAP timeline covering beats 2–6 with all enter/exit animations timed to the narration

All timings below are estimates based on the 45s narration. The `/* ---- overlay beats will be added in Task 3 ---- */` comment and the placeholder duration line in Task 2's script should be **replaced** with this code.

- [ ] **Step 1: Add initial states for all overlay panels**

Insert after the intro title initial states (after `gsap.set('.intro-eyebrow, .intro-accent, .intro-product', { opacity: 0, y: 20 });`):

```js
      /* ---- overlay panel initial states ---- */
      gsap.set('#beat2, #beat3, #beat4, #beat5, #beat6', { opacity: 0, visibility: 'hidden', scale: 0.96 });
      gsap.set('.end-logo', { opacity: 0, scale: 0.92 });
      gsap.set('.end-cta', { opacity: 0, y: 16 });
```

- [ ] **Step 2: Write Beat 2 — Persistent Connection (4.5s–9s)**

Replace the `/* ---- overlay beats will be added in Task 3 ---- */` comment with:

```js
      /* ==== BEAT 2: Persistent Connection (4.5s–9s) ==== */
      tl.set('#beat2', { visibility: 'visible' }, 4.5);
      tl.to('#beat2', { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(1.2)' }, 4.5);
      tl.to('.ws-event-1', { opacity: 1, x: 0, duration: 0.3, ease: 'power2.out' }, 5.5);
      tl.to('.ws-event-2', { opacity: 1, x: 0, duration: 0.3, ease: 'power2.out' }, 6.5);
      tl.to('.ws-event-3', { opacity: 1, x: 0, duration: 0.3, ease: 'power2.out' }, 7.5);
      /* exit */
      tl.to('#beat2', { opacity: 0, scale: 0.96, duration: 0.35, ease: 'power2.in' }, 8.6);
      tl.set('#beat2', { visibility: 'hidden' }, 8.95);
```

- [ ] **Step 3: Write Beat 3 — Subscription Types (9s–16s)**

```js
      /* ==== BEAT 3: Subscription Types (9s–16s) ==== */
      tl.set('#beat3', { visibility: 'visible' }, 9.0);
      tl.to('#beat3', { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(1.2)' }, 9.0);
      /* feature rows waterfall in as speaker names them */
      tl.to('#row-blocks', { opacity: 1, x: 0, duration: 0.32, ease: 'power2.out' }, 9.8);
      tl.to('#row-tx', { opacity: 1, x: 0, duration: 0.32, ease: 'power2.out' }, 10.8);
      tl.to('#row-accounts', { opacity: 1, x: 0, duration: 0.32, ease: 'power2.out' }, 11.6);
      tl.to('#row-contracts', { opacity: 1, x: 0, duration: 0.32, ease: 'power2.out' }, 12.5);
      /* JSON snippet on "readable JSON" */
      tl.to('#jsonSnippet', { opacity: 1, duration: 0.3, ease: 'power2.out' }, 14.0);
      /* exit during natural pause at ~16.2s */
      tl.to('#beat3', { opacity: 0, x: -20, duration: 0.35, ease: 'power2.in' }, 15.8);
      tl.set('#beat3', { visibility: 'hidden' }, 16.15);
```

- [ ] **Step 4: Write Beat 4 — Use Cases (16.8s–22s)**

```js
      /* ==== BEAT 4: Use Cases & Integration (16.8s–22s) ==== */
      tl.set('#beat4', { visibility: 'visible' }, 16.8);
      tl.to('#beat4', { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(1.2)' }, 16.8);
      /* pills appear as speaker names each use case */
      tl.to('#pill-wallets', { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(1.4)' }, 18.5);
      tl.to('#pill-dashboards', { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(1.4)' }, 19.2);
      tl.to('#pill-defi', { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(1.4)' }, 19.8);
      tl.to('#pill-monitoring', { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(1.4)' }, 20.5);
      /* exit */
      tl.to('#beat4', { opacity: 0, scale: 0.96, duration: 0.35, ease: 'power2.in' }, 21.6);
      tl.set('#beat4', { visibility: 'hidden' }, 21.95);
```

- [ ] **Step 5: Write Beat 5 — Supported Chains (22s–27s)**

```js
      /* ==== BEAT 5: Supported Chains (22s–27s) ==== */
      tl.set('#beat5', { visibility: 'visible' }, 22.0);
      tl.to('#beat5', { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(1.2)' }, 22.0);
      /* chains appear as speaker names each */
      tl.to('#chain-solana', { opacity: 1, scale: 1, duration: 0.28, ease: 'back.out(1.6)' }, 23.0);
      tl.to('#chain-ethereum', { opacity: 1, scale: 1, duration: 0.28, ease: 'back.out(1.6)' }, 23.5);
      tl.to('#chain-polygon', { opacity: 1, scale: 1, duration: 0.28, ease: 'back.out(1.6)' }, 24.0);
      tl.to('#chain-arbitrum', { opacity: 1, scale: 1, duration: 0.28, ease: 'back.out(1.6)' }, 24.5);
      tl.to('#chain-bsc', { opacity: 1, scale: 1, duration: 0.28, ease: 'back.out(1.6)' }, 25.0);
      tl.to('#chain-robinhood', { opacity: 1, scale: 1, duration: 0.28, ease: 'back.out(1.6)' }, 25.5);
      /* exit during natural pause at ~26.2s */
      tl.to('#beat5', { opacity: 0, scale: 0.96, duration: 0.35, ease: 'power2.in' }, 26.2);
      tl.set('#beat5', { visibility: 'hidden' }, 26.55);
```

- [ ] **Step 6: Write Beat 6 — Production Tips (27s–38s)**

```js
      /* ==== BEAT 6: Production Tips (27s–38s) ==== */
      tl.set('#beat6', { visibility: 'visible' }, 27.0);
      tl.to('#beat6', { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(1.2)' }, 27.0);
      /* checklist rows stagger in */
      tl.to('#check-reconnect', { opacity: 1, x: 0, duration: 0.32, ease: 'power2.out' }, 28.5);
      tl.to('#check-restore', { opacity: 1, x: 0, duration: 0.32, ease: 'power2.out' }, 30.0);
      tl.to('#check-backfill', { opacity: 1, x: 0, duration: 0.32, ease: 'power2.out' }, 31.5);
      /* exit — return to clean speaker for CTA */
      tl.to('#beat6', { opacity: 0, scale: 0.96, duration: 0.4, ease: 'power2.in' }, 37.0);
      tl.set('#beat6', { visibility: 'hidden' }, 37.4);
```

- [ ] **Step 7: Add initial x-offset for feature rows and check rows**

These rows slide in from the right. Add to the initial states block (after the overlay panel initial states added in Step 1):

```js
      gsap.set('.feature-row, .check-row', { x: 22 });
      gsap.set('.pill', { scale: 0.85 });
      gsap.set('.chain-cell', { scale: 0.85 });
      gsap.set('.ws-event-pill', { x: -10 });
```

- [ ] **Step 8: Run lint**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos/websockets-hyperframe
npx --yes hyperframes@0.8.27 lint --verbose
```

Expected: 0 errors.

- [ ] **Step 9: Commit**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos
git add websockets-hyperframe/index.html
git commit -m "feat: overlay card beats 2-6 with narration-synced GSAP animations"
```

---

### Task 4: GSAP Timeline — Outro + Final Polish

**Files:**
- Modify: `websockets-hyperframe/index.html` (the `<script>` block — add outro animations, remove placeholder duration)

**Interfaces:**
- Consumes: DOM from Task 2 (`.corner-logo`, `.video-layer`, `#end`, `.end-logo`, `.end-cta-1`, `.end-cta-2`), timeline from Tasks 2+3
- Produces: complete GSAP timeline covering the full 0–48s composition including the outro end card with rotating CTA lines

- [ ] **Step 1: Replace the placeholder duration line with the outro animations**

Remove this line from the script:
```js
      /* ---- placeholder end so timeline has full duration ---- */
      tl.to({}, { duration: 0.1 }, 47.9);
```

Replace with:

```js
      /* ==== OUTRO (44.5s–48s) ==== */
      /* fade corner logo and speaker */
      tl.to(cornerLogo, { opacity: 0, duration: 0.3, ease: 'power2.in' }, 44.5);
      tl.to(videoLayer, { opacity: 0, duration: 0.5, ease: 'power2.in' }, 44.5);

      /* end card appears */
      tl.set(sceneEnd, { visibility: 'visible', opacity: 1 }, 45.0);
      tl.to('.end-logo', { opacity: 1, scale: 1, duration: 0.46, ease: 'power2.out' }, 45.2);

      /* CTA line 1 in */
      tl.to('.end-cta-1', { opacity: 1, y: 0, duration: 0.38, ease: 'power2.out' }, 45.8);
      /* CTA line 1 out, line 2 in (rotate) */
      tl.to('.end-cta-1', { opacity: 0, y: -12, duration: 0.28, ease: 'power2.in' }, 46.8);
      tl.to('.end-cta-2', { opacity: 1, y: 0, duration: 0.32, ease: 'power2.out' }, 47.0);
      /* hold until 48s */
      tl.to({}, { duration: 0.8 }, 47.2);
```

- [ ] **Step 2: Add the browser auto-play guard**

Add this line right before `window.__timelines['main'] = tl;`:

```js
      if (!/[?&]render=1/.test(location.search)) tl.play(0);
```

This lets the composition play automatically in browser preview, but the HyperFrames renderer drives seeks itself via `?render=1`.

- [ ] **Step 3: Run the full check suite**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos/websockets-hyperframe
npx --yes hyperframes@0.8.27 check
```

Expected: 0 errors. Fix any issues that arise (common: missing hard kills after fades, clip boundary warnings). Warnings about Google Fonts or large file sizes are acceptable.

- [ ] **Step 4: Preview and visually verify**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos/websockets-hyperframe
npx --yes hyperframes@0.8.27 preview --background
npx --yes hyperframes@0.8.27 preview --status
```

Visual checks:
1. Frame 0: speaker visible, no black frame
2. 0.6s: lower-third slides in with "Mohit Thakkar / Solutions Engineer"
3. ~4s: lower-third exits, intro title exits
4. ~4.5s: first card (persistent connection) appears right-side
5. Cards cycle through beats 2–6 without overlapping
6. ~38s: all cards gone, clean speaker for CTA
7. ~45s: dark outro with logo → CTA line 1 → CTA line 2

Stop the preview after verification:
```bash
npx --yes hyperframes@0.8.27 preview --stop
```

- [ ] **Step 5: Commit**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos
git add websockets-hyperframe/index.html
git commit -m "feat: outro animations and complete 48s timeline"
```

---

### Task 5: Timestamp Fine-Tuning + Render

**Files:**
- Modify: `websockets-hyperframe/index.html` (adjust GSAP timing values to match actual narration)

**Interfaces:**
- Consumes: complete composition from Task 4
- Produces: final `index.html` with accurate timestamps and a rendered MP4

This task requires watching the video in the preview and adjusting the timestamp values in the GSAP timeline so each overlay card entrance lands on the correct spoken word. The timestamps in Tasks 2–4 are estimates.

- [ ] **Step 1: Start preview and note actual word timings**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos/websockets-hyperframe
npx --yes hyperframes@0.8.27 preview --background
```

Open the preview URL in a browser. Play through the video and note the actual second when the speaker says each key word/phrase:

| Phrase | Estimated | Actual |
|--------|-----------|--------|
| "Tatum WebSocket subscriptions" | 3s | ___ |
| "persistent connection" | 5s | ___ |
| "blocks" | 9.8s | ___ |
| "transactions" | 10.8s | ___ |
| "accounts" | 11.6s | ___ |
| "smart contract events" | 12.5s | ___ |
| "readable JSON" | 14s | ___ |
| "wallets" | 18.5s | ___ |
| "dashboards" | 19.2s | ___ |
| "DeFi apps" | 19.8s | ___ |
| "monitoring" | 20.5s | ___ |
| "Solana" | 23s | ___ |
| "Ethereum" | 23.5s | ___ |
| "Polygon" | 24s | ___ |
| "Arbitrum One" | 24.5s | ___ |
| "BSC" | 25s | ___ |
| "Robinhood" | 25.5s | ___ |
| "reconnect" | 28.5s | ___ |
| "restore your subscriptions" | 30s | ___ |
| "backfill" | 31.5s | ___ |
| speaker finishes talking | 44s | ___ |

- [ ] **Step 2: Update timestamp values in index.html**

Edit the GSAP timeline in the `<script>` section, replacing the estimated timestamps with the actual values noted in Step 1. Each `tl.to(...)` and `tl.set(...)` call has a position parameter (the last argument) — update those numbers.

- [ ] **Step 3: Re-run check**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos/websockets-hyperframe
npx --yes hyperframes@0.8.27 check
```

- [ ] **Step 4: Preview again and verify sync**

Watch through once more in the browser to confirm overlays land on their words.

```bash
npx --yes hyperframes@0.8.27 preview --stop
```

- [ ] **Step 5: Render draft MP4**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos/websockets-hyperframe
mkdir -p renders
npx --yes hyperframes@0.8.27 render --quality draft --output renders/websockets-draft.mp4
```

Verify the output:
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 renders/websockets-draft.mp4
# Expected: ~48.0 (within 0.5s)
```

- [ ] **Step 6: Render high-quality final MP4**

```bash
npx --yes hyperframes@0.8.27 render --quality high --output renders/websockets-final.mp4
```

Verify:
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 renders/websockets-final.mp4
ls -lh renders/websockets-final.mp4
```

- [ ] **Step 7: Commit**

```bash
cd /Users/mohitthakkar/Desktop/Tatum/Tatum-Projects/videos
git add websockets-hyperframe/index.html
git commit -m "feat: fine-tuned timestamps and rendered final MP4"
```

Note: do NOT commit the renders/ directory to git (large binary files). Add `renders/` to `.gitignore` if one exists.
