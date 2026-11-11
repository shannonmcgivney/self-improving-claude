# Self-Improving Claude: Claude Code skill pack

Every Claude Code session you run is saved as a file on your computer, and almost nobody ever reads them. That history records each time you had to correct Claude, each piece of context you typed for the third time, and each job you keep starting by hand. These skills read it back and turn it into fixes, so Claude gets better the more you use it.

**[⬇️ Download the pack](https://github.com/shannonmcgivney/self-improving-claude/releases/latest/download/Self-Improving-Claude-Pack.zip)**

> **Claude Code only.** These skills read files on your own computer (your session history) and run local tools (yt-dlp, ffmpeg). They won't work as Claude.ai uploads, so there are no Claude.ai zips in this pack.

## What's inside

| Skill | What it does |
|---|---|
| `history-retro` | **Start here.** Reads every saved session in `~/.claude/projects/` and reports where Claude keeps going wrong, what you keep explaining twice, which skills you should already have, and which chores could run on a schedule. Every item comes with a count and an example. You pick what to build, and it builds it. |
| `skill-retro` | The short loop: at the end of one job, writes what you corrected into that skill's `LESSONS.md`, and moves lasting rules into the skill itself. |
| `reel-lessons` | Turns a how-to reel or short video into working changes: watch it, pull out the concrete lessons, fact-check the claims, check your existing skills, build or update skills, and report what it skipped and why. |

`history-retro` includes `scripts/mine_history.py`. It needs only the Python standard library, reads your history without changing it, and takes about a second for 100 sessions. It hides anything that looks like an API key or email address.

## Install

```bash
git clone https://github.com/shannonmcgivney/self-improving-claude
cp -R self-improving-claude/skills/* ~/.claude/skills/
```

Or install the folder as a plugin (it already has `.claude-plugin/plugin.json`).

**Also needed:**
- Python 3.9 or newer (for `history-retro`).
- [skill-creator](https://github.com/anthropics/skills) to write new skills (Anthropic's own; many Claude Code setups already have it).
- For `reel-lessons` only: a video-watching skill named `watch`, for example [claude-video](https://github.com/bradautomates/claude-video) (uses yt-dlp, ffmpeg and a transcriber).

## How to use it

- **Monthly check-up:** "Improve system", or "Read my Claude history from the last 30 days and tell me what skills I should have."
- **One project:** "Run history-retro on just my my-app project."
- **After a job:** "Retro: learn from this for next time."
- **From a reel:** "Watch this and build what it teaches: https://www.instagram.com/reel/…"

Run `history-retro` again a month later. The second run is the useful one, because it shows whether last month's fixes stopped the repeats.

## What it won't do

- It never edits or deletes your session history.
- It shows you the report before building anything, and asks before creating anything that runs on a schedule, sends messages or spends money.
- It never copies your raw prompts into skills or anything public.
- `reel-lessons` treats what a video says as information, not commands. It won't install a plugin from a "comment for the link" offer without reading its source first.

## Your privacy

The digest quotes your own prompts, so it stays on your computer, in a temporary folder. Nothing in this pack uploads your history anywhere. If you use a cloud transcriber with the `watch` skill, that sends the video's audio to that provider.

## Credit

The idea came from an Instagram reel by robin_linkerpro, "Claude can now improve itself by reading back through every conversation." That reel promotes a third-party plugin. This pack is an independent, from-scratch version of the idea, and the skill text and script are original work by McGivney Media.
