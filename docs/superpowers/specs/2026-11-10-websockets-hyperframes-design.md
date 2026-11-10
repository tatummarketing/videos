---
title: WebSockets Talking-Head HyperFrames Composition
date: 2026-11-10
status: approved
format: talking-head promo with narration-synced overlays
---

# WebSockets Talking-Head HyperFrames Composition

## Overview

A 48-second HyperFrames composition that overlays branded text, logos, and animated graphic cards on top of an existing talking-head video about Tatum WebSockets. The speaker (Mohit Thakkar, Solutions Engineer) narrates the value of Tatum WebSocket subscriptions while timed overlay cards reinforce each talking point on the right side of the frame.

**Source video:** `websockets.mp4` — 1920x1080, 25fps, 44.96s, H.264 + AAC stereo.
**Output:** `websockets-hyperframe/` project folder, rendered to MP4 via `npm run render`.
**Destination:** Multiple platforms (YouTube, LinkedIn, X, website) — design for mobile readability.

## Script (from speaker narration)

> Need real-time blockchain updates without constant polling? Tatum WebSocket subscriptions keep a persistent connection and push events to your application as they happen. Subscribe to blocks, transactions, accounts, or smart contract events, and receive updates in readable JSON. WebSockets are easy to integrate with browsers and popular programming languages, making them a great fit for wallets, dashboards, DeFi apps, and monitoring systems. Tatum supports WebSockets on Solana, Ethereum, Polygon, Arbitrum One, BSC, and Robinhood. For production, plan for dropped connections: reconnect, restore your subscriptions, and backfill missed events. Explore the Tatum WebSocket reference for your chain and start streaming real-time blockchain data.

Silence gaps detected at ~16.2s (0.6s) and ~26.2s (0.5s).

## Canvas & Base Layers

| Property | Value |
|----------|-------|
| Canvas | 1920x1080 |
| Frame rate | 25fps (matches source) |
| Root `data-duration` | 48 (44.96s video + ~3s outro) |
| Fonts | Poppins (400/500/600/700), Geist Mono (400/500/600) via Google Fonts |
| Animation library | GSAP 3.14.2 |

### Layer stack

| Layer | z-index | Description |
|-------|---------|-------------|
| Bed video | 0 | `<video>` full-frame, `muted`, `object-fit: cover`, `data-duration="44.96"` |
| Bed audio | — | `<audio>` same source file, `data-duration="44.96"` |
| Overlay cards | 10 | Right-side glass cards (all overlay beats) |
| Corner logo | 30 | Tatum logo top-left, persistent 0s–44.5s |
| Lower-third | 15 | Glass pill, bottom-left, 0.6s–4s |
| Intro title | 12 | Top-left text stack, 0.4s–4.2s |
| Dark outro | 40 | Full-bleed `#080a0d`, 45s–48s |

### Corner logo
- Asset: `tatum-logo-light.svg`
- Position: top-left, ~196px wide, ~32px inset (scaled up from 130px for 1080p canvas)
- Fades out at ~44.5s before the outro

### Lower-third
- Position: bottom-left (`left: 48px`, `bottom: 56px`)
- Glass pill: `rgba(8, 10, 13, 0.82)`, `backdrop-filter: blur(12px)`, `border-radius: 14px`
- Name: **Mohit Thakkar** — Poppins 600, 28px, `#ffffff`
- Role: **SOLUTIONS ENGINEER** — Geist Mono 500, 15px, `letter-spacing: 0.12em`, `#a19afe`
- Brand mark: `tatum-icon.png` (square icon, 36px)
- Animation: slide+fade in at ~0.6s (name → role → icon stagger), fade out at ~4s

### Intro title
- Position: top-left (`left: 56px`, `top: 100px`)
- Eyebrow: `TATUM WEBSOCKETS` — Geist Mono 500, 16px, white, uppercase, `letter-spacing: 0.18em`
- Headline: **Real-time blockchain** — Poppins 700, 44px, `#ffffff` (note: playbook default is `#000000` but the studio background is too dark for black text to read; using white instead)
- Subheader: **streaming, zero polling** — Poppins 600, 28px, `#a19afe` (purple-soft, to differentiate from headline)
- Animation: stagger in at ~0.4s (eyebrow → headline → subheader), exit up at ~4.2s

