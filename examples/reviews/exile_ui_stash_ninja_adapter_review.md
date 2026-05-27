# Exile-UI Stash-Ninja Adapter Review

This is a review and adapter plan only. It does not implement an Exile-UI plugin, modify Exile-UI files, automate the game client, send keypresses, read the screen, read clipboard data, call poe.ninja, call the trade site, write Exile-UI caches, publish artifacts, or record recommendation outcomes.

## Review Date

- Reviewed on: 2026-05-27
- Upstream project: `Lailloken/Exile-UI`
- Upstream snapshot inspected locally: `5f3185dd58672baa2859f7357c0704afc18ee7af`
- User interest: use Exile-UI personally for overlay/campaign QoL, and evaluate whether Wraeclast Quant can safely provide market intelligence to Stash-Ninja.

## Source Inputs

- Exile-UI repository: `https://github.com/Lailloken/Exile-UI`
- Stash-Ninja wiki: `https://github.com/Lailloken/Exile-UI/wiki/Stash%E2%80%90Ninja`
- Reddit discussion supplied by the user: `https://www.reddit.com/r/PathOfExile2/comments/1to8wa1/what_is_this_software/`
- Exiled Exchange 2 FAQ for community overlay rule-of-thumb: `https://kvan7.github.io/Exiled-Exchange-2/faq`

## Observed Exile-UI Boundary

Exile-UI is an AutoHotkey overlay, not a local market-analysis library. Its README says the tool reads the game's `client.txt`, sends keypresses for copied item info, chat commands, and in-game searches, checks screen content for context sensitivity, and reads on-screen text on keypress for tooltips. Its author also states that GGG has not approved local third-party tools and cannot guarantee ban safety.

The user-provided Reddit thread and the Exiled Exchange 2 FAQ both reflect the common community view that overlays are generally considered safe when they avoid process injection, memory reading, and multi-action automation. That consensus is useful context, but it is anecdotal and does not change Wraeclast Quant's project boundary.

For Wraeclast Quant, the safe integration boundary is:

- Exile-UI may remain a separate user-installed overlay.
- Wraeclast Quant may generate local, derived-only companion outputs.
- Wraeclast Quant must not send keypresses, click UI, read screen pixels, read clipboard contents, automate stash interaction, whisper, trade, or reuse Exile-UI's game-client hooks.

## Observed Stash-Ninja Shape

Stash-Ninja is implemented primarily in `modules/stash-ninja.ahk`.

Important local files and inferred roles:

- `data/global/[stash-ninja] tabs 2.json`: fixed PoE2 stash-tab grid metadata. Rows contain grid coordinates, display names, and poe.ninja ids for known tab items.
- `ini 2/stash-ninja.ini`: user settings for PoE2 Stash-Ninja. The code reads and writes sections such as `settings`, `global profiles`, and tab-specific sections.
- `data/global/[stash-ninja] prices 2.ini`: processed price cache generated from poe.ninja economy responses. The code writes tab sections and `<tab> names` sections after fetching prices.

Relevant settings/profile fields:

- `[settings] use global profiles`
- `[settings] enable price history`
- `[settings] font-size`
- `[global profiles] limit <1-5> bot`
- `[global profiles] limit <1-5> top`
- `[global profiles] limit <1-5> cur`
- `[<tab>] limit <1-5> bot/top/cur`
- `[<tab>] bookmarking`
- `[<tab>] bookmarks <1-5>` containing JSON-like item-count mappings

Currency selectors use numeric indexes mapped in the UI to `c`, `e`, `d`, and `%` for chaos, exalted, divine, and weekly percentage change. For PoE2, Stash-Ninja fetches `https://poe.ninja/poe2/api/economy/exchange/current/overview?league=<league>&type=<type>` for tab types including `Currency`, `Delirium`, `Essences`, `Ritual`, `Runes`, `Ultimatum`, and `Idols`.

## Adapter Options

### Option A: Derived Watchlist Export

Wraeclast Quant writes a local derived JSON or Markdown file with high-score items, actions, scores, confidence/readiness caveats, and suggested Stash-Ninja profile/bookmark decisions.

Recommended first implementation:

