import llm
import subprocess
from typing import List


def parse_tmux_fragment_argument(
    argument_string: str,
) -> list[dict[str, str | int | None]]:
    if not argument_string.strip():
        return [{"pane": None, "lines": None}]

    params = []

    # Split the argument string by commas
    argument_parts = argument_string.split(",")
    for part in argument_parts:
        # Split each part by colon
        pane_part, sep, line_value = part.partition(":")
        line_part = line_value if sep else None

        params.append(
            {
                "pane": pane_part if pane_part else None,
                "lines": int(line_part) if line_part else None,
            }
        )

    return params


@llm.hookimpl
def register_fragment_loaders(register):
    """Register the tmux fragment loader"""
    register("tmux", tmux_loader_function)


def tmux_loader_function(argument: str) -> List[llm.Fragment]:
    try:
        params = parse_tmux_fragment_argument(argument)
    except ValueError as e:
        raise ValueError(f"Invalid tmux fragment argument '{argument}': {e}") from e

    fragments = []
    for param in params:
        pane_id = param["pane"]
        lines = param["lines"]
        cmd = ["tmux", "capture-pane", "-p"]

        if pane_id:
            cmd += ["-t", f"{pane_id}"]

        content = subprocess.check_output(
            cmd, text=True, stderr=subprocess.PIPE
        ).rstrip()

        if lines:
            content = "\n".join(content.splitlines()[-lines:])

        fragments.append(llm.Fragment(content, source=f"tmux:{pane_id=}:{lines=}"))

    return fragments
