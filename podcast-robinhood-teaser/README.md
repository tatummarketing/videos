# Podcast episode teaser (1:1)

25-second square intro/teaser video for a Tatum Podcast episode, built with
[HyperFrames](https://www.npmjs.com/package/hyperframes). Two-speaker ElevenLabs
voiceover over the arcade intro track, pop-art panel collage in Tatum brand style.

Final video: `../podcast-robinhood-teaser.mp4` (repo root).

## Reusing this scaffolding for another episode teaser

The project is self-contained. To make a teaser for a new episode you only touch
two things: the dialogue script and the panel content.

### 1. Voiceover — `audio/build-teaser.py`

- Edit the `TURNS` array: `(speaker, text, gap-before-seconds, settings overrides)`.
  Keep lines short — it is a teaser, not the episode.
- Voice IDs and per-speaker base settings are at the top (`VOICES`, `BASE`).
- Put `ELEVENLABS_API_KEY` in the environment or in `.env` in the project root
  (see `.env.example`).
- Run `python3 audio/build-teaser.py`. It caches TTS per turn
  (`audio/tN-speaker.mp3`) — delete a turn's files to force regeneration after
  editing its text. Output: `audio/teaser-final.mp3` (speech + music, loudness
  normalized) and `audio/timings.json` (start/end per turn).
- The script applies the podcast pipeline tricks: edge trims and fades, pause
  caps, per-clip loudness match, tail-blip removal, deterministic tempo jitter,
  and a piecewise music envelope (lead-in swell, quiet bed under speech, outro
  swell on the last line). Music: `audio/bgm-arcade.mp3`.
- Get word-level timestamps for retiming the video:
  `npx hyperframes transcribe audio/teaser-speech.wav --json -m small.en`

### 2. Composition — `index.html`

Scene map (retime `data-start`/`data-duration` and the GSAP timeline to the new
`timings.json` / transcript):

| Scene | What happens |
| --- | --- |
| S1 | Tatum logo assembles from three blocks (geometry taken 1:1 from `tatum-logo-color.svg`), ripple rings, wordmark |
| S2 | Episode question slams in line by line on purple, oversized `?` with starburst |
| Beats A–E | White paper + dot pattern; panels/stickers/token tiles pop in per spoken beat |
| S4 | Logo blocks reassemble, morph into Spotify icon, CTA line |

Style rules baked in (keep them):

- Poppins; sentence case for headings, uppercase only for eyebrows/tags.
- Tags follow the site tag system: white, 2px `#e9eaeb` border, 4px radius.
- Soft layered shadows, never thick offset "comic" shadows; logo blocks have
  square corners.
- Colors: `#4f37fd` purple, `#2ccd9a` green, `#181d27` ink, `#fafafa` paper.

Swap the token images in `assets/tokens/` (Dexscreener thumbnails) and the
wojak/meme overlay in `assets/brand/` for content matching the new episode.

### 3. Check + render

```sh
npx hyperframes check
npx hyperframes snapshot --at "1.4,4.3,8.2,14.2,18.6,23"   # eyeball key frames
npx hyperframes render
```

Copy the final MP4 from `renders/` to the repo root.
