#!/usr/bin/env python3

import os
import time
import subprocess
import uuid
import nvim_remote

# Helper functions


def run_nvim(env):
    nvim = subprocess.Popen(["nvim", "-nu", "NORC", "--headless"], env=env)
    time.sleep(1)
    return nvim


def run_nvim_remote(cmdlines, env):
    for cmdline in cmdlines:
        nvim_remote.main(cmdline, env)


def setup_env():
    env = {"NVIM_LISTEN_ADDRESS": "./pytest_socket_{}".format(uuid.uuid4())}
    env.update(os.environ)
    return env


# Tests


def test_remote_send(capsys):
    env = setup_env()
    nvim = run_nvim(env)
    cmdlines = [
        ["nvr", "--nostart", "--remote-send", "iabc<cr><esc>"],
        ["nvr", "--nostart", "--remote-expr", "getline(1)"],
    ]
    run_nvim_remote(cmdlines, env)
    nvim.terminate()
    out, err = capsys.readouterr()
    assert out == "abc\n"


# https://github.com/mhinz/neovim-remote/issues/77
def test_escape_filenames_properly(capsys):
    filename = "a b|c"
    env = setup_env()
    nvim = run_nvim(env)
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
    run_nvim_remote(cmdlines, env)
    nvim.terminate()
    out, err = capsys.readouterr()
    assert filename == out.rstrip()


def test_escape_single_quotes_in_filenames(capsys):
    filename = "foo'bar'quux"
    env = setup_env()
    nvim = run_nvim(env)
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
    run_nvim_remote(cmdlines, env)
    nvim.terminate()
    out, err = capsys.readouterr()
    assert filename == out.rstrip()


def test_escape_double_quotes_in_filenames(capsys):
    filename = 'foo"bar"quux'
    env = setup_env()
    nvim = run_nvim(env)
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
    run_nvim_remote(cmdlines, env)
    nvim.terminate()
    out, err = capsys.readouterr()
    assert filename == out.rstrip()
