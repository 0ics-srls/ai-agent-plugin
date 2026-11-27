#!/usr/bin/env python3
"""The switch of the status line: it puts the key `statusLine` in a settings file of Claude Code, or
takes it out, and keeps the rest of the file as it is.

usage: install.py on|off|status [project|user]
       install.py default

Run in the project's root folder.
- project: `.claude/settings.local.json` — this project on this machine, not committed — with the
  absolute path of the project's `.claude/support/statusline/statusline.py`. Where the set is not in
  the project (a plugin), this scope is refused.
- user: `~/.claude/settings.json` — every repository of this user — with a copy of the script in
  `~/.claude/statusline-cvm.py`.
- no scope: the project when the set is in it, the user otherwise.
- default, for the setup: on, unless a status line is already set at any level or it was switched off
  in this project (`.claude/statusline.off`, which `off project` leaves).

A status line that is not ours is never replaced nor removed. Every answer is a line that starts with
`status line:`. Exit: 0 done or nothing to do, 1 refused (the line says why), 2 usage.
Standard library only, Python 3.9 and later.
"""

from __future__ import annotations

import io
import json
import shutil
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

USAGE = "usage: install.py on|off|status [project|user]\n       install.py default"
SAYS = "status line:"
KEY = "statusLine"
PROJECT_SCRIPT = Path(".claude/support/statusline/statusline.py")
USER_SCRIPT = Path(".claude/statusline-cvm.py")  # under the home
OUR_SCRIPTS = (PROJECT_SCRIPT.as_posix().removeprefix(".claude/"), USER_SCRIPT.name)  # what our command names
OFF_MARK = Path(".claude/statusline.off")  # `off project` leaves it: the setup's default respects it
EXIT_DONE, EXIT_REFUSED, EXIT_USAGE = 0, 1, 2


class Scope(Enum):
    PROJECT = "project"  # <project>/.claude/settings.local.json: this machine, not committed
    USER = "user"  # ~/.claude/settings.json: every repository of this user


class Owner(Enum):
    """Whose status line a settings file holds; the value is how `status` says it."""

    NONE = "off"
    OURS = "on"
    OTHER = "on (another status line)"


@dataclass(frozen=True)
class Target:
    """Where a scope's status line is written, and what it runs."""

    scope: Scope
    settings: Path  # the file that gets the key
    shown: str  # that file, as the answers name it
    script: Path  # the script the command runs
    command: str  # the whole command line


@dataclass(frozen=True)
class Level:
    """A settings file Claude Code reads, highest first."""

    name: str
    settings: Path
    shown: str


class Refused(Exception):
    """The switch did nothing, and its message says why."""


def interpreter() -> str:
    """The Python the status line's command names: the one found on the PATH."""
    return "python3" if shutil.which("python3") else "python"


def target(scope: Scope, project: Path, home: Path) -> Target:
    if scope is Scope.PROJECT:
        script = (project / PROJECT_SCRIPT).absolute()
        return Target(
            scope=scope,
            settings=project / ".claude" / "settings.local.json",
            shown=".claude/settings.local.json",
            script=script,
            command=f'{interpreter()} "{script.as_posix()}"',
        )
    return Target(
        scope=scope,
        settings=home / ".claude" / "settings.json",
        shown="~/.claude/settings.json",
        script=home / USER_SCRIPT,
        command=f"{interpreter()} ~/{USER_SCRIPT.as_posix()}",
    )


def levels(project: Path, home: Path) -> tuple[Level, ...]:
    """The three files that can hold a status line, in the order Claude Code prefers them."""
    return (
        Level("local", project / ".claude" / "settings.local.json", ".claude/settings.local.json"),
        Level("project", project / ".claude" / "settings.json", ".claude/settings.json"),
        Level("user", home / ".claude" / "settings.json", "~/.claude/settings.json"),
    )


def default_scope(project: Path) -> Scope:
    return Scope.PROJECT if (project / PROJECT_SCRIPT).is_file() else Scope.USER


def read_settings(path: Path, shown: str) -> dict[str, object]:
    """The settings of a file, `{}` when it is missing; the tree is the user's and is kept as it is."""
    if not path.exists():
        return {}
    try:
        tree: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise Refused(f"kept — {shown} cannot be read as JSON ({error})") from error
    if not isinstance(tree, dict):
        raise Refused(f"kept — {shown} is not a JSON object")
    return tree


