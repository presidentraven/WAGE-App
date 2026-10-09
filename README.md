# W.A.G.E. v0.5 — Installable Android home-screen app (PWA)

## What this release does

- Adds `manifest.webmanifest`, `sw.js`, 192px/512px icons, and an installation banner. It behaves like a phone app **after hosting via HTTPS and installing**. No Play Store listing or APK is included.
- Preserves all four pilot pages, the 60432 home-cost baseline, 35-mile job search, 197 source-stamped EIA Chicago gasoline observations, and EIA collector.
- Adds optional unpaid commuting and preparation minutes. Reports **take-home gain after direct job costs per total committed hour**, not a legal hourly rate.
- Offline operation works after the hosted app is opened online at least once; online data remains subject to publishing/sync.
- Includes a future nationwide ZIP record schema. Nationwide feeds have **not** been populated.

## Install on Android Chrome (after hosting)

1. Extract this ZIP to a new GitHub repository (public if using GitHub Free and GitHub Pages). Preserve directories, especially `index.html`, `sw.js`, `manifest.webmanifest`, `icons/`, `data/`, and `.github/`.
2. In GitHub go to `Settings → Pages → Build and deployment → Source: GitHub Actions`. Public hosting is not private; **never** upload personal addresses or pay details.
3. Open **Actions → Publish W.A.G.E. and refresh EIA archive → Run workflow** once. When the Pages deployment succeeds, open the displayed HTTPS site address in Chrome on Android and tap `⋮ → Install app` (or `Add to Home screen`). The app banner can also offer installation when supported.
4. Open W.A.G.E. from the new home-screen icon. If you disconnect from the internet, the loaded version should still calculate; external job search and ZIP lookups need internet.
5. To schedule actual EIA updates, add your API key as a GitHub Actions secret `EIA_API_KEY`, and run the `Publish W.A.G.E. and refresh EIA archive` workflow. The workflow updates validated source records and publishes the web app in the same run. With no key, it can publish the historical static version, but does not claim to have refreshed EIA data.

**Opening downloaded `index.html` from your Files app allows calculator use but DOES NOT install a genuine PWA.** Service workers require HTTPS or localhost.

**Data migration:** Any local observations on the earlier standalone HTML file may belong to a different browser origin. Export your Job and Evidence CSV files from v0.4 first, then import them into the hosted app. A clear browser cache or removal may erase locally saved observations; keep backups.

## Nationwide scaling plan

Use **one codebase**, not a separate code copy for each ZIP. The data pipeline resolves input ZIP to its current USPS identity and available Census ZCTA, county, state and metro reference geographies; only source-supported values are used. The display must show `ZIP/ZCTA/county/metro/state` scope, original date, provenance, and completeness. Nationwide availability is a future feature, not implied by the pilot. The `data/zip_profile_schema.json` and `data/zip_profiles/60432.json` are starting design contracts. Household inputs should remain on-device by default, with voluntary anonymous sharing only and appropriate privacy controls.

## Historical data and Joliet methodology

The pilot contains 197 weekly EIA Chicago metropolitan gasoline observations from 2023 through October 2026 and dates for selected Illinois wage/policy and Joliet roadwork changes. These are not daily 60432 readings. Private employer jobs must currently be entered manually, with a source and first-seen date.

## Job location methodology (new)

- **Permanent home-cost reference ZIP:** 60432, approximated by 41.5393, -88.0469 (ZIP-Codes.com listing; ZIP centroid approximation). **Job search radius:** 35 statute miles as the crow flies, measured from the reference coordinate to destination ZIP-code centroids, not driven road miles. Zip code areas and their centroids can straddle radius cutoffs.
- **Fill-up assumption:** gasoline purchased in ZIP 60432; the embedded EIA weekly Chicago-area values are a regional price proxy until actual 60432 station-price observations become available. Expenses are based on 60432 household budget; workers can vary workday meals and mileage.
- The manual job ledger requests employer, role, date first observed, work city and ZIP, hourly advertised rate, optional real-world round-trip road miles, and source URL. If Internet is available it may fetch destination ZIP approximate coordinates from https://api.zippopotam.us/us/{ZIP}; if unavailable it stores the listing for review, not counted as verified in-range.
- The separate road mileage controls fuel/wear in the simulator. It should never be inferred as two times radius distance. Actual route estimates require a separate traffic/routing provider.
- No private-sector employer feed is yet connected and no backdated ads are invented. The recommended manual starting point is https://illinoisjoblink.illinois.gov/ (search ZIP 60432, 35-mile radius if provided). No personal home address is transmitted.

## What really updates automatically?

| Data | Collection | Limit |
|---|---|---|
| Chicago regular gas | EIA API, scheduled, when configured | Weekly regional observations, NOT daily 60432 pump prices |
| Illinois employment policy | Dated verified baseline | New policy changes require human review |
| Historic Joliet roadwork | Dated notices baseline | No measured daily congestion delay yet |
| Private-sector job postings | Manual ledger, ZIP filter ready; automated feed not connected | Requires permitted provider and saved history |
| MIT Will County living wage | Curated benchmark | Not a daily value and not ZIP-specific |

## Technical details

- `scripts/update_data.py --online` reads EIA official v2 API with `EIA_API_KEY`, validates dates, series ID, order and values; never fabricates daily rows. Failure stops the workflow and preserves prior git-committed records.
- `scripts/update_data.py --offline` rebuilds the baseline without network (resets `as_of` to the Oct 9, 2026 baseline; does not imply fresh data).
- `scripts/build_site.py` regenerates a bundled `index.html` retaining a usable offline archive.
- `data/current.json` is machine-readable snapshot; each period is source-stamped. The browser loads it when hosted, otherwise falls back to its built-in records.
- `python -m unittest discover -s tests -v` runs the basic integrity tests.
- Estimated daily cost and commuting wear are user assumptions, not source measurements. We do not collect a personal address, route, or exact location on the server.

## Planned next integrations

Add approved job listing feeds that preserve first-seen and last-seen timestamps; date-stamped IDOT closure snapshots; and a licensed/consented route-time source. Store observations separately from estimates. Add an expense time series before attempting true 2023/2024 retroactive living-cost comparisons.
