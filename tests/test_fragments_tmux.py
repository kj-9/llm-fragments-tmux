import os
import pytest
import llm_fragments_tmux

class DummyArgs:
    def __init__(self, pane_id=None, lines=None):
        self.pane_id = pane_id
        self.lines = lines

def test_is_tmux_running_false(monkeypatch):
    monkeypatch.delenv("TMUX", raising=False)
    assert not llm_fragments_tmux.TmuxFragment._is_tmux_running()

def test_is_tmux_running_true(monkeypatch):
    monkeypatch.setenv("TMUX", "/tmp/tmux-1000/default,1234,0")
    assert llm_fragments_tmux.TmuxFragment._is_tmux_running()

def test_get_current_pane_id_static_success(monkeypatch):
    monkeypatch.setenv("TMUX_PANE", "%1")
    assert llm_fragments_tmux.TmuxFragment._get_current_pane_id_static() == "%1"

def test_get_current_pane_id_static_error(monkeypatch):
    monkeypatch.delenv("TMUX_PANE", raising=False)
    with pytest.raises(RuntimeError):
        llm_fragments_tmux.TmuxFragment._get_current_pane_id_static()

def test_capture_pane_static_invalid(monkeypatch):
    # Simulate tmux not installed or invalid pane
    def fake_check_output(*a, **k):
        raise Exception("tmux not found")
    monkeypatch.setattr(llm_fragments_tmux.subprocess, "check_output", fake_check_output)
    result = llm_fragments_tmux.TmuxFragment._capture_pane_static("%9999")
    assert "tmux error" in result

def test_from_args_not_in_tmux(monkeypatch):
    monkeypatch.delenv("TMUX", raising=False)
    args = DummyArgs()
    frag = llm_fragments_tmux.TmuxFragment.from_args(args)
    assert "tmux error" in frag.text

def test_from_args_capture(monkeypatch):
    monkeypatch.setenv("TMUX", "dummy")
    monkeypatch.setenv("TMUX_PANE", "%1")
    def fake_capture_pane_static(pane_id, lines=None):
        return f"pane_id={pane_id}, lines={lines}"
    monkeypatch.setattr(llm_fragments_tmux.TmuxFragment, "_capture_pane_static", staticmethod(fake_capture_pane_static))
    args = DummyArgs(pane_id="%1", lines=10)
    frag = llm_fragments_tmux.TmuxFragment.from_args(args)
    assert frag.text == "pane_id=%1, lines=10"
