# history-retro lessons

Newest first. One entry per run: what the digest showed (patterns and counts, never raw prompts), what was built, and whether last run's fixes worked.

## From building this skill
- Text the Claude desktop app injects (side-session notes, terminal-pane notes, briefs a parent session writes for a child) looks like human prompts. The miner filters these out; if a new kind shows up as "repeated sentences", add it to `APP_NOTE` or `SPAWNED` in the script.
- Forked sessions repeat the parent's opening prompt, so the miner keeps only the first copy.
- If most sessions show "(no folder)", work is happening in temporary folders the app deletes with the session. Move anything worth keeping into a real project folder.
- On the author's first 90-day run, the most-repeated request (typed by hand in 14 sessions) became its own skill, `reel-lessons` (github.com/shannonmcgivney/reel-lessons). Guessing which skills to build had missed it.