- `data/processed/exile_ui_stash_ninja_watchlist.json`
- `data/processed/exile_ui_stash_ninja_watchlist.md`

Properties:

- Does not require Exile-UI installation.
- Does not write Exile-UI settings.
- Does not require Exile-UI to support imports.
- Lets the user manually copy decisions into Stash-Ninja.
- Keeps Wraeclast Quant fully local and derived-only.

This is the safest first packet.

### Option B: Stash-Ninja Settings Patch Preview

Wraeclast Quant writes a local patch preview for `ini 2/stash-ninja.ini`, containing proposed global profile thresholds or bookmark lists. The user manually reviews and applies it outside Wraeclast Quant.

Possible outputs:

- `data/processed/exile_ui_stash_ninja_patch_preview.md`
- `data/processed/exile_ui_stash_ninja_patch_preview.diff`

Properties:

- More useful than a plain watchlist because it maps to Stash-Ninja's settings vocabulary.
- Still avoids direct writes into a third-party tool.
- Requires careful item-name normalization against `data/global/[stash-ninja] tabs 2.json`.
- Should include rollback instructions and a "close Exile-UI first" manual note if ever used.

This is a reasonable second packet after Option A.

### Option C: Direct Exile-UI File Writer

Wraeclast Quant directly modifies `ini 2/stash-ninja.ini` or `data/global/[stash-ninja] prices 2.ini`.

This is not recommended for MVP.

Reasons:

- It mutates a third-party app's user config.
- It can race with Exile-UI while the overlay is running.
- The price cache is derived from poe.ninja response ids and internal formatting, not a stable public import contract.
- A bad write could break the user's overlay setup.
- It would require a backup/restore workflow, user-provided Exile-UI path, version compatibility checks, and strict failure-closed tests.

## Recommended MVP Path

Build Option A first: a Wraeclast Quant "Stash-Ninja companion watchlist" export.

Suggested behavior:

1. Read the latest local run from SQLite.
2. Select recommendations above a configurable score threshold, defaulting to the same human-review-friendly threshold used elsewhere.
3. Emit derived-only fields:
   - generated timestamp
   - latest run id and source mode
   - item name
   - score
   - action
   - review coverage state
   - suggested Stash-Ninja treatment: `watch`, `bookmark-candidate`, `ignore`, or `manual-review`
   - local caveat text
4. Exclude:
   - raw source payloads
   - Exile-UI paths
   - local absolute paths
   - outcome notes
   - secrets, cookies, tokens, clipboard text, or account data
5. Add a Markdown handoff explaining that the user may manually use the output with Exile-UI/Stash-Ninja.

Suggested command, if approved later:

```powershell
wq stash-ninja-watchlist --output-path data/processed/exile_ui_stash_ninja_watchlist.json
```

Because this would be a new public CLI command, it needs explicit user approval before implementation under `AGENTS.md`.

## Future Patch-Preview Path

After the watchlist export exists, a second packet can inspect a user-supplied Exile-UI folder path and generate a patch preview only:

```powershell
wq stash-ninja-patch-preview --exile-ui-path <folder> --output-path data/processed/exile_ui_stash_ninja_patch_preview.md
```

Guardrails:

- Read-only inspection of Exile-UI files.
- No writes to Exile-UI.
- Validate that `modules/stash-ninja.ahk` and `data/global/[stash-ninja] tabs 2.json` exist.
- Detect PoE2 tab metadata shape before proposing mappings.
- Never run AutoHotkey.
- Never call Exile-UI.
- Never inspect the game client.
- Never read clipboard contents.

## Open Questions

- Should Wraeclast Quant output only a neutral companion watchlist, or should it also suggest Stash-Ninja profile thresholds?
- Which item categories matter most for the user's current stash workflow: currency, essences, ritual, socketables, delirium, or idols?
- Does the user want Exile-UI integration to remain purely manual, or is a patch-preview workflow acceptable later?
- Should Wraeclast Quant keep Exile-UI outputs out of public site bundles by explicit contract test, similar to review worksheets?

## Decision

Proceed only with a local derived watchlist export if the user approves a new command. Do not merge Exile-UI, vendor Exile-UI code, write AutoHotkey, modify Exile-UI settings, write Stash-Ninja caches, or integrate with campaign/overlay features.