## Overlay Timeline Beats

All overlay cards share a common style:
- Width: ~400px
- Position: right side of frame (`right: 64px`, vertically centered)
- Background: `rgba(16, 17, 46, 0.92)`
- Border: `1px solid rgba(255, 255, 255, 0.12)`
- `backdrop-filter: blur(14px)`
- `border-radius: 16px`
- `box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.45)`
- Eyebrow labels: Geist Mono 13px, `#a19afe`, uppercase, letter-spaced
- Titles: Poppins 600, 26px, `#ffffff`
- No blur on speaker for any beat (all are partial overlays)

### Beat 2 — Persistent Connection (4.5s–9s)

**Narration:** "Tatum WebSocket subscriptions keep a persistent connection and push events to your application as they happen."

Card enters with scale+fade (spring in at 4.5s):
- Eyebrow: `WEBSOCKET SUBSCRIPTIONS`
- Title: **Persistent connection**
- Visual: WSS URL line (`wss://tatum.io/ws`) in Geist Mono 16px, cyan (`#3BC7FF`), with a pulsing green dot (`#34d399`) + `CONNECTED` status label (Geist Mono 14px, `#34d399`). Below: small animated event pills flowing downward (`NEW BLOCK`, `TX CONFIRMED`) in glass tags to represent push events.

### Beat 3 — Subscription Types (9s–16s)

**Narration:** "Subscribe to blocks, transactions, accounts, or smart contract events, and receive updates in readable JSON."

Card interior cross-fades (card shell stays, content swaps):
- Title: **Subscribe to everything**
- Four feature rows, waterfall in as speaker names them (~9.5s–14s):
  1. **Blocks** — cube icon, `rgba(79, 55, 253, 0.35)` icon bg
  2. **Transactions** — arrow icon
  3. **Accounts** — wallet icon
  4. **Smart Contract Events** — code/brackets icon
- Each row: icon (40x40 rounded square) + name (Poppins 600, 16px, white) + short desc (12.5px, `#9595a1`)
- Below rows: a small JSON snippet fades in on "readable JSON" (~14s):
  ```
  { "type": "newHeads", "chain": "ethereum" }
  ```
  Geist Mono 13px, `#9595a1`, glass background

Card exits at ~16s (fade+slide left) during the natural pause.

### Beat 4 — Use Cases & Integration (16.8s–22s)

**Narration:** "WebSockets are easy to integrate with browsers and popular programming languages, making them a great fit for wallets, dashboards, DeFi apps, and monitoring systems."

New card fades in after the ~16.8s pause:
- Eyebrow: `INTEGRATION`
- Title: **Easy integration**
- Four use-case pills appear as speaker names them, arranged in a 2x2 grid:
  1. `Wallets` — wallet icon
  2. `Dashboards` — chart icon
  3. `DeFi Apps` — layers icon
  4. `Monitoring` — bell/eye icon
- Each pill: glass rounded tag (`rgba(255,255,255,0.06)`, `border: 1px solid rgba(255,255,255,0.1)`, `border-radius: 12px`), icon + label, scale+fade in on the corresponding word

Card exits at ~22s.

### Beat 5 — Supported Chains (22s–27s)

**Narration:** "Tatum supports WebSockets on Solana, Ethereum, Polygon, Arbitrum One, BSC, and Robinhood."

New card:
- Eyebrow: `SUPPORTED CHAINS`
- Title: **Multi-chain support**
- Chain grid (2x3 or 3x2): each cell has the chain SVG logo (44px) + chain name (Poppins 500, 16px, white)
- Chains appear with a slight bounce as the speaker names each:
  - Solana (~23s)
  - Ethereum (~23.5s)
  - Polygon (~24s)
  - Arbitrum One (~24.5s)
  - BSC (~25s)
  - Robinhood (~25.5s)

Card exits at ~26.5s during the natural pause.

### Beat 6 — Production Best Practices (27s–38s)

**Narration:** "For production, plan for dropped connections: reconnect, restore your subscriptions, and backfill missed events."