def owner_of(settings: dict[str, object]) -> Owner:
    """Whose status line the settings hold: the one function that looks inside the key."""
    if KEY not in settings:
        return Owner.NONE
    status_line = settings[KEY]
    command = status_line.get("command") if isinstance(status_line, dict) else None
    if isinstance(command, str) and any(script in command for script in OUR_SCRIPTS):
        return Owner.OURS
    return Owner.OTHER


def write_settings(path: Path, settings: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def turn_on(where: Target, project: Path) -> str:
    settings = read_settings(where.settings, where.shown)
    if owner_of(settings) is Owner.OTHER:
        raise Refused(f"kept — {where.shown} has another status line, and it is not replaced")
    if where.scope is Scope.PROJECT and not where.script.is_file():
        raise Refused(
            f"not turned on — {PROJECT_SCRIPT.as_posix()} is not in this project (the set is a plugin): use: on user"
        )
    if where.scope is Scope.USER:
        where.script.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path(__file__).resolve().parent / PROJECT_SCRIPT.name, where.script)
    else:
        (project / OFF_MARK).unlink(missing_ok=True)
    wanted: dict[str, object] = {"type": "command", "command": where.command, "padding": 0}
    if settings.get(KEY) != wanted:
        settings[KEY] = wanted
        write_settings(where.settings, settings)
    return f"on ({where.scope.value}) — {where.shown}"


def turn_off(where: Target, project: Path) -> str:
    settings = read_settings(where.settings, where.shown)
    owner = owner_of(settings)
    if owner is Owner.OTHER:
        raise Refused(f"kept — {where.shown} has another status line, and it is not removed")
    if owner is Owner.OURS:
        del settings[KEY]
        write_settings(where.settings, settings)
    if where.scope is Scope.USER:
        where.script.unlink(missing_ok=True)
    else:
        (project / OFF_MARK).parent.mkdir(parents=True, exist_ok=True)
        (project / OFF_MARK).write_text("", encoding="utf-8")
    return f"off ({where.scope.value})"


def status(project: Path, home: Path) -> list[str]:
    """One line per level, then the level Claude Code uses: the highest that has a status line."""
    lines = []
    used = ""
    for level in levels(project, home):
        owner = owner_of(read_settings(level.settings, level.shown))
        lines.append(f"{level.name} ({level.shown}) — {owner.value}")
        if owner is not Owner.NONE and not used:
            used = level.name
    lines.append(f"Claude Code uses {used}" if used else "off")
    return lines


def default(project: Path, home: Path) -> str:
    """What the setup asks: on, unless somebody already decided."""
    if (project / OFF_MARK).exists():
        return f"not turned on — switched off in this project ({OFF_MARK.as_posix()})"
    for level in levels(project, home):
        if owner_of(read_settings(level.settings, level.shown)) is not Owner.NONE:
            return f"kept — {level.shown} already has a status line"
    return turn_on(target(default_scope(project), project, home), project)


def answer(args: list[str], project: Path, home: Path) -> list[str] | None:
    """The lines the switch says for a command line; None when the command line is not one of ours."""
    if args == ["default"]:
        return [default(project, home)]
    if not args or len(args) > 2 or args[0] not in ("on", "off", "status"):
        return None
    if len(args) == 2 and args[1] not in (Scope.PROJECT.value, Scope.USER.value):
        return None
    if args[0] == "status":
        return status(project, home)
    scope = Scope(args[1]) if len(args) == 2 else default_scope(project)
    where = target(scope, project, home)
    return [turn_on(where, project) if args[0] == "on" else turn_off(where, project)]


def main() -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        lines = answer(sys.argv[1:], Path.cwd(), Path.home())
    except Refused as refused:
        print(f"{SAYS} {refused}")
        return EXIT_REFUSED
    if lines is None:
        print(USAGE)
        return EXIT_USAGE
    for line in lines:
        print(f"{SAYS} {line}")
    return EXIT_DONE


if __name__ == "__main__":
    sys.exit(main())
