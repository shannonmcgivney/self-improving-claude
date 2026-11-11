---
name: skill-retro
description: Makes a skill better every time it's used - after a skill-driven job is done, collects what the user corrected, what failed, what took extra tries and what worked, turns each into a short dated lesson, and writes it into that skill's lessons file (and, if it's a lasting rule, into the skill's instructions). Use when the user says "retro", "learn from this", "remember this for next time", "update the skill", "what did we learn", "make the skill better", at the end of any multi-step skill run, or after they correct how a skill did something.
---

# Skill retro: the skill gets better every time

A skill only gets better with use if someone writes the lesson down in the skill itself, right after the job, while the corrections are fresh. This is that step.

This skill learns from **this session**. To find patterns across **all** past sessions (repeated corrections, context typed again and again, jobs done by hand), use `history-retro`, which hands per-skill corrections back here.

## When
- At the end of every multi-step skill run.
- Whenever the user corrects a skill's output ("no, always…", "don't do X again").
- When a step took 2+ tries, a script failed, or a tool behaved unexpectedly.

## Steps
1. **Name the target skill** (folder in `~/.claude/skills/<name>/`). Read its `SKILL.md` and its lessons file (`rules/lessons.md` or `LESSONS.md`; create `LESSONS.md` if neither exists).
2. **Collect evidence from this session only**: the user's corrections (quote their words), steps redone and why, errors and their fixes, things that worked better than expected. No guesses about what "might" help.
3. **Write each as a lesson**, newest first:
   ```markdown
   ## YYYY-MM-DD - <job or project name>
   - **What happened:** …
   - **Learned:** … (one sentence each)
   - **Rules changed:** <file> → <section>, or "none (logged only)"
   ```
4. **Promote lasting rules.** A lesson that will apply every time becomes an instruction: edit the exact step in `SKILL.md` or the rules file it belongs to (one or two lines). A lesson that has shown up twice is always promoted. Keep the skill short: replace outdated lines instead of adding.
5. **Show the user the diff** (lesson lines and any rule edits) in a few lines. They can veto any of it.
6. **Sync copies.** If the skill also lives in a repo or backup folder, copy the changed files there. If it's published publicly, say so; don't push without asking.

## Rules
- Never store credentials, personal data about clients or students, or anything the user marked private in a lessons file.
- Lessons are facts from real use, written plainly. No "always strive to…" filler.
- One retro per run. If nothing new was learned, write one line saying so; that is still useful evidence the skill is stable.
