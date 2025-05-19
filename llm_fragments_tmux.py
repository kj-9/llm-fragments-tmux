import llm
import subprocess
from typing import List
from dataclasses import dataclass


@dataclass
class Args:
    pane: str | None = None
    lines: int | None = None


def parse_tmux_fragment_argument(
    argument_string: str,
) -> list[Args]:
    if not argument_string.strip():
        return [Args()]

    args = []

    # Split the argument string by commas
    argument_parts = argument_string.split(",")
    for part in argument_parts:
        # Split each part by colon
        pane_part, sep, line_value = part.partition(":")
        line_part = line_value if sep else None

        args.append(
            Args(
                pane=pane_part if pane_part else None,
                lines=int(line_part) if line_part else None,
            )
        )

    return args


@llm.hookimpl
def register_fragment_loaders(register):
    """Register the tmux fragment loader"""
    register("tmux", tmux_loader_function)


def tmux_loader_function(argument: str) -> List[llm.Fragment]:
    try:
        args = parse_tmux_fragment_argument(argument)
    except ValueError as e:
        raise ValueError(f"Invalid tmux fragment argument '{argument}': {e}") from e

    fragments = []
    for arg in args:
        cmd = ["tmux", "capture-pane", "-p"]

        if arg.pane:
            cmd += ["-t", f"{arg.pane}"]

        content = subprocess.check_output(
            cmd, text=True, stderr=subprocess.PIPE
        ).rstrip()

        if arg.lines:
            content = "\n".join(content.splitlines()[-arg.lines :])

        # wrap the content in a tag
        content = f"<tmux pane={arg.pane or 'current_pane'} lines={arg.lines or 'all'}>\n{content}\n</tmux>"

        fragments.append(
            llm.Fragment(content, source=f"tmux:{arg.pane or ''}:{arg.lines or ''}")
        )

    return fragments
