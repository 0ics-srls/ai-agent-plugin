#!/usr/bin/env python3
"""Claude Code status line: the git branch, the model, and the CVM's progress while a plan runs.

Claude Code starts this script with the session as JSON on stdin and shows the one line it prints.
While the CVM planexecutor executes a plan of the project, the line has a bar: the completed blocks,
the current block N/M with its id, and the phase the planexecutor's log says — for a TDDAB plan and
for a Step plan. With no execution, or a completed one, the branch and the model alone.

The files of `.cvm/` are the CVM's: each is read once, by a reader that maps it into the types below.
Standard library only, Python 3.9 and later. It exits 0 on every path: a status line that fails
blanks the terminal's line.
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

BAR_WIDTH = 14
ERROR_WIDTH = 60
PLANEXECUTOR = "planexecutor"
RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"
ORANGE = "\033[38;5;166m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"


class PlanType(Enum):
    TDDAB = "tddab"
    STEP = "step"


class Phase(Enum):
    """Where the planexecutor is in a block; the value is the label shown in brackets."""

    STARTING = "starting"
    RED = "RED"
    GREEN = "GREEN"
    EXECUTE = "EXECUTE"
    VERIFY = "VERIFY"
    FIX = "FIX"
    CROSS_CHECK = "CROSS-CHECK"
    COMMIT = "MB+COMMIT"
    NEXT = "next block"
    FINAL = "FINAL REVIEW"


PHASE_COLOUR = {
    Phase.RED: RED,
    Phase.GREEN: GREEN,
    Phase.EXECUTE: GREEN,
    Phase.VERIFY: CYAN,
    Phase.FIX: YELLOW,
    Phase.CROSS_CHECK: CYAN,
    Phase.COMMIT: GREEN,
    Phase.FINAL: CYAN,
}


@dataclass(frozen=True)
class Rule:
    """A line of the planexecutor's log, and the phase it means."""

    prefix: str  # how the line starts
    phase: Phase
    passed: str = ""  # when set, `phase` holds only if the text after the first ":" has it
    failed: Phase = Phase.FIX  # ... and this one otherwise


# The lines both kinds of plan log, then each kind's own. The first rule whose prefix matches wins.
COMMON: tuple[Rule, ...] = (
    Rule("=== ALL ", Phase.FINAL),
    Rule("Block ", Phase.NEXT),  # "Block <id> COMPLETED (n/m)"
    Rule("Fix attempt", Phase.FIX),
)
RULES: dict[PlanType, tuple[Rule, ...]] = {
    PlanType.TDDAB: (
        *COMMON,
        Rule("=== Block ", Phase.RED),
        Rule("RED done", Phase.GREEN),
        Rule("GREEN done", Phase.VERIFY),
        Rule("VERIFY result", Phase.CROSS_CHECK, passed="passed"),
        Rule("RE-VERIFY result", Phase.CROSS_CHECK, passed="passed"),
        Rule("CROSS-CHECK invalid", Phase.CROSS_CHECK),
        Rule("CROSS-CHECK result", Phase.COMMIT, passed="passed=true"),
        Rule("CROSS-CHECK failed", Phase.FIX),
        Rule("CROSS-CHECK re-verify failed", Phase.FIX),
    ),
    PlanType.STEP: (
        *COMMON,
        Rule("=== Block ", Phase.EXECUTE),
        Rule("EXECUTE done", Phase.VERIFY),
        Rule("VERIFY result", Phase.COMMIT, passed="passed"),
        Rule("RE-VERIFY result", Phase.COMMIT, passed="passed"),
    ),
}


@dataclass(frozen=True)
class Session:
    """What Claude Code says of the session."""

    project: Path
    model: str  # "" when the session does not say


@dataclass(frozen=True)
class Execution:
    """The planexecutor's current execution, not completed."""

    plan_type: PlanType
    progress: tuple[int, int] | None  # (current, total); None when it is not "N/M"
    state: str
    log: tuple[str, ...]
    error: str  # "" when there is none


@dataclass(frozen=True)
class Plan:
    """The plan the CVM parsed last, and the blocks it marked completed."""

    block_ids: tuple[str, ...]
    done_ids: frozenset[str]  # the ids of uplan-progress.json, whoever's they are


# ------------------------------------------------------------------ the readers
# The only functions that see a parsed tree. A file that is missing, unreadable or of the wrong kind
# is read as missing: the line is drawn with what is there.


def _load(path: Path) -> object:
    try:
        tree: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return tree


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _fraction(text: str) -> tuple[int, int] | None:
    current, slash, total = text.partition("/")
    if not slash or not current.isdigit() or not total.isdigit():
        return None
    return int(current), int(total)


