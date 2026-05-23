\# Resources



This file defines public resources Wraeclast Quant may use for Path of Exile 2 market intelligence.



\## Rules



\- Respect each site's terms, robots.txt, and API limits.

\- Prefer official APIs, RSS feeds, downloadable data, or manually reviewed pages where available.

\- Do not bypass login walls, rate limits, CAPTCHAs, or access controls.

\- Do not automate in-game actions.

\- Do not send whispers, perform trades, move the character, click UI, or interact with the game client.

\- Use cached snapshots aggressively.

\- Treat all recommendations as decision support only; the user must manually execute trades.

\- If a source does not clearly allow automated collection, use `manual-review` only.



\## Field Guide



Each resource may include:



\- `id`: stable machine-readable identifier

\- `name`: human-readable source name

\- `type`: source category

\- `url`: source URL

\- `priority`: critical, high, medium, low

\- `allowed\_use`: api, rss, manual-review, manual-or-api-if-available, public-page-snapshot, no-automation

\- `collector`: intended collector module or placeholder

\- `refresh`: suggested refresh cadence

\- `reliability`: high, medium, low, unknown

\- `notes`: how the source should be used



\---



\## Official Sources



\- id: official\_trade\_site

&#x20; name: Path of Exile 2 Official Trade

&#x20; type: official\_trade

&#x20; url: https://www.pathofexile.com/trade2

&#x20; priority: critical

&#x20; allowed\_use: manual-review

&#x20; collector: official\_trade\_placeholder

&#x20; refresh: manual

&#x20; reliability: high

&#x20; notes: Official trade search. Use as the ground truth for manual price checks and listing verification. Do not automate aggressive queries.



\- id: official\_developer\_docs

&#x20; name: Path of Exile Developer Docs

&#x20; type: official\_docs

&#x20; url: https://www.pathofexile.com/developer/docs

&#x20; priority: critical

&#x20; allowed\_use: manual-review

&#x20; collector: official\_docs\_placeholder

&#x20; refresh: weekly

&#x20; reliability: high

&#x20; notes: Official API and OAuth documentation. Review before implementing any real API connector.



\- id: official\_api\_reference

&#x20; name: Path of Exile API Reference

&#x20; type: official\_docs

&#x20; url: https://www.pathofexile.com/developer/docs/reference

&#x20; priority: critical

&#x20; allowed\_use: manual-review

&#x20; collector: official\_docs\_placeholder

&#x20; refresh: weekly

&#x20; reliability: high

&#x20; notes: Official endpoint reference. Use to validate what is supported before adding collectors.



\- id: official\_forum

&#x20; name: Path of Exile Official Forum

&#x20; type: official\_forum

&#x20; url: https://www.pathofexile.com/forum

&#x20; priority: high

&#x20; allowed\_use: manual-review-or-api-if-available

&#x20; collector: patch\_notes\_placeholder

&#x20; refresh: daily

&#x20; reliability: high

&#x20; notes: Announcements, patch notes, hotfixes, league news, balance updates.



\- id: official\_patch\_notes\_current

&#x20; name: Path of Exile 2 Current Patch Notes

&#x20; type: patch\_notes

&#x20; url: https://www.pathofexile.com/forum/view-thread/3932540

&#x20; priority: critical

&#x20; allowed\_use: manual-review

&#x20; collector: patch\_notes\_placeholder

&#x20; refresh: daily-during-league-launch

&#x20; reliability: high

&#x20; notes: Current known patch notes source. Update this URL when a new major patch or league launches.



\---



\## Price Data



\- id: poe2\_scout\_currency

&#x20; name: POE2 Scout Currency

&#x20; type: price\_site

&#x20; url: https://poe2scout.com/economy/currency

&#x20; priority: high

&#x20; allowed\_use: manual-or-api-if-available

&#x20; collector: price\_site\_placeholder

&#x20; refresh: hourly

&#x20; reliability: medium

&#x20; notes: Current currency prices and market trend checks.



\- id: poe2\_scout\_uniques

&#x20; name: POE2 Scout Unique Items

&#x20; type: price\_site

