import pytest
from llm_fragments_tmux import parse_tmux_fragment_argument, Args
import subprocess
import time
from collections import namedtuple


@pytest.fixture(scope="function")
def tmux_session_factory():
    sessions = []

    def _create_tmux_session(session_name):
        create_tmux_session(session_name)
        sessions.append(session_name)
        time.sleep(3)  # Wait for tmux to process the commands

    yield _create_tmux_session

    # Cleanup: kill all created sessions
    for session_name in sessions:
        kill_tmux_session(session_name)


def run_command(cmd, check=True, **kwargs):
    """Helper to run a tmux command via subprocess."""
    return subprocess.run(cmd, shell=True, check=check, **kwargs)


def create_tmux_session(session_name):
    """Create a new tmux session with the given name in Bash, without a prompt."""
    run_command(
        f"tmux new-session -d -s {session_name} 'PS1=\"\" exec bash --norc '",
        check=False,
    )


def kill_tmux_session(session_name):
    run_command(f"tmux kill-session -t {session_name}", check=False)


def send_tmux_command(session_name, command):
    run_command(f"tmux send-keys -t {session_name} '{command}' C-m")


# Refactor for test_parse_tmux_fragment_argument_valid
ParseTmuxFragmentTest = namedtuple(
    "ParseTmuxFragmentTest",
    ("argument", "expected"),
)


@pytest.mark.parametrize(
    ParseTmuxFragmentTest._fields,
    [
        ParseTmuxFragmentTest("", [Args()]),
        ParseTmuxFragmentTest(
            "1,2:20,hoge:20,5",
            [
                Args(pane="1", lines=None),
                Args(pane="2", lines=20),
                Args(pane="hoge", lines=20),
                Args(pane="5", lines=None),
            ],
        ),
        ParseTmuxFragmentTest("1:20", [Args(pane="1", lines=20)]),
        ParseTmuxFragmentTest(
            "1,2:", [Args(pane="1", lines=None), Args(pane="2", lines=None)]
        ),
        ParseTmuxFragmentTest(":20", [Args(pane=None, lines=20)]),
        ParseTmuxFragmentTest(
            "1,2", [Args(pane="1", lines=None), Args(pane="2", lines=None)]
        ),
        ParseTmuxFragmentTest("20", [Args(pane="20", lines=None)]),
    ],
)
def test_parse_tmux_fragment_argument_valid(argument, expected):
    assert parse_tmux_fragment_argument(argument) == expected


@pytest.mark.parametrize(
    "argument",
    [
        "1,2:abc",
        ":xyz",
        "1:!@#",
    ],
)
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
        TmuxFragmentParamTest(
            ["echo hello world from tmux"],
            "",
            [
                "<tmux pane=test_session_cmds0--expected_lines0 lines=all>",
                "echo hello world from tmux",
                "hello world from tmux",
                "</tmux>",
            ],
        ),
        TmuxFragmentParamTest(
            ["echo line1", "echo line2", "echo line3"],
            "2",
            [
                "<tmux pane=test_session_cmds1-2-expected_lines1 lines=2>",
                "echo line3",
                "line3",
                "</tmux>",
            ],
        ),
        TmuxFragmentParamTest(
            ["echo lineA", "echo lineB", "echo lineC", "echo lineD"],
            "3",
            [
                "<tmux pane=test_session_cmds2-3-expected_lines2 lines=3>",
                "lineC",
                "echo lineD",
                "lineD",
                "</tmux>",
            ],
        ),
    ],
)
def test_tmux_fragment_parametrized(
    tmux_session_factory, cmds, fragment_arg, expected_lines, request
):
    # add a unique session name to avoid conflicts
    session_name = f"test_session_{request.node.callspec.id}"
    tmux_session_factory(session_name)

    for cmd in cmds:
        send_tmux_command(session_name, cmd)

    result = subprocess.run(
        ["llm", "fragments", "show", f"tmux:{session_name}:{fragment_arg}"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output_lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert output_lines == expected_lines
