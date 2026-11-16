---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Create proof of concept for unknown/complex features (junior workflow). Explores feasibility in isolated docs folder, no production code. Use when the user says POC, proof of concept, prova, test idea, skus ci to pojde, or wants to experiment before committing.
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/j-setup` first).
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md`

## When to Use
Use this command when:
- Adding something NEW that you haven't done before
- Integrating an external library/API you don't know well
- The feature is complex and you're not sure how to approach it
- You want to experiment WITHOUT touching production code

**Better to experiment in POC than mess up real code!**

## Steps

### 1. Understand What's Needed
Ask user:
```
You want to try something new. Tell me:
- What do you want to achieve?
- What technology/library/API is involved?
- What's the unknown part you want to figure out?

When done, say "done".
```

### 2. Create POC Branch and Folder
- Check existing **folders** in `{@tasks}/` matching pattern `poc-NN-*`
- Use: `ls -d {@tasks}/poc-[0-9][0-9]-*/ 2>/dev/null | sort | tail -1`
- Extract number and increment, or start with 01 if none exist
- The base branch follows `@merge-strategy`: `gitflow` or `gitflow-simple` → `{@dev-branch}`; otherwise
  `{@main-branch}`
```bash
git checkout {base-branch}
git pull origin {base-branch}
git checkout -b poc/NN-description
mkdir -p {@tasks}/poc-NN-description
```
POC gets its own branch like every other piece of work — the user sees it on remote
and main stays clean. Lightweight: no MB state, no plan files, just the branch.

### 3. Research Phase
- Search for documentation
- Look at examples
- Check if similar POCs exist in `{@tasks}/`
- Use web search if needed

### 4. Simple Plan
Create `{@tasks}/poc-NN-description/README.md`:
```markdown
# POC: [description]

## Goal
What we want to verify/learn

## Questions to Answer
- [ ] Does X work with Y?
- [ ] How do we configure Z?
- [ ] What's the performance like?

## Approach
1. Step 1
2. Step 2
3. ...

## Results
(fill after POC)

## Conclusion
(fill after POC: YES we can use it / NO we need alternative)
```

### 5. Execute POC
- Create minimal code to test the concept
- Keep it simple - just enough to answer the questions
- NO need for tests, clean code, or perfect structure
- Document what you learn

### 6. Evaluate Results
```
POC completed!

GOAL: [what we wanted to verify]

RESULTS:
- Question 1: [answer]
- Question 2: [answer]

CONCLUSION:
[Can we use this? Yes/No/With modifications]

NEXT:
- If YES → ready to implement in real code with j-new-feature
- If NO → need alternative approach
```

### 7. Save POC
- Commit ONLY the POC folder (never `git add .` — it would stage unrelated working-tree files):
```bash
git add {@tasks}/poc-NN-description
git commit -m "poc(NN): description"
git push -u origin poc/NN-description
```
- Keep it for future reference (branch stays on remote, like feature branches)
- Update MB if relevant learnings
- Merging into the base branch is optional: do it if the README's findings are worth
  having on the base branch, otherwise the branch alone preserves them

## Rules
- POC code stays in `{@tasks}/poc-NN-description/`, NEVER in the project's source
- POC work happens on a `poc/NN-*` branch, NEVER directly on the base branch
- Commit only the POC folder — `git add .` is forbidden here
- Keep POC minimal - just enough to answer questions
- Document everything you learn
- If POC successful → start real feature with `j-new-feature`
- If POC fails → discuss alternatives before proceeding
- POC doesn't follow full workflow - no MB state tracking needed