&#x20; url: https://poe2scout.com/

&#x20; priority: high

&#x20; allowed\_use: manual-or-api-if-available

&#x20; collector: price\_site\_placeholder

&#x20; refresh: hourly

&#x20; reliability: medium

&#x20; notes: Use for unique item price checks and trend snapshots where available.



\- id: poe\_ninja\_poe2\_currency

&#x20; name: poe.ninja POE2 Currency

&#x20; type: price\_site

&#x20; url: https://poe.ninja/poe2/economy/vaal/currency

&#x20; priority: high

&#x20; allowed\_use: api

&#x20; collector: price\_site\_placeholder

&#x20; refresh: hourly

&#x20; reliability: medium

&#x20; notes: Currency economy overview and historical trend reference.



\- id: poe\_ninja\_poe2\_economy

&#x20; name: poe.ninja POE2 Economy

&#x20; type: price\_site

&#x20; url: https://poe.ninja/poe2/economy/

&#x20; priority: high

&#x20; allowed\_use: manual-or-api-if-available

&#x20; collector: price\_site\_placeholder

&#x20; refresh: hourly

&#x20; reliability: medium

&#x20; notes: Broader economy overviews. Useful for market trend snapshots and cross-checking POE2 Scout.



\---



\## Build Data



\- id: poe\_ninja\_poe2\_builds

&#x20; name: poe.ninja POE2 Builds

&#x20; type: build\_site

&#x20; url: https://poe.ninja/poe2/builds

&#x20; priority: high

&#x20; allowed\_use: manual-or-api-if-available

&#x20; collector: build\_site\_placeholder

&#x20; refresh: daily

&#x20; reliability: high

&#x20; notes: Best source for current league build popularity, skill usage, ascendancies, and gear patterns.



\- id: maxroll\_poe2\_builds

&#x20; name: Maxroll POE2 Build Guides

&#x20; type: build\_site

&#x20; url: https://maxroll.gg/poe2/build-guides

&#x20; priority: high

&#x20; allowed\_use: manual-review

&#x20; collector: build\_site\_placeholder

&#x20; refresh: daily-during-league-launch

&#x20; reliability: high

&#x20; notes: Curated build guides. Useful for league starter demand prediction and item dependency extraction.



\- id: mobalytics\_poe2\_starter\_builds

&#x20; name: Mobalytics POE2 Starter Builds

&#x20; type: build\_site

&#x20; url: https://mobalytics.gg/poe-2/starter-builds

&#x20; priority: medium

&#x20; allowed\_use: manual-review

&#x20; collector: build\_site\_placeholder

&#x20; refresh: daily-during-league-launch

&#x20; reliability: medium

&#x20; notes: Starter build guides. Useful for early league demand prediction.



\---



\## Item Reference / Game Knowledge



\- id: poe2db

&#x20; name: PoE2DB

&#x20; type: item\_database

&#x20; url: https://poe2db.tw/

&#x20; priority: high

&#x20; allowed\_use: manual-review

&#x20; collector: reference\_placeholder

&#x20; refresh: weekly

&#x20; reliability: medium

&#x20; notes: Item, skill, modifier, unique, and game-data reference. Use for enrichment, not price truth.



\- id: poe2\_wiki

&#x20; name: Path of Exile 2 Wiki

&#x20; type: wiki

&#x20; url: https://www.poe2wiki.net/

&#x20; priority: medium

&#x20; allowed\_use: manual-review

&#x20; collector: reference\_placeholder

&#x20; refresh: weekly

&#x20; reliability: medium

&#x20; notes: Human-readable explanations for mechanics, items, quests, skills, and league systems.



\---



\## Crafting / Base Valuation



\- id: craft\_of\_exile\_poe2

&#x20; name: Craft of Exile POE2

&#x20; type: crafting\_reference

&#x20; url: https://www.craftofexile.com/

&#x20; priority: medium

&#x20; allowed\_use: manual-review

&#x20; collector: crafting\_placeholder

&#x20; refresh: weekly

&#x20; reliability: medium

