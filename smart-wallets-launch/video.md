# Tatum product videos (HyperFrames) — agent guide

Self-contained playbook for building Tatum product videos with **HyperFrames**.  
Anyone with this file, brand assets, bed media, and a brief should be able to produce a matching video without access to prior project folders.

Two house formats:

| Format | Default canvas | Bed | Typical use |
|--------|----------------|-----|-------------|
| **Talking-head promo** | **1280×720** | Camera / avatar | Feature explainers with UI overlays |
| **AI plate + overlays** | **1920×1080** | AI / cinematic journey plate | Product launch trailers, capability announcements |

Do not invent alternate formats (square, UI-only, 3D) unless the brief explicitly asks.

The talking-head rules fill most of this doc. **AI plate + overlays** are covered in [their own section](#ai-plate--hyperframes-overlays-launch-trailers) — use that section when the bed is generative footage and HyperFrames owns all readable graphics.

---

## What HyperFrames is

[HyperFrames](https://hyperframes.heygen.com/introduction) renders **video from HTML**.

- A **composition** is an HTML file.
- Timing is declared with **`data-*` attributes** on the DOM.
- Motion is driven by a **seekable** animation runtime (we use **GSAP**).
- The CLI captures frames by seeking the timeline (not by recording a live playhead), so everything must be **deterministic** and **seek-safe**.

Docs index for agents: https://hyperframes.heygen.com/llms.txt  
CLI topic help: `npx hyperframes docs <topic>`  
Topics include: `data-attributes`, `gsap`, `compositions`, `rendering`, `examples`, `troubleshooting`.

### Requirements

- **Node.js 22+** (prefer **24** if your environment uses it)
- **FFmpeg** on `PATH`
- Network for first-time `npx` / font fetch (fonts are cached after compile)

Install agent skills once per machine (recommended):

```bash
npx hyperframes skills
# or: npx skills add heygen-com/hyperframes
```

---

## Project layout

**New videos live in their own Cursor project**, not nested in this playbook or an older workspace. That keeps each piece visible under **Today** in Recents instead of collapsing into Older.

```text
/Users/ted/Projects/tatum-videos/<slug>/
  index.html          # main composition (required)
  hyperframes.json    # registry / paths config
  meta.json           # optional project metadata
  assets/             # bed video, logos, icons
  renders/<slug>.mp4  # named output (not only video.mp4)
  compositions/       # optional sub-compositions
```

After creating the folder, move the agent workspace root there. Use this playbook (`video.md`) for brand and format; do not scaffold new work under `video/videos/`.

Minimal `hyperframes.json`:

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

Scaffold with the CLI if you prefer:

```bash
npx hyperframes init my-feature-hyperframe --non-interactive --example=blank
```

Or create the folder + `index.html` by hand using the skeleton later in this doc.

---

## Development loop

Work from the project directory. After every meaningful HTML/CSS/JS change:

```bash
# 1) Fast structural validation
npx hyperframes lint

# 2) Final gate (re-runs lint + browser layout/contrast/runtime checks)
npx hyperframes check

# 3) Optional: Studio preview (share URL with human for review)
npx hyperframes preview

# 4) Render only after checks pass (and ideally after human preview)
npx hyperframes render --quality draft --output renders/draft.mp4    # iteration
npx hyperframes render --quality high --output renders/final.mp4     # delivery
```

Rules:

- Fix all **lint errors** before considering the work done. Warnings are often OK (large file, Google Fonts).
- Prefer `check` as the gate before preview/render (`check` already includes lint).
- Do not skip render verification: confirm the file exists, size > 0, duration matches `data-duration`.

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 renders/final.mp4
```

Useful extras:

```bash
npx hyperframes doctor --json          # environment health
npx hyperframes snapshot --at 1,5,9    # frame grabs for debugging
npx hyperframes docs gsap
```

---

## Composition contract (must follow)

### Root

```html
<div
  id="root"
  data-composition-id="main"
  data-start="0"
  data-duration="25"
  data-width="1280"
  data-height="720"
>
  …
</div>
```

- `data-width` / `data-height` must match the CSS size of `html, body, #root`.
- `data-duration` is the **full** piece including outro (often longer than the bed video).

### Timed media / end cards = clips

Any element with its own time window needs:

- `class="clip"`
- `data-start`
- `data-duration`
- `data-track-index` (unique track per overlapping layer)

HyperFrames toggles **visibility** of clips from those attributes. **Do not** GSAP-animate `visibility` or `display` on clip roots — animate **children** instead.

### Video + audio

Bed footage:

```html
<video
  id="avatar-video"
  class="clip"
  src="assets/avatar.mov"
  muted
  playsinline
  preload="auto"
  data-start="0"
  data-duration="22"
  data-track-index="0"
></video>
<audio
  id="avatar-audio"
  class="clip"
  src="assets/avatar.mov"
  data-start="0"
  data-duration="22"
  data-track-index="1"
></audio>
```

- Video element is **`muted`**; audio is a **separate** clip (same source file is fine).
- Match video/audio `data-duration` to the bed length. Outro lives on the root duration beyond that.

### GSAP timeline registration

```js
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });

// … build tl …

window.__timelines['main'] = tl; // key === data-composition-id

// Preview in browser; HyperFrames render uses ?render=1 and drives seeks itself
if (!/[?&]render=1/.test(location.search)) {
  tl.play(0);
}
```

### Determinism & seek-safety

Because the renderer seeks by frame:

- No `Date.now()`, `Math.random()`, or network fetches in the composition.
- Prefer animating **`transform` (`x`/`y`/`scale`) and `opacity`**, not `left`/`top`/layout props that snap to device pixels.
- Avoid rewriting DOM with `innerHTML` inside `tl.call` when seeking backward must restore state — use two pre-rendered states and toggle them.
- After an exit fade that ends on a clip boundary, add a hard kill if lint asks:

  ```js
  tl.to('#panel', { opacity: 0, duration: 0.35 }, 18.6);
  tl.set('#panel', { opacity: 0, visibility: 'hidden' }, 19.0);
  ```

- If you fade the avatar out for the outro, force it visible at `t=0`:

  ```js
  tl.set('#avatar-video', { opacity: 1 }, 0);
  ```

---

## Tatum visual system

### Brand tokens

| Token | Value |
|-------|--------|
| Purple | `#4f37fd` |
| Purple soft | `#a19afe` |
| Purple ink | `#402dce` |
| Outro / lower-third glass | `#080a0d` / `rgba(8, 10, 13, 0.82)` |
| Headline (on camera) | `#000000` |
| Subheader / eyebrow (on camera) | `#ffffff` |

### Typography

- **Poppins** — names, headlines, UI mock labels  
- **Geist Mono** — eyebrows, roles, chips, monospace UI bits  

Load via Google Fonts in the composition (HyperFrames compiles/caches them on render), or self-host with `@font-face` if offline builds matter.

### Assets (ship inside `assets/`)

| File | Use |
|------|-----|
| `tatum-logo-light.svg` | Top-left corner logo on the talking-head |
| `tatum-logo-white.svg` | Outro |
| `tatum-icon.png` | Lower-third brand mark (square icon — **not** the word “Tatum”) |
| `avatar.mov` / `.mp4` | Talking-head bed |

Include these files in the project you hand off. This guide assumes they exist under `assets/`.

### Corner logo

- Position: top-left (~28–32px inset), ~130px wide.
- z-index **below** full dashboard overlays so the product UI covers the logo when the board is up.
- Fade out immediately before the outro.

### Intro titles (on talking head)

Top-left stack (~`left: 56px`, `top: 100px`):

| Layer | Color | Style |
|-------|--------|--------|
| Eyebrow (small label) | **White** | Geist Mono, uppercase, letter-spacing ~0.18em |
| **Headline** | **Black** | Poppins 700, ~44px |
| **Subheader** | **White** | Poppins 600, ~28–32px |

Break long headline/subheader onto **two lines** (`<br />`) so they don’t collide with the speaker’s face.

Stagger in (~0.5s → ~2.5s), out before the first product overlay. Prefer positive, product-led copy.

### Lower thirds

Bottom-left glass pill (~`left: 48px`, `bottom: 56px`):

1. **Name** — white, ~28px semibold  
2. **Role** — Geist Mono uppercase, `#a19afe`  
3. **Brand** — `tatum-icon.png` (~36px), **not** text “Tatum”

Animate name → role → icon; dismiss before the first big overlay (~4s).

### Outro (end card)

- Starts when the **talking-head bed ends**, not mid-narration.  
  Example: bed = 22s → root `data-duration="25"`, outro clip `data-start="22"` `data-duration="3"`.
- Full-bleed `#080a0d`, light grid, white logo, short CTA (optional gradient accent on one phrase).
- **No URL chip** unless the brief asks for it.
- CSS resting state: `visibility: hidden` on the outro clip so it doesn’t black-out frame 0 before the framework activates it. Animate **inner** elements only.

---

## Overlay rules (critical)

| Overlay type | When | Talking head | Logo |
|--------------|------|--------------|------|
| **Full / near-fullscreen** (whole dashboard) | Scripted window (e.g. 4.5s–13s) | **Blur** (~16px) + light scrim; optional slight scale-up | Covered (overlay above logo) |
| **Partial** (drawer, side panel, card) | Later beat (e.g. 15s–19s) | **No blur** — face stays sharp | Usually still visible |

Do not blur the bed behind partial overlays. Clear blur when a full overlay exits.

### Product fidelity

- Rebuild UI from the **real product**, not invented marketing widgets.
- Match real labels, tabs, and empty states.
- Prefer real fixture/sample data shapes when inventing numbers/rows for demos.

### Motion inside overlays

- Stagger sections in; show one meaningful interaction (filter apply, cell select, tab switch).
- Cursor demos: GSAP `x` / `y` only. Measure the target with the overlay in-layout; nudge the tip down a few pixels if it sits above the control.
- Skip decorative click-ripples unless they clearly read as intentional.

---

## Default timeline spine

Adjust times to the script, keep this shape:

1. **0 → ~4s** — Clear talking head; corner logo; lower third; intro titles  
2. **Scripted window** — Full overlay **with** blur  
3. **Later window** — Partial overlay **without** blur  
4. **Until bed ends** — Clear talking head again  
5. **Bed end → composition end** — Outro only  

### Bed media hygiene

- Some exports have a **black first frame**. Trim ~40ms+ from the start so frame 0 shows the speaker (`ffmpeg -ss 0.04 -i in.mov …`).
- Probe brightness of frame 0 if the render “starts black”.

---

## Minimal skeleton

Use this as a starting `index.html` (fill in content and timeline):

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1280, height=720" />
    <title>Tatum — Feature</title>
    <link
      href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body, #root {
        width: 1280px; height: 720px; overflow: hidden;
        font-family: 'Poppins', sans-serif;
      }
      #root { position: relative; background: #111; }
      #avatar-video {
        position: absolute; inset: 0; width: 1280px; height: 720px;
        object-fit: cover; display: block; z-index: 1;
      }
      #blurScrim {
        position: absolute; inset: 0; z-index: 2;
        background: rgba(245, 245, 247, 0.45); opacity: 0; pointer-events: none;
      }
      .corner-logo { position: absolute; top: 28px; left: 32px; z-index: 14; width: 130px; }
      .lower-third {
        position: absolute; left: 48px; bottom: 56px; z-index: 15;
        display: flex; border-radius: 14px; overflow: hidden;
        background: rgba(8, 10, 13, 0.82); opacity: 0; visibility: hidden;
      }
      .lt-body { padding: 16px 24px 16px 20px; }
      .lt-name { font-size: 28px; font-weight: 600; color: #fff; }
      .lt-role {
        margin-top: 3px; font-family: 'Geist Mono', monospace; font-size: 15px;
        letter-spacing: 0.12em; text-transform: uppercase; color: #a19afe;
      }
      .lt-brand { display: grid; place-items: center; padding: 0 18px; }
      .lt-brand img { width: 36px; height: 36px; }
      .intro-text {
        position: absolute; left: 56px; top: 100px; z-index: 12;
        opacity: 0; visibility: hidden;
      }
      .intro-eyebrow {
        font-family: 'Geist Mono', monospace; font-size: 16px; font-weight: 500;
        letter-spacing: 0.18em; text-transform: uppercase; color: #fff;
      }
      .intro-accent {
        margin-top: 8px; font-size: 44px; font-weight: 700; line-height: 1.08;
        letter-spacing: -0.02em; color: #000;
      }
      .intro-product {
        margin-top: 4px; font-size: 28px; font-weight: 600; line-height: 1.18; color: #fff;
      }
      /* Full overlay: high z-index, above logo. Partial overlays: no avatar blur. */
      .scene-end {
        position: absolute; inset: 0; z-index: 40;
        display: flex; align-items: center; justify-content: center;
        background: #080a0d; visibility: hidden;
      }
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="25"
      data-width="1280"
      data-height="720"
    >
      <video id="avatar-video" class="clip" src="assets/avatar.mov" muted playsinline preload="auto"
        data-start="0" data-duration="22" data-track-index="0"></video>
      <audio id="avatar-audio" class="clip" src="assets/avatar.mov"
        data-start="0" data-duration="22" data-track-index="1"></audio>

      <div id="blurScrim" aria-hidden="true"></div>
      <div class="corner-logo"><img src="assets/tatum-logo-light.svg" alt="Tatum" /></div>

      <div class="lower-third" id="lowerThird">
        <div class="lt-body">
          <p class="lt-name">Speaker Name</p>
          <p class="lt-role">Title</p>
        </div>
        <div class="lt-brand"><img src="assets/tatum-icon.png" alt="" width="36" height="36" /></div>
      </div>

      <div class="intro-text" id="intro">
        <p class="intro-eyebrow">Product area</p>
        <p class="intro-accent">Headline line one<br />line two</p>
        <p class="intro-product">Subheader line one<br />line two</p>
      </div>

      <!-- Full overlay (blur bed) + partial overlay (no blur) go here -->

      <section id="end" class="clip scene-end" data-start="22" data-duration="3" data-track-index="3">
        <div id="endInner">
          <img src="assets/tatum-logo-white.svg" alt="Tatum" width="280" />
          <p>Short CTA with <span style="color:#a19afe">accent</span>.</p>
        </div>
      </section>
    </div>

    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      tl.set('#avatar-video', { opacity: 1 }, 0);
      // Build lower-third, intro, overlays, outro on `tl` …
      window.__timelines['main'] = tl;
      if (!/[?&]render=1/.test(location.search)) tl.play(0);
    </script>
  </body>
</html>
```

---

## Copy & tone

- Lead with outcomes (reliability, speed, clarity), not fear.
- Keep on-screen text short; UI motion carries the story.
- Outro: one short line; brand accent on the payoff.

---

## Handoff checklist

Before sharing a finished project:

- [ ] `assets/` includes logos, icon, and bed media  
- [ ] `npx hyperframes lint` — 0 errors  
- [ ] `npx hyperframes check` — passed  
- [ ] High-quality MP4 in `renders/`  
- [ ] Frame 0 is talking head (not black)  
- [ ] Full overlays blur; partial overlays do not  
- [ ] Outro starts at bed end; no unexpected URL  
- [ ] Lower third uses **icon**, not “Tatum” text  
- [ ] Headline **black**, subheader **white**  

---

## Common failures

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| Starts on black | Bed has black first frame, or outro clip visible at t=0 | Trim bed; `visibility: hidden` on outro clip; `tl.set(avatar, {opacity:1}, 0)` |
| Stuttery cursor / UI | Animating `left`/`top` | Use GSAP `x`/`y` |
| Lint: don’t animate clip visibility | Tweening `#end` visibility | Animate `#endInner` only |
| Lint: exit missing hard kill | Fade ends on clip boundary | Add `tl.set(..., { opacity: 0 }, t)` |
| Logo shows through dashboard | Overlay z-index too low | Raise full overlay above corner logo |
| Face blurred behind drawer | Applied full-overlay blur to partial | Remove blur/scrim for partial overlays |
| Outro too early | Tied to mid-script, not bed end | Start outro at bed duration; extend root duration |

---

## AI plate + HyperFrames overlays (launch trailers)

Reference project: `tatum-websockets-launch/` (WebSockets launch on a cinematic AI journey plate).

### Intent

- Full-bleed **AI / generative journey** as the bed.
- HyperFrames owns **all readable text**, glass cards, event tags, subscribe cmds, introduce title, logos, and the dark outro.
- Prefer **continuous camera motion** in the plate; overlays ride that motion rather than fighting it with hard cuts.
- Keep product language **accurate to docs.tatum.io** (real endpoints, real subscription names, real supported chains).

### Canvas & media

| Item | Value |
|------|--------|
| Composition | **1920×1080**, 24fps when the plate is 24fps |
| Bed | Full-bleed `<video>` `object-fit: cover` |
| Audio | Separate `<audio>` clip, **same source** as the bed. Video stays `muted`. |
| Duration | Root = bed length + dark outro (~2.5–3.5s) |

```html
<video id="bed" class="bed" src="assets/footage/journey.mp4"
  muted playsinline data-start="0" data-duration="15.73" data-track-index="0"></video>
<audio id="bed-audio" src="assets/footage/journey.mp4"
  data-start="0" data-duration="15.73" data-track-index="10" data-volume="1"></audio>
```

### Opening & ending timing

- **No black veil at t=0.** Cut straight onto the first meaningful plate frame (globe, city, product shot). If frame 0 is black, trim the plate or set `data-media-start`.
- Corner logo top-left from open; fade out on the cut to outro.
- Soft **top scrim** under the logo is fine. Do **not** add a thin purple→green chrome strip across the top edge — it reads as an artifact.
- Prefer a gentle **end slowdown** (retime last ~1.5–2s of A/V with `setpts` + `atempo`) over a freeze-frame hold. Freezes break the plate audio awkwardly.
- Dark outro only after the plate ends — same `#080a0d` + grid language as talking-head outros.

### Type scale (1920×1080, phone-safe)

Size for **small-screen** viewing (X / LinkedIn / phone). Values below are the house defaults after the WebSockets pass:

| Element | Size / treatment |
|---------|------------------|
| Corner logo | **~196px** wide, top-left (~32–44px inset) |
| Floating labels (chain names, etc.) | **26px** semibold + **44px** chain icons |
| Glass card URL / primary mono | **26px** Geist Mono |
| Glass card status (`CONNECTED`) | **20px** semibold, letter-spaced |
| Event / stream tags (pills) | **22px** Geist Mono, padding ~16×28 |
| Code / RPC commands | **30px** Geist Mono in a glass chip |
| Introduce title | **88px** extrabold; accent word in **solid** `#2ccd9a` |
| Introduce support line | **38px** semibold |
| Outro logo | **~340px** wide |
| Outro lines (rotated) | **same size** — **46px** semibold; one line each, no mid-sentence wrap |

Glass endpoint cards on stream beats: aim **~900px** wide with generous padding (~38×44). Tags must **orbit around** the card — never land on top of it.

### Brand accents on cinematic plates

| Token | Value | Use |
|-------|--------|-----|
| Tatum green | `#2ccd9a` | Product-name accent in introduce titles |
| Cyan / pulse | `#3BC7FF` | WSS URL, packet borders, live data glow |
| Status OK | `#34d399` | Connected dots / “CONNECTED” |
| Outro accent | white → `#a19afe` → `#4f37fd` | Optional gradient on **one** payoff phrase |

**Never** put a `background-clip: text` gradient on a word that also inherits a heavy black `text-shadow`. Transparent fill lets the shadow show through and the letter centers go muddy. Prefer **solid** `#2ccd9a` (or a dedicated shadow only on that span).

### Overlay stack

```text
z-0   bed video
z-2   monitor blur / darken (only when title must read over busy UI)
z-10  graphics layer (labels, cards, tags, cmds, introduce)
z-27  top scrim
z-30  corner logo
z-40  dark outro clip
```

When the plate lands on a busy monitor / dashboard:

1. Soft blur + darken the bed (`backdrop-filter: blur(10px)` + `rgba(4,8,16,~0.48)`).
2. Keep introduce title **above** that veil so type stays sharp.
3. Hold title long enough to read (~2s+ of on-screen time); do not rush the cut to outro.

### Motion patterns

- Labels / cards: emerge with opacity + scale + small travel; exit opposite direction.
- Stream tags: start already **outside** the glass card bounds and fly further out.
- Commands: **one at a time**, no overlapping crossfades (layout lint + readability).
- Outro copy: **rotate** single lines in the same centered slot (first out → second in). Equal font size. Center with `width: 100%` on the text stage — do not shrink-wrap to the logo width or long lines look off-center.

### Copy rules (product-accurate)

- Pull endpoints, method names, and subscription types from **docs.tatum.io** (e.g. WebSocket Event Subscriptions).
- Example Eth/Polygon: `eth_subscribe("newHeads" | "logs" | "newPendingTransactions")`.
- Example stream tags: `NEW HEAD`, `PENDING TX`, `LOGS`, plus Solana-native labels when the story is multi-chain (`SLOT UPDATE`, `ACCOUNT UPDATE`).
- Supported-chain callouts must match GA: e.g. **Solana · Ethereum · Polygon**.
- Spell product names as in docs: **WebSockets**.

### Retiming the plate (subtle end linger)

When introduce copy needs more hold without a freeze:

```bash
# Last ~2s at 0.75× — audio time-stretched to match (no pitch freeze gap)
ffmpeg -y -i assets/footage/journey.mp4 -filter_complex "\
[0:v]trim=0:13.0,setpts=PTS-STARTPTS[v1];\
[0:a]atrim=0:13.0,asetpts=PTS-STARTPTS[a1];\
[0:v]trim=13.0:15.069,setpts=(PTS-STARTPTS)/0.75[v2];\
[0:a]atrim=13.0:15.069,asetpts=PTS-STARTPTS,atempo=0.75[a2];\
[v1][a1][v2][a2]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac \
  assets/footage/journey-retimed.mp4
```

Then point both `<video>` and `<audio>` at the retimed file and match `data-duration` to the new length.

### AI-plate checklist

- [ ] 1920×1080; frame 0 is the journey (not black)
- [ ] Bed audio on a separate `<audio>` clip; video muted
- [ ] Type sizes follow the phone-safe table above
- [ ] No top chrome strip; logo top-left until outro
- [ ] Busy monitor beats use soft blur/darken under titles
- [ ] Stream tags clear the glass card
- [ ] Copy matches docs (methods, chains, spelling)
- [ ] Accent words use solid brand green (no muddy clip+shadow)
- [ ] Outro lines same font size, full-width centered, rotated
- [ ] Prefer end slowdown over freeze if you need more read time
- [ ] `hyperframes check` passed; draft MP4 reviewed on a phone-width window

