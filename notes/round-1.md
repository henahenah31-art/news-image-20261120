# Round 1 — build notes

Built 2026-11-20 ~07:30 WIB (session started after the bounty opened
2026-11-20T00:00:00Z). Fresh round 1 for news-image-20261120, $250, 50
places, free entry. Kit: ~/workspace/makefun/news-image-20261120-kit
(level above 27, harness ba4baca8). Anchor: makefun anchor
c8955f4338de6e0f2909be0404055bc0652e71f3 round 34110268.

## What changed vs the 19 Nov round-2 pattern

- New day, new front page: masthead "THE WORLD TODAY — Friday,
  20 November 2026", dateline "38 STORIES - ONE IMAGE".
- Story count 35 -> 38: 8 mains + 30 briefs (was 8 + 27).
- Layout rebuilt for 8 mains: hero (Akvan) + a row of 3 (ICJ, Shenzhen,
  Kyiv) + a row of 4 (Iran, GTA VI, Han, cricket). The 19 Nov layout
  was hero + 3 + 3; the fourth slot in row 3 now carries the cricket
  main, so no main is squeezed into the briefs.
- Code written fresh in this session, in my own structure: a `Page`
  class holding the pixel buffer, glyphs stored as 7 integer bitmask
  rows (not string tuples), different function names and art. The 19
  Nov program was read for the encoder technique only; no code was
  pasted from it.
- New art, all drawn for this page: cyclone spiral, scales of justice,
  three flags (US/China/Russia), columned embassy with a cracked
  window, missile with warning rings, neon skyline + game controller,
  gavel, cricket bat/ball/stumps.
- No world map (same call as 19 Nov: no space at this density; region
  tags on the briefs serve as the markers).
- "BY THE NUMBERS" footer kept, with four new numbers.

## Story list (all verified against reporting; see dates below)

Mains (8):
1. Cyclone Akvan makes landfall today near Gopalpur, Odisha, around
   noon; winds 90-100 kmph gusting to 110; 300,000+ evacuated (over
   3 lakh), 423 rescue teams, 69 trains cancelled, red alert in 11
   districts. Sources: IMD bulletins via jagranjosh / thedailyjagran /
   newsxphere, 19-20 Nov.
2. ICJ finds Myanmar guilty of genocide against the Rohingya, 9-6,
   first time the World Court has held a state guilty of genocide;
   reparations ordered; 700,000+ fled in 2017. Verdict read Thu 19 Nov
   (The Hague). Sources: CNN, Reuters, Le Monde, OHCHR.
3. Trump, Xi and Putin meet in Shenzhen, Thu 19 Nov; joint "Peace
   Declaration": UN reform, more oil, "a nuclear war cannot be won and
   must never be fought"; APEC adopts the Shenzhen Outlook. Sources:
   Le Monde, CNN, The Times, Xinhua via appistos.
4. Russian daytime strikes on Kyiv, Thu 19 Nov: 1 killed, 5 hurt;
   Austrian and Dutch embassies damaged, St Volodymyr's Cathedral
   windows shattered; 98 drones fired. Sources: AFP/Euronews, Kyiv24.
5. Trump weighs new Iran strikes: Netanyahu pressing for a 4-7 day
   joint campaign; Trump undecided; B-1/B-2 on 96-hour notice; intel
   claims Iran plotted a chemical/dirty-bomb attack on US officials,
   no imminent threat indicated. Sources: NYT via israelrealtime,
   Axios, CNN, 18-19 Nov.
6. GTA VI day one: Sensor Tower estimates 19.1m copies, $1.84bn;
   Metacritic 99; ~6m watching streams at 2pm ET; Take-Two -2.7%.
   Sources: USA Today, Reuters via Men's Journal, Finimize, 19 Nov.
7. South Korea's Supreme Court overturns ex-PM Han Duck-soo's 15-year
   term and remands the case for retrial (partial acquittal on
   pre-declaration conduct; other convictions stand; detention
   extended 2 months). Ruled Thu 19 Nov. Sources: Yonhap, Seoul
   Economic Daily. NOTE: not a full acquittal — phrased as "term
   overturned" on the page.
8. Cricket day 2, Wellington: Nicholls 146 not out at lunch, NZ 317
   for 6; Phillips fell for 108 after a 200-run stand. Genuinely
   20 Nov (live scorecard). Sources: ESPNcricinfo live scorecard.