&#x20; notes: Crafting probabilities and modifier reference if POE2 support is available. Useful for rare base valuation and crafting arbitrage ideas.



\---



\## Social Signals



\- id: reddit\_poe2

&#x20; name: Reddit Path of Exile 2

&#x20; type: social

&#x20; url: https://www.reddit.com/r/PathOfExile2/

&#x20; priority: medium

&#x20; allowed\_use: api-or-manual-review

&#x20; collector: social\_placeholder

&#x20; refresh: daily

&#x20; reliability: medium

&#x20; notes: Build hype, item mentions, complaint signals, balance discussion, and sentiment tracking.



\- id: reddit\_pathofexile

&#x20; name: Reddit Path of Exile

&#x20; type: social

&#x20; url: https://www.reddit.com/r/pathofexile/

&#x20; priority: medium

&#x20; allowed\_use: api-or-manual-review

&#x20; collector: social\_placeholder

&#x20; refresh: daily

&#x20; reliability: medium

&#x20; notes: Broader community discussion. Useful when POE2 discussion spills into the main Path of Exile subreddit.



\- id: reddit\_pathofexilebuilds

&#x20; name: Reddit Path of Exile Builds

&#x20; type: social\_builds

&#x20; url: https://www.reddit.com/r/PathOfExileBuilds/

&#x20; priority: medium

&#x20; allowed\_use: api-or-manual-review

&#x20; collector: social\_placeholder

&#x20; refresh: daily

&#x20; reliability: medium

&#x20; notes: Build theorycrafting and early meta discovery. Verify POE2 relevance before using signals.



\---



\## Discord Signals



\- id: official\_poe2\_discord

&#x20; name: Official Path of Exile 2 Discord

&#x20; type: discord

&#x20; url: https://discord.gg/pathofexile

&#x20; priority: high

&#x20; allowed\_use: manual-review

&#x20; collector: discord\_placeholder

&#x20; refresh: daily-during-league-launch

&#x20; reliability: medium

&#x20; notes: High-value build hype and activity signal. Track class/build channel activity, repeated item mentions, skill discussion volume, and emerging league-starter consensus. Do not scrape private Discord content without permission. Future implementation should use an approved Discord bot or manual exports only.



\---



\## Video / Creator Signals



\- id: youtube\_manual\_watchlist

&#x20; name: YouTube Manual Creator Watchlist

&#x20; type: youtube

&#x20; url: https://www.youtube.com/

&#x20; priority: medium

&#x20; allowed\_use: manual-review

&#x20; collector: youtube\_placeholder

&#x20; refresh: daily-during-league-launch

&#x20; reliability: medium

&#x20; notes: Replace this with specific creator channels. Track build guide uploads, league starter videos, market strategy videos, and item showcases.



\# Add creator channels like this:

\#

\# - id: youtube\_creator\_example

\#   name: Example Creator

\#   type: youtube\_channel

\#   url: https://www.youtube.com/@example

\#   priority: medium

\#   allowed\_use: rss-or-manual-review

\#   collector: youtube\_placeholder

\#   refresh: daily-during-league-launch

\#   reliability: medium

\#   notes: Add channel-specific notes here.



\---



\## Manual Research Queue



\- id: manual\_trade\_checks

&#x20; name: Manual Trade Checks

&#x20; type: manual\_workflow

&#x20; url: https://www.pathofexile.com/trade2

&#x20; priority: critical

&#x20; allowed\_use: manual-review

&#x20; collector: none

&#x20; refresh: as-needed

&#x20; reliability: high

&#x20; notes: Use this when the agent flags an item. Manually verify real listings, rolls, corruption status, stack size, and seller behavior before acting.



\- id: manual\_build\_dependency\_review

&#x20; name: Manual Build Dependency Review

&#x20; type: manual\_workflow

&#x20; url: https://poe.ninja/poe2/builds

&#x20; priority: high

&#x20; allowed\_use: manual-review

&#x20; collector: none

&#x20; refresh: daily-during-league-launch

&#x20; reliability: high

&#x20; notes: Manually inspect whether high-scoring items are actually core build dependencies or just incidental gear.