def read_session(text: str) -> Session:
    try:
        tree: object = json.loads(text)
    except ValueError:
        tree = None
    if not isinstance(tree, dict):
        return Session(Path(), "")
    workspace = tree.get("workspace")
    project = _text(workspace.get("project_dir")) if isinstance(workspace, dict) else ""
    model = tree.get("model")
    return Session(
        project=Path(project or _text(tree.get("cwd")) or "."),
        model=_text(model.get("display_name")) if isinstance(model, dict) else "",
    )


def read_execution(cvm: Path) -> Execution | None:
    metadata = _load(cvm / "metadata.json")
    current = _text(metadata.get("currentExecutionId")) if isinstance(metadata, dict) else ""
    if not current:
        return None
    run = _load(cvm / "executions" / f"{current}.json")
    if not isinstance(run, dict) or run.get("programId") != PLANEXECUTOR:
        return None
    if run.get("state") == "COMPLETED" or run.get("status") == "complete":
        return None
    variables = run.get("variables")
    plan_type = _text(variables.get("planType")) if isinstance(variables, dict) else ""
    progress = _text(variables.get("progress")) if isinstance(variables, dict) else ""
    output = run.get("output")
    return Execution(
        plan_type=PlanType.STEP if plan_type == PlanType.STEP.value else PlanType.TDDAB,
        progress=_fraction(progress),
        state=_text(run.get("state")) or "?",
        log=tuple(_text(line) for line in output) if isinstance(output, list) else (),
        error=_text(run.get("error")),
    )


def read_plan(cvm: Path) -> Plan:
    plan = _load(cvm / "uplan.json")
    blocks = plan.get("blocks") if isinstance(plan, dict) else None
    done = _load(cvm / "uplan-progress.json")
    return Plan(
        block_ids=tuple(
            _text(block.get("id")) for block in blocks if isinstance(block, dict)
        ) if isinstance(blocks, list) else (),
        done_ids=frozenset(_text(done_id) for done_id in done) if isinstance(done, list) else frozenset(),
    )


def read_branch(project: Path) -> str:
    """The branch of the project's repository; "" outside one, or without git."""
    try:
        git = subprocess.run(
            ["git", "-C", str(project), "branch", "--show-current"],
            capture_output=True, text=True, timeout=1, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return git.stdout.strip()


# ------------------------------------------------------------------ the line


def phase_of(log: tuple[str, ...], plan_type: PlanType) -> Phase:
    """The last line of the log that a rule knows decides."""
    for line in reversed(log):
        for rule in RULES[plan_type]:
            if line.startswith(rule.prefix):
                if not rule.passed:
                    return rule.phase
                verdict = line.split(":", 1)[-1].lower()
                return rule.phase if rule.passed in verdict else rule.failed
    return Phase.STARTING


def done_count(plan: Plan, current: int) -> int:
    """The completed blocks of this plan; by the current block when the progress is another plan's."""
    ours = plan.done_ids.intersection(plan.block_ids)
    if ours or plan.done_ids.issubset(plan.block_ids):
        return len(ours)
    return max(current - 1, 0)


def bar(done: int, total: int) -> str:
    filled = min(round(BAR_WIDTH * done / total), BAR_WIDTH) if total else 0
    return f"{ORANGE}{'█' * filled}{DIM}{'░' * (BAR_WIDTH - filled)}{RESET}"


def cvm_part(execution: Execution, plan: Plan) -> str:
    if execution.progress is None:
        return f"{DIM}cvm: {execution.state}{RESET}"
    current, total = execution.progress
    block_id = plan.block_ids[current - 1] if 0 < current <= len(plan.block_ids) else "?"
    phase = phase_of(execution.log, execution.plan_type)
    error = execution.error
    if len(error) > ERROR_WIDTH:
        error = error[:ERROR_WIDTH] + "…"
    shown_error = f" {RED}✗ {error}{RESET}" if error else ""
    return (
        f"{bar(done_count(plan, current), total)} {BOLD}{current}/{total}{RESET} {block_id} "
        f"{PHASE_COLOUR.get(phase, DIM)}[{phase.value}]{RESET}{shown_error}"
    )


def render(session: Session, branch: str, execution: Execution | None, plan: Plan) -> str:
    parts = []
    if branch:
        parts.append(f"{DIM}⎇ {branch}{RESET}")
    if session.model:
        parts.append(f"{DIM}{session.model}{RESET}")
    if execution is not None:
        parts.append(cvm_part(execution, plan))
    return "  ".join(parts)


def main() -> None:
    # The system's encoding on Windows (cp1252) cannot write the bar, and the session is UTF-8.
    for stream in (sys.stdin, sys.stdout):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8")
    session = read_session(sys.stdin.read())
    cvm = session.project / ".cvm"
    print(render(session, read_branch(session.project), read_execution(cvm), read_plan(cvm)))


if __name__ == "__main__":
    main()
