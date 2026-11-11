#!/usr/bin/env python3
"""Mine Claude Code session history (~/.claude/projects/**/*.jsonl) into a compact digest.

Standard library only. Read-only: never modifies the session files.

Usage:
  python3 -I mine_history.py [--days 60] [--root ~/.claude/projects] [--project SUBSTR]
                             [--out digest.md] [--json digest.json]

The digest gives Claude the evidence for three questions:
  1. Where does Claude go wrong?      -> correction prompts, interrupts, tool errors
  2. What do you explain twice?       -> sentences repeated across sessions
  3. What is done by hand repeatedly? -> similar opening prompts, recurring weekdays/times
Judgement (what is a real pattern, what deserves a skill) is left to Claude.
"""
import argparse, collections, datetime as dt, json, os, re, sys
from pathlib import Path

CORRECTION = re.compile(
    r"^\s*(no[,.! ]|nope|don'?t|do not|stop|wrong|that'?s (not|wrong)|not what|actually[, ]|"
    r"i (said|told you|asked)|again[,.!]|instead[, ]|why did you|you (forgot|missed|didn'?t)|"
    r"please (don'?t|stop|use)|undo|revert|that (broke|didn'?t work))",
    re.I)
INTERRUPT = "[Request interrupted by user"
SECRET = re.compile(r"(sk-[A-Za-z0-9_\-]{12,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|"
                    r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}|[A-Za-z0-9+/]{40,}={0,2})")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
TAGGED = re.compile(r"<([a-z][\w-]*)(?:\s[^>]*)?>.*?</\1>", re.S)  # system-reminder, side-sessions-event, pasted_content...
APP_NOTE = re.compile(r"\[(This command|The command|Use read_terminal)[^\]]*\]", re.S)
SPAWNED = re.compile(r"^(Task \(from the session that started this one\)|Background \(from the session)")
STOP = set("the a an and or to of in on for with is it this that be me my i you your we our can "
           "please just so as at by from are was will would should could do have has use make".split())


