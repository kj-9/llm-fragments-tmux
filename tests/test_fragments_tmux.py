import pytest
from llm_fragments_tmux import parse_tmux_fragment_argument
import subprocess
import time
from collections import namedtuple

@pytest.fixture
def tmux_session_factory():
    created_sessions = []

    def _create(commands):
        session_name = f"llmfragtest{int(time.time() * 1000)}"
        create_tmux_session(session_name)
        for cmd in commands:
            send_tmux_command(session_name, cmd)
        created_sessions.append(session_name)
        return session_name

    yield _create

    # Cleanup: kill all created sessions
    for session_name in created_sessions:
        kill_tmux_session(session_name)


def run_tmux_command(cmd, check=True, **kwargs):
    """Helper to run a tmux command via subprocess."""
    return subprocess.run(cmd, shell=True, check=check, **kwargs)

def create_tmux_session(session_name):
    run_tmux_command(f"tmux new-session -d -s {session_name}")

def kill_tmux_session(session_name):
    run_tmux_command(f"tmux kill-session -t {session_name}", check=False)

def send_tmux_command(session_name, command):
    run_tmux_command(f"tmux send-keys -t {session_name} '{command}' C-m")

# Refactor for test_parse_tmux_fragment_argument_valid
ParseTmuxFragmentTest = namedtuple(
    "ParseTmuxFragmentTest",
    ("argument", "expected"),
)

@pytest.mark.parametrize(
    ParseTmuxFragmentTest._fields,
    [
        ParseTmuxFragmentTest("", [{"pane": None, "lines": None}]),
        ParseTmuxFragmentTest("1,2:20,hoge:20,5", [{"pane": "1", "lines": None}, {"pane": "2", "lines": 20}, {"pane": "hoge", "lines": 20}, {"pane": "5", "lines": None}]),
        ParseTmuxFragmentTest("1:20", [{"pane": "1", "lines": 20}]),
        ParseTmuxFragmentTest("1,2:", [{"pane": "1", "lines": None}, {"pane": "2", "lines": None}]),
        ParseTmuxFragmentTest(":20", [{"pane": None, "lines": 20}]),
        ParseTmuxFragmentTest("1,2", [{"pane": "1", "lines": None}, {"pane": "2", "lines": None}]),
        ParseTmuxFragmentTest("20", [{"pane": "20", "lines": None}]),
    ],
)
def test_parse_tmux_fragment_argument_valid(argument, expected):
    assert parse_tmux_fragment_argument(argument) == expected

@pytest.mark.parametrize("argument", [
    "1,2:abc",
    ":xyz",
    "1:!@#",
])
def test_parse_tmux_fragment_argument_invalid(argument):
    with pytest.raises(ValueError):
        parse_tmux_fragment_argument(argument)


# Refactor for test_tmux_fragment_parametrized
TmuxFragmentParamTest = namedtuple(
    "TmuxFragmentParamTest",
    ("cmds", "fragment_arg", "expected_lines"),
)

@pytest.mark.parametrize(
    TmuxFragmentParamTest._fields,
    [
        TmuxFragmentParamTest(["echo hello world from tmux"], "0", ["echo hello world from tmux"]),
        TmuxFragmentParamTest(["echo line1", "echo line2", "echo line3"], "2", ["echo line2", "echo line3"]),
        TmuxFragmentParamTest(["echo lineA", "echo lineB", "echo lineC", "echo lineD"], "3", ["echo lineB", "echo lineC", "echo lineD"]),
    ],
)
def test_tmux_fragment_parametrized(tmux_session_factory, cmds, fragment_arg, expected_lines):
    session_name = tmux_session_factory(cmds)
    time.sleep(0.5)
    result = subprocess.run([
        "llm", "fragments", "show", f"tmux:{session_name}:{fragment_arg}"
    ], capture_output=True, text=True)

    assert result.returncode == 0
    output_lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert output_lines == expected_lines

