# llm-fragments-tmux

[![PyPI](https://img.shields.io/pypi/v/llm-fragments-tmux.svg)](https://pypi.org/project/llm-fragments-tmux/)
[![Changelog](https://img.shields.io/github/v/release/kj-9/llm-fragments-tmux?include_prereleases&label=changelog)](https://github.com/kj-9/llm-fragments-tmux/releases)
[![Tests](https://github.com/kj-9/llm-fragments-tmux/actions/workflows/test.yml/badge.svg)](https://github.com/kj-9/llm-fragments-tmux/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/kj-9/llm-fragments-tmux/blob/main/LICENSE)

A plugin for [LLM](https://llm.datasette.io/) that provides fragments from tmux panes. It allows you to capture the content of a tmux pane and use it as a fragment in LLM prompts, or list available tmux panes for selection.

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).
```bash
llm install llm-fragments-tmux
```

## Example

Here's a step-by-step example of how you might use this plugin in practice:

1. Open tmux
```bash
tmux
```
2. Run a command in your tmux pane
```bash
echo "Hello, world! This is a test."
```
3. Use LLM with the tmux fragment to explain what happened
```bash
llm -f tmux: "Explain what happened in this terminal session."
```
This will capture the output from your current tmux pane and send it to LLM for explanation.


## Usage

This plugin provides a tmux fragment for use with LLM's `-f`/`--fragment` option.

You can use the content of one or more tmux panes directly in your LLM prompts using positional arguments:

```bash
llm -f tmux:1,2:20 "Summarize the following terminal output:"
```
- The first field (before the colon) is a comma-separated list of tmux pane ids (e.g., `1,2`). Omit for the current pane.
- The second field (after the colon) is the number of lines from the bottom of the pane(s) to capture (e.g., `20`). Omit for all lines.
- Examples:
  - `tmux:1,2:20` — panes 1 and 2, last 20 lines
  - `tmux:1` — pane 1, all lines
  - `tmux::20` — current pane, last 20 lines
  - `tmux:` — current pane, all lines (default)

You can also use the fragment in other LLM commands that support `-f`/`--fragment`.


## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd llm-fragments-tmux
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
python -m pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
