#!/usr/bin/env python3

import os
import subprocess
import time
import uuid

import pytest

import nvim_remote

# Helper functions


def run_nvim(env: dict[str, str]) -> subprocess.Popen[bytes]:
    nvim = subprocess.Popen(["nvim", "-nu", "NORC", "--headless"], env=env)
    time.sleep(1)
    return nvim


def run_nvim_remote(cmdlines: list[list[str]], env: dict[str, str]) -> None:
    for cmdline in cmdlines:
        nvim_remote.main(cmdline, env)


@pytest.fixture
def nvim_env() -> dict[str, str]:
    """Create environment with socket address and clean up socket file after test."""
    socket_path = f"./pytest_socket_{uuid.uuid4()}"
    env = {"NVIM_LISTEN_ADDRESS": socket_path}
    env.update(os.environ)
    yield env
    # Clean up socket file if it exists
    if os.path.exists(socket_path):
        os.remove(socket_path)


# Tests


def test_remote_send(
    nvim_env: dict[str, str], capsys: pytest.CaptureFixture[str]
) -> None:
    nvim = run_nvim(nvim_env)
    cmdlines = [
        ["nvr", "--nostart", "--remote-send", "iabc<cr><esc>"],
        ["nvr", "--nostart", "--remote-expr", "getline(1)"],
    ]
    run_nvim_remote(cmdlines, nvim_env)
    nvim.terminate()
    out, _err = capsys.readouterr()
    assert out == "abc\n"


# https://github.com/mhinz/neovim-remote/issues/77
def test_escape_filenames_properly(
    nvim_env: dict[str, str], capsys: pytest.CaptureFixture[str]
) -> None:
    filename = "a b|c"
    nvim = run_nvim(nvim_env)
    cmdlines = [
        ["nvr", "-s", "--nostart", "-o", filename],
        [
            "nvr",
            "-s",
            "--nostart",
            "--remote-expr",
            'fnamemodify(bufname(""), ":t")',
        ],
    ]
    run_nvim_remote(cmdlines, nvim_env)
    nvim.terminate()
    out, _err = capsys.readouterr()
    assert filename == out.rstrip()


def test_escape_single_quotes_in_filenames(
    nvim_env: dict[str, str], capsys: pytest.CaptureFixture[str]
) -> None:
    filename = "foo'bar'quux"
    nvim = run_nvim(nvim_env)
    cmdlines = [
        ["nvr", "-s", "--nostart", "-o", filename],
        [
            "nvr",
            "-s",
            "--nostart",
            "--remote-expr",
            'fnamemodify(bufname(""), ":t")',
        ],
    ]
    run_nvim_remote(cmdlines, nvim_env)
    nvim.terminate()
    out, _err = capsys.readouterr()
    assert filename == out.rstrip()


def test_escape_double_quotes_in_filenames(
    nvim_env: dict[str, str], capsys: pytest.CaptureFixture[str]
) -> None:
    filename = 'foo"bar"quux'
    nvim = run_nvim(nvim_env)
    cmdlines = [
        ["nvr", "-s", "--nostart", "-o", filename],
        [
            "nvr",
            "-s",
            "--nostart",
            "--remote-expr",
            'fnamemodify(bufname(""), ":t")',
        ],
    ]
    run_nvim_remote(cmdlines, nvim_env)
    nvim.terminate()
    out, _err = capsys.readouterr()
    assert filename == out.rstrip()
