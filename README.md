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

## Usage

This plugin provides two main commands:

### 1. Capture tmux pane content

Print the content of a tmux pane (for testing or use in LLM):

```bash
llm fragments_tmux --pane-id <pane_id> --lines <num_lines>
```
- `--pane-id` (optional): Specify the tmux pane id (default: current pane)
- `--lines` (optional): Number of lines from the bottom of the pane to capture (default: all)

Example:
```bash
llm fragments_tmux --pane-id %1 --lines 20
```

### 2. List available tmux panes

List all tmux panes with their IDs and titles for selection:

```bash
llm list_tmux_panes
```

This will print a list of all panes, e.g.:
```
session:0.0 %1 zsh
session:0.1 %2 vim
```

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
