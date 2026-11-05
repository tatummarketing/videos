# HyperFrames Composition Project — WaaS Predictable Pricing

Avatar video: `assets/avatar.mp4` (HeyGen c58140af, 15.04s, 1280×720).

Narration (word-timestamped via whisper):

- 0.0–4.0 "Tatum smart wallets are embedded crypto wallets that don't punish you as you scale."
- 4.5–8.9 "Create wallets in minutes with built-in APIs for balances, prices, and notifications."
- 9.8–12.7 "Predictable costs from your first wallet to your millionth."
- 13.4–14.9 "Book your free solution engineering session."

## Composition

- `index.html` — 1280×720, 18s total: intro copy → built-in APIs card → pricing-at-scale card (30K → 1M wallets, prices step down) → end card
- Pricing figures from `pagers/public/smart-wallet-enterprise-calculator.html` PRESETS:
  30K: $0.013/wallet, $0.10/tx · 50K: $0.009/$0.08 · 100K: $0.006/$0.06 · 1M: $0.0028/$0.0085

## Commands

```bash
cd waas-pricing-hyperframe
npx hyperframes preview   # preview in browser
npx hyperframes render    # export MP4
npx hyperframes lint      # validate composition
```

## Documentation

https://hyperframes.heygen.com/introduction
