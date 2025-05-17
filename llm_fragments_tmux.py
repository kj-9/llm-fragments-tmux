import click
import llm
import subprocess

class TmuxFragment(llm.Fragment):
    name = "tmux"
    type = "tmux"
    description = "Content of a tmux pane (current or specified by pane id)"

    @classmethod
    def from_args(cls, args):
        pane_id = getattr(args, "pane_id", None)
        lines = getattr(args, "lines", None)
        if not cls._is_tmux_running():
            return cls("[tmux error: Not running inside a tmux session]")
        try:
            content = cls._capture_pane_static(pane_id or cls._get_current_pane_id_static(), lines=lines)
        except Exception as e:
            content = f"[tmux error: {e}]"
        return cls(content)

    @staticmethod
    def _is_tmux_running():
        """Check if tmux is running and the current process is inside a tmux session."""
        import os
        return os.environ.get("TMUX") is not None

    @staticmethod
    def _get_current_pane_id_static():
        import os
        pane_id = os.environ.get("TMUX_PANE")
        if not pane_id:
            raise RuntimeError("TMUX_PANE environment variable not set. Are you running inside tmux?")
        return pane_id

    @staticmethod
    def _capture_pane_static(pane_id, lines=None):
        args = ["tmux", "capture-pane", "-p"]
        if lines is not None:
            args += ["-S", f"-{lines}"]
        if pane_id:
            args += ["-t", pane_id]
        try:
            return subprocess.check_output(args, text=True)
        except subprocess.CalledProcessError as e:
            return f"[tmux error: {e}\nOutput: {e.output}]"
        except Exception as e:
            return f"[tmux error: {e}]"

    def __init__(self, content):
        super().__init__(content=content)
        self._content = content

    @property
    def text(self):
        return self._content

@llm.hookimpl
def register_fragments(register):
    register(
        TmuxFragment,
        name="tmux",
        description="Content of a tmux pane (current or specified by pane id)",
        add_arguments=lambda parser: parser.add_argument("--pane-id", help="tmux pane id (default: current pane)")
    )

@llm.hookimpl
def create_fragment_from_args(args):
    return TmuxFragment.from_args(args)

@llm.hookimpl
def register_commands(cli):
    @cli.command()
    @click.option("--pane-id", help="tmux pane id (default: current pane)")
    @click.option("--lines", type=int, help="Number of lines from the bottom of the pane to capture (default: all)")
    def fragments_tmux(pane_id, lines):
        """Print the content of a tmux pane (for testing). Use --pane-id to specify a pane, --lines to limit output."""
        class Args:
            pass
        args = Args()
        args.pane_id = pane_id
        args.lines = lines
        frag = TmuxFragment.from_args(args)
        click.echo(frag.text)

    @cli.command()
    def list_tmux_panes():
        """List all tmux panes with their IDs and titles for selection."""
        try:
            output = subprocess.check_output([
                "tmux", "list-panes", "-a", "-F", "#{session_name}:#{window_index}.#{pane_index} #{pane_id} #{pane_title}"
            ], text=True)
            click.echo("Available tmux panes:")
            click.echo(output)
        except Exception as e:
            click.echo(f"[tmux error: {e}]")