def clean(text):
    text = TAGGED.sub(" ", text)
    text = APP_NOTE.sub(" ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = SECRET.sub("[REDACTED]", text)
    text = EMAIL.sub("[email]", text)
    return re.sub(r"\s+", " ", text).strip()


def human_text(rec):
    """Return the human-typed text of a user record, or None."""
    if rec.get("type") != "user" or rec.get("isSidechain"):
        return None
    origin = rec.get("origin") or {}
    if isinstance(origin, dict) and origin.get("kind") not in (None, "human"):
        return None
    if rec.get("isMeta") or rec.get("isCompactSummary"):
        return None
    msg = rec.get("message") or {}
    content = msg.get("content")
    if isinstance(content, str):
        parts = [content]
    elif isinstance(content, list):
        if any(isinstance(c, dict) and c.get("type") == "tool_result" for c in content):
            return None
        parts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
    else:
        return None
    raw = " ".join(parts)
    if INTERRUPT in raw:
        return INTERRUPT
    t = clean(raw)
    return t or None


def tool_errors(rec):
    out = []
    msg = rec.get("message") or {}
    content = msg.get("content")
    if rec.get("type") == "user" and isinstance(content, list):
        for c in content:
            if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"):
                body = c.get("content")
                if isinstance(body, list):
                    body = " ".join(x.get("text", "") for x in body if isinstance(x, dict))
                out.append(clean(str(body))[:200])
    return out


def tool_uses(rec):
    msg = rec.get("message") or {}
    content = msg.get("content")
    names = []
    if rec.get("type") == "assistant" and isinstance(content, list):
        for c in content:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                name = c.get("name", "?")
                if name == "Skill":
                    name = "Skill:" + str((c.get("input") or {}).get("skill", "?"))
                names.append(name)
    return names


def words(t):
    return [w for w in re.findall(r"[a-z0-9']+", t.lower()) if w not in STOP and len(w) > 2]


def sentences(t):
    for s in re.split(r"(?<=[.!?])\s+|\n+", t):
        s = s.strip()
        if 6 <= len(s.split()) <= 60:
            yield s


def project_label(path, cwd):
    if cwd:
        p = cwd.replace(str(Path.home()), "~")
        if "scratch-workspaces" in p:
            return "(no folder)"
        return p
    return path.parent.name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path.home() / ".claude/projects"))
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--project", default="", help="only sessions whose cwd contains this text")
    ap.add_argument("--out", default="history-digest.md")
    ap.add_argument("--json", default="")
    ap.add_argument("--max-prompts", type=int, default=6, help="opening prompts listed per session")
    a = ap.parse_args()

    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.days)
    sessions = []
    for f in Path(a.root).rglob("*.jsonl"):
        if "subagents" in f.parts:
            continue
        try:
            if dt.datetime.fromtimestamp(f.stat().st_mtime, dt.timezone.utc) < cutoff:
                continue
        except OSError:
            continue
        s = {"file": str(f), "prompts": [], "errors": [], "tools": collections.Counter(),
             "interrupts": 0, "title": "", "cwd": "", "start": None}
        try:
            fh = open(f, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(rec, dict):
                    continue
                if rec.get("type") == "custom-title":
                    s["title"] = rec.get("customTitle", "")
                if rec.get("cwd") and not s["cwd"]:
                    s["cwd"] = rec["cwd"]
                ts = rec.get("timestamp")
                if ts and not s["start"]:
                    s["start"] = ts
                t = human_text(rec)
                if t == INTERRUPT:
                    s["interrupts"] += 1
                elif t:
                    s["prompts"].append(t)
                s["errors"] += tool_errors(rec)
                s["tools"].update(tool_uses(rec))
        if not s["prompts"]:
            continue
        if a.project and a.project.lower() not in (s["cwd"] or "").lower():
            continue
        s["project"] = project_label(f, s["cwd"])
        s["spawned"] = bool(SPAWNED.match(s["prompts"][0]))
        sessions.append(s)

    sessions.sort(key=lambda s: s["start"] or "")
    seen, uniq = set(), []
    for s in sessions:  # forked sessions repeat the parent's opening; keep the first
        key = (s["start"][:16] if s["start"] else "", s["prompts"][0][:200])
        if key not in seen:
            seen.add(key); uniq.append(s)
    sessions = uniq
    if not sessions:
        print("No sessions with human prompts found in range.", file=sys.stderr)
        sys.exit(1)

    # 1. corrections
    corrections = []
    for s in sessions:
        for i, p in enumerate(s["prompts"]):
            if i > 0 and CORRECTION.search(p):
                corrections.append((s["start"][:10], s["project"], p[:300]))

    # 2. repeated sentences across sessions (explained twice)
    sent_sessions = collections.defaultdict(set)
    sent_text = {}
    for idx, s in enumerate(sessions):
        prompts = s["prompts"][1:] if s["spawned"] else s["prompts"]
        for p in prompts:
            for sent in sentences(p):
                key = " ".join(words(sent))
                if len(key.split()) >= 4:
                    sent_sessions[key].add(idx)
                    sent_text.setdefault(key, sent)
    repeated = sorted(((len(v), sent_text[k]) for k, v in sent_sessions.items() if len(v) >= 2),
                      reverse=True)[:60]

    # 3. recurring jobs: cluster opening prompts by word overlap
    openers = [(i, s["prompts"][0]) for i, s in enumerate(sessions)]
    clusters = []
    for i, p in openers:
        ws = set(words(p)[:40])
        for c in clusters:
            inter = len(ws & c["words"])
            if ws and inter / max(1, min(len(ws), len(c["words"]))) >= 0.45 and inter >= 4:
                c["members"].append(i)
                c["words"] &= ws if len(c["words"] & ws) >= 4 else c["words"]
                break
        else:
            clusters.append({"words": ws, "members": [i]})
    recurring = [c for c in clusters if len(c["members"]) >= 2]
    recurring.sort(key=lambda c: -len(c["members"]))

    tool_total = collections.Counter()
    err_total = collections.Counter()
    for s in sessions:
        tool_total.update(s["tools"])
        for e in s["errors"]:
            err_total[re.sub(r"[\d/\\._-]{6,}", "…", e[:90])] += 1

    # write digest
    L = []
    L.append(f"# Claude Code history digest\n")
    L.append(f"- Sessions: {len(sessions)} (last {a.days} days, from {sessions[0]['start'][:10]} "
             f"to {sessions[-1]['start'][:10]})")
    L.append(f"- Human prompts: {sum(len(s['prompts']) for s in sessions)}; interrupts: "
             f"{sum(s['interrupts'] for s in sessions)}; tool errors: {sum(len(s['errors']) for s in sessions)}")
    proj = collections.Counter(s["project"] for s in sessions)
    L.append("- Projects: " + "; ".join(f"{p} ({n})" for p, n in proj.most_common(12)))
    L.append("\n## 1. Possible corrections (you pushing back mid-session)\n")
    L += [f"- {d} · {p} · \"{t}\"" for d, p, t in corrections[-80:]] or ["- none found"]
    L.append("\n## 2. Sentences repeated across sessions (explained more than once)\n")
    L += [f"- ×{n}: \"{t[:240]}\"" for n, t in repeated] or ["- none found"]
    L.append("\n## 3. Recurring jobs (similar opening prompts)\n")
    for c in recurring[:30]:
        ms = [sessions[i] for i in c["members"]]
        days = collections.Counter(dt.datetime.fromisoformat(m["start"].replace("Z", "+00:00")).strftime("%a")
                                   for m in ms if m["start"])
        L.append(f"### ×{len(ms)} · keywords: {', '.join(sorted(c['words'])[:12])}")
        L.append(f"- weekdays: {dict(days)}; projects: {sorted(set(m['project'] for m in ms))}")
        for m in ms[:5]:
            L.append(f"  - {m['start'][:16]} \"{m['prompts'][0][:220]}\"")
    if not recurring:
        L.append("- none found")
    L.append("\n## 4. Tool use and failures\n")
    L.append("- Most used: " + ", ".join(f"{k} {v}" for k, v in tool_total.most_common(25)))
    L.append("- Most common tool errors:")
    L += [f"  - ×{n}: {e}" for e, n in err_total.most_common(20)] or ["  - none"]
    L.append("\n## 5. Sessions (title · opening prompts)\n")
    for s in sessions:
        L.append(f"### {s['start'][:16]} · {s['project']} · {s['title'] or '(untitled)'}"
                 + (" · [started by another session]" if s["spawned"] else "")
                 + f" · prompts {len(s['prompts'])}, interrupts {s['interrupts']}, errors {len(s['errors'])}")
        for p in s["prompts"][: a.max_prompts]:
            L.append(f"- \"{p[:260]}\"")
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")

    if a.json:
        Path(a.json).write_text(json.dumps({
            "sessions": [{k: (dict(v) if isinstance(v, collections.Counter) else v)
                          for k, v in s.items()} for s in sessions],
            "corrections": corrections, "repeated": repeated,
        }, indent=1, default=str), encoding="utf-8")
    print(f"Wrote {a.out}: {len(sessions)} sessions, {len(corrections)} corrections, "
          f"{len(repeated)} repeated sentences, {len(recurring)} recurring clusters.")


if __name__ == "__main__":
    main()
