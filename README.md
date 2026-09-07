# Renal Omics Weekly

This folder is the restartable local control plane for a weekly research-paper podcast.

## Workflow

1. `scripts/research_week.py` queries the free Europe PMC API for the preceding seven days and excludes previously published papers.
2. The weekly Codex task reviews and ranks 5–8 candidates, selects 3–5, and rotates one paper from `classic_pool.json`.
3. Safari opens a dated NotebookLM notebook, adds stable paper pages plus the dated source guide, and generates an English Deep Dive Audio Overview.
4. The audio download is normalized to 128 kbps AAC with macOS `afconvert`.
5. The audio is uploaded as a GitHub Release asset. `scripts/render_feed.py` rebuilds the RSS feed and archive page, then pushes them to GitHub Pages.
6. Spotify receives the RSS feed once. Future episodes are discovered automatically.

## One-time items

- Add a public feed-verification address to `owner_email` in `podcast.json`.
- Submit `https://s-weissbach.github.io/renal-omics-weekly/feed.xml` to Spotify for Creators and enter the emailed verification code.
- Keep Safari signed in to the Google account that owns the NotebookLM notebooks.

## Safety and recovery

- Downloads stay in the ignored `downloads/` folder until publication succeeds.
- A dated episode folder and GitHub release tag make each run idempotent.
- Publication stops if the verification email is blank or an output file would be overwritten.
- A paper DOI/PMID is recorded only after an episode has been published.

