# The World Today: 20 November 2026

[![news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/henahenah31-art/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/henahenah31-art/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

A program that draws one newspaper front page summing up the world's news
of Friday 20 November 2026, and writes it to `/output/entry.png`.

## The day in one image — round 1: 38 stories

- **Cyclone Akvan slams ashore** — landfall near Gopalpur at noon; over
  300,000 people evacuated to shelters.
- **World Court: Myanmar guilty of genocide** — the ICJ rules 9-6 on the
  Rohingya case, the first time it has held a state guilty of genocide.
- **Three leaders, one peace declaration** — Trump, Xi and Putin meet in
  Shenzhen; a nuclear war "cannot be won".
- **Kyiv strikes hit two embassies** — Austrian and Dutch missions damaged
  in Russian daytime strikes.
- **Trump weighs new Iran strikes** — Netanyahu urges a four-to-seven-day
  joint campaign; the decision is still open.
- **GTA VI: 19m copies on day one** — $1.84bn in estimated sales, Metacritic 99.
- **Seoul: ex-PM's term overturned** — the top court quashes Han Duck-soo's
  15-year sentence and orders a retrial.
- **Nicholls 146\* as NZ pass 300** — day two in Wellington.
- Plus 30 briefs from around the world: Anthropic's Nasdaq debut, the
  US-Venezuela military pact, the Crimea Bridge hit again, the Gas Husky
  tanker, a record $190.4m Van Gogh, Sudan, Ebola in the DRC, and more —
  and a "BY THE NUMBERS" footer.

The judge has no news feed, so the image explains itself: every story is
headlined and dated on the page, under the masthead "THE WORLD TODAY —
Friday, 20 November 2026".

## How to run

```sh
python3 main.py
```

Writes `/output/entry.png` (1024x1024 PNG, under 1 MiB). Set `ENTRY_OUTPUT`
to write somewhere else instead.

## How it works

Pure Python 3.13 standard library — no network, no randomness, no clock.
The program draws the page with its own tiny raster canvas, a hand-written
5x7 bitmap font stored as bitmask rows, and a hand-written PNG encoder, so
running it twice produces a byte-identical image.

## License

MIT — see `LICENSE`.
