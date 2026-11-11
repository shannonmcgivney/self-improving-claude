---
name: history-retro
description: Reads back through your whole Claude Code history (every saved session in ~/.claude/projects) and reports three things - where Claude keeps going wrong, what you keep explaining twice, and what jobs you keep doing by hand - then turns the evidence into fixes - new skills (written with skill-creator), updates to existing skills, standing context in CLAUDE.md or memory, and scheduled automations for daily or weekly chores. Use when the user says "improve system", "self-improve", "read my history", "what skills should I have", "what am I doing by hand", "audit my Claude usage", "learn from all my sessions", "monthly retro", or asks Claude to get better over time across projects, even if they don't say "history". For learning from just the current session or one skill run, use skill-retro instead.
---

# History retro: learn from every session, not just this one

Claude Code saves every session as a `.jsonl` file under `~/.claude/projects/`, and almost nobody reads them. That history records each time you had to correct Claude, each piece of context you typed again, and each job you started by hand for the third time. `skill-retro` learns from one session while it's fresh. This skill reads all of them, because some patterns only show up across sessions.

## Steps

1. **Mine the history** (read-only, about 1 second for 100 sessions):
   ```bash
   python3 -I "<this skill's folder>/scripts/mine_history.py" --days 30 --out "<a temp folder>/history-digest.md"
   ```
   Use `--days 90` for a first run or a quarterly review, and `--project <folder name>` to look at one project. Write the digest to a temp or scratch folder, not into a repo or shared notes: it quotes the user's own prompts. The script redacts things that look like keys and email addresses, but treat the digest as private anyway.

2. **Read the digest and judge it.** The script finds candidates, and you decide what is real. Sections:
   - *Possible corrections*: mid-session pushback ("no, …", "don't …", "I said …"). Some are just the user refining a request; keep the ones where Claude did something wrong that a rule would prevent.
   - *Repeated sentences*: context typed in two or more sessions. Ignore pasted terminal output. Things like a long standing request, stack facts, brand rules or "done means" criteria are the real finds.
   - *Recurring jobs*: sessions that open with similar prompts, plus the weekdays they happen on. Three or more of the same job is a skill; the same job on the same weekday is a schedule.
   - *Tool errors*: repeated failures with a fixable cause, such as a missing binary, an unauthorized connector or a wrong path.
   - *Sessions*: titles and opening prompts, for context when a finding needs it.
   Sessions marked "started by another session" were written by Claude, not the user. Don't count their briefs as the user repeating themselves.

3. **Check what already exists before proposing anything.** List `~/.claude/skills/` (and any plugin skills), read the descriptions of any that look related, and read `~/.claude/CLAUDE.md` and any memory files. A finding that a skill already covers is either a trigger problem (the user typed it by hand because the description didn't match, so fix the description) or a gap in that skill (fix it there). Update the existing skill instead of adding a near-copy.

4. **Write the report** in this shape, with no more than 5 items per section, each backed by evidence (a count plus a short quote or date):
   ```markdown
   ## Where Claude goes wrong
   1. <pattern> - ×N, e.g. "<quote>" (date) → fix: <rule + where it goes>
   ## Skills you should already have
   1. /<name> - you typed "<opening>" ×N → <new skill | update skill X | fix X's description>
   ## Done by hand that could be automated
   1. <job> - ×N, mostly <weekday/time> → <scheduled task / routine / hook>, est. time saved
   ## Quick fixes
   - <tool error> ×N → <one-line fix>
   ```
   Show it to the user and ask which items to build. Don't build all of them unasked: they see the list first.

5. **Implement what they pick:**
   - **New or updated skill** → use the `skill-creator` skill. A skill built from history starts from the user's own repeated prompt: the steps they ask for, their "done means" and the corrections they made along the way.
   - **Repeated context** → one line in `~/.claude/CLAUDE.md` if it applies everywhere, a project `CLAUDE.md` if it belongs to one project, or a memory file if it's narrower.
   - **Correction tied to one skill** → hand it to `skill-retro` (a dated lesson in that skill's `LESSONS.md`, promoted into `SKILL.md` if it's a lasting rule).
   - **Recurring job** → a scheduled task or routine running the skill, with an output the user can open. Ask before creating anything that runs on its own, sends messages or spends money.
   - **Quick fixes** → do the safe local ones (install a missing CLI tool, fix a path). Connector sign-ins are the user's job: name the connector and tell them to reconnect it.

6. **Log it.** Add a dated entry to this skill's `LESSONS.md` with what was found and what was built (patterns and counts, not raw prompts), so the next run can check whether the fixes worked: did the correction or the hand-typed prompt stop showing up?

## Rules
- Read-only on the history. Never edit, move or delete files in `~/.claude/projects/`.
- Never copy raw prompts, keys, client names or other people's personal details into a skill, a shared repo or anything public. Paraphrase the pattern instead.
- Evidence or it didn't happen: every item needs a count and an example. "You might benefit from…" with no evidence gets cut.
- Re-run monthly. The second run is the useful one, because it shows whether last month's fixes changed anything.