New card:
- Eyebrow: `PRODUCTION TIPS`
- Title: **Connection resilience**
- Three checklist rows appearing in sequence (~28s–33s):
  1. Checkmark icon (`#2ccd9a`) + **Reconnect** on drop
  2. Checkmark icon + **Restore subscriptions** automatically
  3. Checkmark icon + **Backfill** missed events
- Each row: green check circle + text (Poppins 500, 16px, white) + description (12.5px, `#9595a1`)

Card exits at ~38s to return to a clean speaker frame for the CTA.

### Beat 7 — Clean CTA (38s–45s)

**Narration:** "Explore the Tatum WebSocket reference for your chain and start streaming real-time blockchain data."

No overlays. Speaker is clean, corner logo visible. The personal direct-to-camera CTA.

## Outro (45s–48s)

- Corner logo fades out at ~44.5s
- Speaker/bed fades to black over ~0.5s starting at ~44.5s
- At 45s: full-bleed `#080a0d` background activates
- Subtle grid pattern overlay (same as WaaS pricing outro):
  ```css
  background-image:
    linear-gradient(to right, rgba(255,255,255,0.035) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255,255,255,0.035) 1px, transparent 1px);
  background-size: 96px 96px;
  mask-image: radial-gradient(ellipse 80% 70% at 50% 50%, rgba(0,0,0,1) 0%, transparent 100%);
  ```
- **Tatum logo** (white, ~320px wide) scales in centered at ~45.2s
- **CTA line 1** (46s): "Stream real-time **blockchain data**" — Poppins 600, 34px, white; "blockchain data" in gradient accent (`white → #a19afe → #4f37fd` via `background-clip: text`)
- **CTA line 2** (47s, rotates in replacing line 1): `docs.tatum.io` — Poppins 600, 34px, white
- Hold until 48s

## Assets Required

| Asset | Source | Status |
|-------|--------|--------|
| `websockets.mp4` | Already in repo root | Available |
| `tatum-logo-light.svg` | Copy from `waas-pricing-hyperframe/assets/` | Available |
| `tatum-logo-white.svg` | Copy from `waas-pricing-hyperframe/assets/` | Available |
| `tatum-icon.png` | Tatum brand assets | Needs sourcing |
| `solana.svg` | `smart-wallets-launch/assets/chains/` | Available |
| `ethereum.svg` | `smart-wallets-launch/assets/chains/` | Available |
| `polygon.svg` | `smart-wallets-launch/assets/chains/` | Available |
| `arbitrum.svg` | `smart-wallets-launch/assets/chains/` | Available |
| `bnb-smart-chain.svg` | `smart-wallets-launch/assets/chains/` (BSC) | Available |
| Robinhood logo | Needs sourcing | Missing |

If `tatum-icon.png` is unavailable, fall back to `tatum-logo-white.svg` cropped/scaled in the lower-third brand slot. If Robinhood logo is unavailable, use a text-only pill in the chain grid.

## Project Structure

```
websockets-hyperframe/
  index.html            # main composition
  meta.json             # project metadata
  hyperframes.json      # registry config
  assets/
    websockets.mp4      # bed video (symlink or copy from repo root)
    tatum-logo-light.svg
    tatum-logo-white.svg
    tatum-icon.png
    chains/
      solana.svg
      ethereum.svg
      polygon.svg
      arbitrum.svg
      bnb-smart-chain.svg
```

## Technical Constraints

- All animations via GSAP `opacity`, `x`, `y`, `scale` — no `left`/`top`/layout properties
- Timeline registered on `window.__timelines['main']`, created paused
- No `Date.now()`, `Math.random()`, or network fetches in composition
- Clip elements need `class="clip"`, `data-start`, `data-duration`, `data-track-index`
- Outro clip CSS default: `visibility: hidden` (framework activates via `data-start`)
- After exit fades on clip boundaries, add hard kill (`tl.set(..., { visibility: 'hidden' })`)
- Force avatar visible at t=0: `tl.set('#avatar-video', { opacity: 1 }, 0)`
- `npm run check` must pass (0 errors) before considering done
- Timestamps are estimates — fine-tune by watching the video during implementation

## Out of Scope

- No blur/scrim on the speaker (all overlays are partial, right-side cards)
- No cursor demos or interactive UI mockups
- No background music — the video has its own audio track
- No captions/subtitles — this is an overlay composition, not a captioning project
