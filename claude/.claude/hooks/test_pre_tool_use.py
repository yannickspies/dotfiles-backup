"""Tests for the Bash PreToolUse guard.

Run from the hooks dir:

    PYTHONDONTWRITEBYTECODE=1 uv run --python 3.12 --with pytest \
        pytest -q -p no:cacheprovider test_pre_tool_use.py

The guard must never write a file: one test snapshots the hooks dir, runs the
guard as a subprocess, and asserts nothing appeared. The env var keeps pytest's
own bytecode cache out of the directory.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.dont_write_bytecode = True

HOOKS_DIR = Path(__file__).resolve().parent
SCRIPT = HOOKS_DIR / "pre_tool_use.py"

_spec = importlib.util.spec_from_file_location("pre_tool_use", SCRIPT)
guard = importlib.util.module_from_spec(_spec)
sys.modules["pre_tool_use"] = guard  # dataclasses resolve annotations via sys.modules
_spec.loader.exec_module(guard)

HOME = "/home/u"
PROJ = "/home/u/proj"


def ctx(cwd: str = PROJ, project_dir: str = PROJ) -> "guard.Ctx":
    return guard.Ctx(
        cwd=cwd,
        project_dir=project_dir,
        home=HOME,
        tmp_roots=("/tmp",),
        env={"HOME": HOME, "CLAUDE_PROJECT_DIR": project_dir},
    )


ALLOW = [
    # plain deletions inside the project
    ("rm -rf dist", PROJ),
    ("rm -r ./build", PROJ),
    ("rm -rf node_modules/*", PROJ),
    ("rm -rf ./*", PROJ),
    ("rm dist/a.txt dist/b.txt", PROJ),
    ("rm -rf -- -weird-name", PROJ),
    ("rm -rf dist 2>/dev/null", PROJ),
    # not rm at all
    ("git rm -r --cached tasks/", PROJ),
    ("git clean -fdx", PROJ),
    ("git reset --hard origin/main", PROJ),
    ('python3 -c "import shutil; shutil.rmtree(\'dist\')"', PROJ),
    ("find / -name x", PROJ),
    ("rsync -a / backup/", PROJ),
    # text that only mentions rm
    ('echo "rm -rf /" > notes.txt', PROJ),
    ('grep -n "rm -rf" hooks/pre_tool_use.py', PROJ),
    ("cat <<'EOF' > n.txt\nrm -rf /\nEOF", PROJ),
    ("cat <<EOF\nsudo rm -rf ~\nEOF\necho done", PROJ),
    # find / rsync inside the project
    ("find . -name '*.log' -delete", PROJ),
    ("find . -name x -exec rm -rf {} +", PROJ),
    ("find dist -depth -delete", PROJ),
    ("rsync -a --delete src/ dist/", PROJ),
    ("rsync -a --delete --exclude .git src/ dist/", PROJ),
    # tmp and the memory dir are zones
    ("rm -rf /tmp/claude-1000/foo", PROJ),
    ("rm -rf /tmp/x/*", PROJ),
    ("rm /home/u/.claude/projects/x/memory/y.md", PROJ),
    ("rm ~/.claude/projects/x/memory/y.md", PROJ),
    # cd tracking
    ("cd /tmp && rm -rf build", PROJ),
    ("cd apps/foo && rm -rf ..", PROJ),
    ("(cd /tmp && rm -rf a); rm -rf b", PROJ),
    ("cd /tmp; cd - ; echo x", PROJ),
    # unbalanced quotes with nothing dangerous
    ('echo "hello', PROJ),
    ('rm -rf "dist', PROJ),
    ('rm -rf a && echo "x', PROJ),
    # session launched from home: tmp still works
    ("rm -rf /tmp/scratch", HOME),
]

BLOCK = [
    ("rm -rf /", PROJ),
    ("rm -rf //", PROJ),
    ("rm -rf /*", PROJ),
    ("sudo rm -rf /var", PROJ),
    ("sudo -u root rm -rf /var", PROJ),
    ("/bin/rm -rf /etc", PROJ),
    ("\\rm -rf /opt", PROJ),
    ("env FOO=1 rm -rf /srv", PROJ),
    ("FOO=1 rm -rf /srv", PROJ),
    ("nohup rm -rf /srv", PROJ),
    ("rm -rf ~/x", PROJ),
    ("rm -rf ~", PROJ),
    ("rm -rf ~/", PROJ),
    ("rm -rf $HOME", PROJ),
    ('rm -rf "$HOME/x"', PROJ),
    ("rm -rf ${HOME}", PROJ),
    ("rm ~/.bashrc", PROJ),
    ("rm -rf ../..", PROJ),
    ("rm -rf ..", PROJ),
    ("rm -rf .", PROJ),
    ("rm -rf $CLAUDE_PROJECT_DIR", PROJ),
    ("rm -rf /home/u/proj", PROJ),
    ("rm -rf /home/u/projects", PROJ),
    ("rm -rf /home/other/x", PROJ),
    ("rm -rf *", HOME),
    ("rm -rf .", HOME),
    ("rm -rf ..", HOME),
    ("rm -rf *", "/"),
    ("cd ~ && rm -rf *", PROJ),
    ("cd .. && rm -rf proj", PROJ),
    ("cd /tmp && rm -rf ..", PROJ),
    ("rm -rf /tmp", PROJ),
    ("cd $X && rm -rf build", PROJ),
    ("rm -rf $UNSET/foo", PROJ),
    ("rm -rf $(pwd)", PROJ),
    ("rm -rf `pwd`", PROJ),
    ("cd - && rm -rf build", PROJ),
    ("find / -delete", PROJ),
    ("find ~ -delete", PROJ),
    ("find . -delete", HOME),
    ("find /etc -name x -exec rm {} ;", PROJ),
    ("rsync -a --delete / backup/", PROJ),
    ("rsync -a --delete src/ ~/", PROJ),
    ('bash -c "rm -rf /"', PROJ),
    ("sh -c 'cd /tmp && rm -rf ..'", PROJ),
    ('eval "rm -rf ~"', PROJ),
    ('echo "rm -rf /', PROJ),  # unbalanced quote: documented fallback false positive
    # session launched from home: home is not a zone
    ("rm -rf x", HOME),
    ("rm -rf ~/x", HOME),
]


@pytest.mark.parametrize("command,cwd", ALLOW, ids=[c for c, _ in ALLOW])
def test_allowed(command: str, cwd: str) -> None:
    project_dir = HOME if cwd == HOME else PROJ
    assert guard.evaluate(command, ctx(cwd=cwd, project_dir=project_dir)) is None


@pytest.mark.parametrize("command,cwd", BLOCK, ids=[c for c, _ in BLOCK])
def test_blocked(command: str, cwd: str) -> None:
    project_dir = HOME if cwd == HOME else PROJ
    reason = guard.evaluate(command, ctx(cwd=cwd, project_dir=project_dir))
    assert reason, f"expected a block reason for {command!r}"


def test_block_reason_names_the_resolved_path() -> None:
    reason = guard.evaluate("rm -rf ~/x", ctx())
    assert "'~/x'" in reason and "/home/u/x" in reason and "home dir" in reason


def _run(payload: object, **env_overrides: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "HOME": HOME, "CLAUDE_PROJECT_DIR": PROJ, "PYTHONDONTWRITEBYTECODE": "1"}
    env.update(env_overrides)
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )


def test_subprocess_blocks_with_exit_2() -> None:
    result = _run({"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}, "cwd": PROJ})
    assert result.returncode == 2
    assert result.stderr.startswith("BLOCKED:")


def test_subprocess_allows_safe_command() -> None:
    result = _run({"tool_name": "Bash", "tool_input": {"command": "rm -rf dist"}, "cwd": PROJ})
    assert result.returncode == 0
    assert result.stderr == ""


def test_subprocess_ignores_other_tools() -> None:
    result = _run({"tool_name": "Read", "tool_input": {"file_path": "/etc/passwd"}, "cwd": PROJ})
    assert result.returncode == 0


def test_subprocess_survives_garbage_input() -> None:
    result = _run("not json")
    assert result.returncode == 0
    assert "warning" in result.stderr


def _tree(root: Path) -> list[str]:
    return sorted(str(p.relative_to(root)) for p in root.rglob("*"))


def test_guard_writes_no_files() -> None:
    # pytest may have cached its own rewritten test module before this runs;
    # the snapshot is taken after that, so only the guard's writes would show.
    before = _tree(HOOKS_DIR)
    _run({"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}, "cwd": PROJ})
    _run({"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": PROJ})
    _run("not json")
    assert _tree(HOOKS_DIR) == before


GIT_ASK = [
    "git reset --hard origin/main",
    "git checkout -- src/a.ts",
    "git checkout .",
    "git checkout -f main",
    "git restore src/a.ts",
    "git restore --worktree --staged a.ts",
    "git switch --discard-changes main",
    "git switch -C feat",
    "git clean -fdx",
    "git clean --force",
    "git push --force",
    "git push -f origin feat",
    "git push origin +feat",
    "git push --force-with-lease origin main",
    "git push --force-with-lease origin HEAD:refs/heads/main",
    "git branch -D feat",
    "git branch -d -f feat",
    "git branch --delete --force feat",
    "git stash drop",
    "git stash clear",
    "git reflog expire --expire=now --all",
    "git update-ref -d refs/heads/x",
    "git rm -rf src",
    "git -C ../wt reset --hard",
    "cd ../wt && git reset --hard",
    "sudo git clean -f",
    'bash -c "git reset --hard"',
    'eval "git stash clear"',
]

GIT_OK = [
    "git status",
    "git reset HEAD~1",
    "git reset --soft HEAD~1",
    "git checkout main",
    "git checkout -b feat",
    "git restore --staged a.ts",
    "git switch -c feat",
    "git clean -n",
    "git push",
    "git push -u origin feat",
    "git push --force-with-lease origin feat",
    "git branch -d feat",
    "git stash",
    "git stash pop",
    "git reflog",
    "git rm -r --cached tasks/",
    "git worktree remove ../wt",
    "git worktree prune",
    "git merge --abort",
    "git commit --amend --no-edit",
    'git commit -m "git reset --hard"',
    'echo "git push --force"',
]


def _git_hits(command: str) -> list[str]:
    hits: list[str] = []
    assert guard.evaluate(command, ctx(), git_hits=hits) is None
    return hits


@pytest.mark.parametrize("command", GIT_ASK)
def test_git_asks(command: str) -> None:
    assert _git_hits(command), f"expected an ask for {command!r}"


@pytest.mark.parametrize("command", GIT_OK)
def test_git_ok(command: str) -> None:
    assert _git_hits(command) == []


def test_deletion_block_wins_over_git_ask() -> None:
    hits: list[str] = []
    assert guard.evaluate("git clean -f && rm -rf /", ctx(), git_hits=hits)


def test_subprocess_asks_on_destructive_git() -> None:
    result = _run({"tool_name": "Bash", "tool_input": {"command": "git reset --hard"}, "cwd": PROJ})
    assert result.returncode == 0
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["permissionDecision"] == "ask"
    assert "reset --hard" in output["permissionDecisionReason"]


def test_subprocess_silent_on_safe_git() -> None:
    result = _run({"tool_name": "Bash", "tool_input": {"command": "git branch -d feat"}, "cwd": PROJ})
    assert result.returncode == 0
    assert result.stdout == ""
