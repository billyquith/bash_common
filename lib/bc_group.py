"""Helpers for metadata-backed grouped command wrappers."""

import json
import os
import subprocess
import sys

from lib.bc_metadata import command_env


def passthrough_arg(name="args", label="Arguments"):
    return {
        "name": name,
        "label": label,
        "kind": "path-list",
        "required": False,
    }


def metadata(name, summary, subcommands):
    normalized = []
    for subcommand in subcommands:
        item = dict(subcommand)
        item.setdefault("passthrough", True)
        normalized.append(item)
    return {
        "schema_version": 1,
        "name": name,
        "summary": summary,
        "command_style": "subcommands",
        "config_sections": {},
        "subcommands": normalized,
    }


def run_group(group_name, summary, routes, argv=None, bc_dir=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    bc_dir = bc_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if argv == ["--bc-metadata"]:
        print(json.dumps(metadata(group_name, summary, [r["metadata"] for r in routes.values()]),
                         indent=2, sort_keys=True))
        return 0

    if not argv or argv[0] in ("-h", "--help"):
        _print_help(group_name, summary, routes)
        return 0 if argv else 1

    subcommand = argv[0]
    route = routes.get(subcommand)
    if not route:
        print(f"Error: unknown subcommand: {subcommand}", file=sys.stderr)
        print("", file=sys.stderr)
        _print_help(group_name, summary, routes, file=sys.stderr)
        return 1

    handler = route.get("handler")
    if handler is not None:
        return handler(argv[1:]) or 0

    target = os.path.join(bc_dir, route["target"])
    target_argv = [*_target_command(target), *route.get("prefix", []), *argv[1:]]
    proc = subprocess.run(target_argv, cwd=os.getcwd(), env=command_env(bc_dir))
    return proc.returncode


def _target_command(path):
    if os.access(path, os.X_OK):
        return [path]

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            first_line = fh.readline()
    except OSError:
        return [path]

    if "python" in first_line:
        return [sys.executable, path]
    if "bash" in first_line or "sh" in first_line:
        return ["bash", path]
    return [path]


def _print_help(group_name, summary, routes, file=None):
    file = file or sys.stdout
    print(f"{group_name} - {summary}", file=file)
    print("", file=file)
    print(f"Usage: {group_name} SUBCOMMAND [ARGS...]", file=file)
    print("", file=file)
    print("Subcommands:", file=file)
    for name, route in routes.items():
        print(f"  {name:<14} {route['metadata'].get('summary', '')}", file=file)
