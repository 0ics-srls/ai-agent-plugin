---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Close/kill an idea with documented reasons and lessons learned. Use when user says kill the idea, chiudi l'idea, abbandona, drop it, zrus to — terminal decision, history is preserved.
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/startup-strategist.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.

## What This Command Does

Formally closes an idea that won't be pursued further. Documents the reasons and captures lessons learned so the same mistakes aren't repeated.

## Steps

### 1. Select Idea to Close

Read `ideas/registry.md`. Show the ideas that can still be closed (any status except `killed` and `pivoted`; a `parked` idea can be killed too).

Ask the user which idea to close. If they already specified one, confirm it.

### 2. Review the Idea's Journey

Read all existing files for this idea. Present a brief timeline:

```
IDEA-{NN}: "{title}"
Journey: captured -> evaluated ({score}/60) -> researched -> ...
Time in funnel: {approximate duration}
Work invested: {list of files/artifacts created}
```

### 3. Understand the Reason

Ask:
```
Why are we closing this idea?
```

Then classify into one of these categories:

| Reason | Description |
|---|---|
| **Market** | No real market, too small, too competitive |
| **Problem** | Problem isn't painful enough, or doesn't exist at scale |
| **Solution** | Can't build a viable solution, or competitors do it better |
| **Timing** | Too early, too late, or market conditions changed |
| **Resources** | Can't commit the time/money/team needed |
| **Passion** | Lost interest, not excited enough to push through hard times |
| **Pivot** | Idea evolved into something else (suggest `biz-pivot` instead) |

If the user says "pivot" - suggest using `biz-pivot` instead and stop.

### 4. Capture Lessons Learned

Ask:
```
Before we close this, what did we learn? Think about:

1. What was the most surprising finding during research/validation?
2. What assumption turned out to be wrong?
3. Is there anything here worth remembering for future ideas?
```

### 5. Create Close Record

Create or update `ideas/evaluations/{slug}.md` - add a closure section at the end:

```markdown
## Closure

- **Date**: {date}
- **Final status**: killed
- **Reason category**: {market|problem|solution|timing|resources|passion}
- **Reason detail**: {user's explanation}

### Lessons Learned
{captured lessons}

### What Carries Forward
{any research, contacts, insights that might be useful for future ideas}
```

### 6. Update Registry

- Change status to `killed`
- Add note: `Closed: {reason category} - {one-line reason} ({date})`

### 7. Summary

```
IDEA CLOSED

IDEA-{NN}: "{title}"
Status:  killed
Reason:  {reason category} - {detail}
Lessons: {1-2 key takeaways}

{if lessons are relevant to other active ideas}
Note: This insight might be relevant to IDEA-{XX} ({title}).
{/if}

The idea and all its research are preserved in ideas/ for future reference.
```

### 8. Update Memory Bank

Update activeContext.md with closure activity. If this was the current focus idea, clear productContext.md.

## Rules
- NEVER delete any files. Closing preserves everything - it just marks the idea as done.
- Be respectful. Killing an idea isn't failure - it's good judgment.
- If user seems to be closing out of frustration rather than reason, gently ask if they want to `biz-pivot` or just take a break instead.
- Connect lessons learned to other active ideas when relevant.
- If closing the last/only active idea, encourage `biz-capture` for new ideas rather than leaving on a negative note.
- Update Memory Bank with closure activity
