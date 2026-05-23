"""Shared .bcconfig discovery and loading helpers."""

import configparser
import os


CONFIG_NAME = ".bcconfig"


def find_files(cwd=None):
    """Return .bcconfig files in load order, lowest priority first."""
    home = os.path.expanduser("~")
    cwd = os.path.abspath(cwd or os.getcwd())

    paths = []
    home_cfg = os.path.join(home, CONFIG_NAME)
    if os.path.isfile(home_cfg):
        paths.append(home_cfg)

    try:
        rel = os.path.relpath(cwd, home)
    except ValueError:
        rel = ".."

    if rel.startswith(".."):
        outside = []
        current = cwd
        while True:
            candidate = os.path.join(current, CONFIG_NAME)
            if os.path.isfile(candidate):
                outside.append(candidate)
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
        outside.reverse()
        paths.extend(outside)
        return paths

    parts = [p for p in rel.split(os.sep) if p and p != "."]
    current = home
    for part in parts:
        current = os.path.join(current, part)
        candidate = os.path.join(current, CONFIG_NAME)
        if os.path.isfile(candidate):
            paths.append(candidate)

    return paths


def load(cwd=None):
    """Load and merge .bcconfig files for cwd."""
    cfg = configparser.RawConfigParser()
    cfg.read(find_files(cwd), encoding="utf-8")
    return cfg


def load_with_provenance(files):
    """Load .bcconfig files and track the source file for every key."""
    prov = {}
    overridden = set()
    merged = configparser.RawConfigParser()

    for filepath in files:
        single = configparser.RawConfigParser()
        single.read(filepath, encoding="utf-8")
        for section in single.sections():
            if not merged.has_section(section):
                merged.add_section(section)
            for key, value in single.items(section):
                if (section, key) in prov:
                    overridden.add((section, key))
                merged.set(section, key, value)
                prov[(section, key)] = filepath

    return merged, prov, overridden


def abbrev(path):
    """Replace the current user's home directory prefix with ~."""
    home = os.path.expanduser("~")
    if path == home or path.startswith(home + os.sep):
        return "~" + path[len(home):]
    return path