Briefs (30), grouped by region in the source searches:
- Asia/Pacific: ANT debuts (opened $111.50, +34%, closed $97.17,
  +17.1%); Wall St tumbles (Dow -2.2% below 50,000; S&P -2%; Nasdaq
  -2.3%); US-Venezuela military pact (Hegseth, Caracas, 18 Nov);
  IAEA: N. Korea built a Yongbyon enrichment extension (Grossi,
  18 Nov); Fiji disaster declaration over El Nino drought, F$20m
  (18 Nov); William and Kate meet Modi in Delhi (18 Nov); Crimea
  Bridge hit again, rail halted (overnight 18-19 Nov); Gas Husky LPG
  tanker hit by four projectiles, sank off Bulgaria, 19 crew saved
  (17 Nov, confirmed 18 Nov); Australia sanctions 3 settlers + 4
  groups over West Bank building (18 Nov); Voyager 1 one light-day
  out (Al Jazeera).
- Europe/Middle East/Africa: Gaza tanks cross the Yellow Line
  (18 Nov, 1,600 killed since the truce); IDF strikes Hezbollah site
  at Janta, Lebanon (19 Nov); US intel: Iran holds 1,500-2,500
  missiles, low confidence (WSJ, 14 Nov); APEC Shenzhen Outlook;
  Berlin "coalition of the willing" urges winter energy ceasefire;
  Sudan court gives RSF chief Hemedti a second death sentence over a
  $396m scandal (19 Nov); UN: airstrikes displaced 2,500+ this week
  in West Kordofan (19 Nov); DRC Ebola six months on, still out of
  control (NRC, 19 Nov); Sassou-Nguesso mediates Tshisekedi-Ruto
  (19 Nov); Nigeria: two death-row inmates escape Kwara prison,
  police free 20 abducted in Zamfara (19 Nov).
- World/business/culture/sport: Van Gogh "Chataigniers en fleurs"
  $190.4m record at Sotheby's (18 Nov); AMD -9.2% after short-seller
  report; Bitcoin flat near $62,640; Walmart raises outlook;
  Take-Two -2.7% on launch day; England beat Australia by 97 in the
  3rd ODI, Hobart (18 Nov); HRW: Burkina Faso targeting critics in
  exile; Guterres welcomes the ICJ verdict; Pew: Islam largest faith
  by 2035; India-Japan defence talks.

Footer numbers: 300,000+ evacuated (Akvan), $1.84bn GTA VI day-one
sales, $190.4m Van Gogh, 9-6 ICJ vote — all from the same reporting.

Date honesty: the competition covers events of 20 Nov 2026. The
genuinely 20 Nov items are the Akvan landfall and the cricket day-2
play; the rest are 18-19 Nov events first reported then, carried as
this morning's front page (the same convention as the 19 Nov entry,
which carried 17-19 Nov events). The footer credit line says so:
"Stories first reported 18-20 Nov 2026." Leads corrected during
verification: Han Duck-soo was NOT fully acquitted (partial acquittal
+ remand); the ICJ verdict and the Shenzhen trilateral both happened
Thu 19 Nov, not Fri 20 Nov; the Modi-Wales meeting, Fiji declaration,
Gas Husky confirmation, Australia sanctions, IAEA Yongbyon and the
US-Venezuela deal are all 18 Nov; the Iran missile estimate is a
14 Nov WSJ report.

## Verification

- Program run twice (ENTRY_OUTPUT to two test paths):
  sha256 `64b7b0ede29ced1313ef787880e9c74fb01d8ee7bbb5c57f411245a0b08e246f`
  for BOTH runs — byte-identical.
- Output: 1024x1024, 40,174 bytes — under the 1 MiB limit.
- Wrap audit (scripted): all 30 briefs wrap to at most 2 lines; hero
  body 3 lines; row-2 bodies 3-4 lines; row-3 bodies 4 lines; every
  headline fits its column; masthead 534 px wide; all four footer
  labels fit on one line.
- Rendered PNG viewed: no overlapping text, no clipped lines, all 8
  headlines + 30 briefs + footer legible at full size.

## Commit

Round 1 commit: see `git log` (message "Round 1: 38 stories...").
Files: `main.py`, `README.md`, `notes/round-1.md` (plus the init
anchor + LICENSE commits already in the repo).
