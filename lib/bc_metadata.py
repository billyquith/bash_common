"""Command metadata discovery for bash_common tools."""

import json
import os
import platform
import subprocess
from pathlib import Path


def system_dir():
    name = platform.system()
    if name == "Darwin":
        return "darwin"
    if name.startswith("CYGWIN"):
        return "cygwin"
    return "unix"


def command_env(bc_dir):
    bc_dir = Path(bc_dir)
    env = os.environ.copy()
    env["BC_INSTALL_DIR"] = str(bc_dir)
    env["PATH"] = os.pathsep.join([
        str(bc_dir),
        str(bc_dir / system_dir()),
        env.get("PATH", ""),
    ])
    return env


def candidate_paths(bc_dir):
    bc_dir = Path(bc_dir)
    roots = [bc_dir, bc_dir / system_dir()]
    seen = set()
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.iterdir()):
            if path.name.startswith(".") or path.name.startswith("_"):
                continue
            if not path.is_file() or not os.access(path, os.X_OK):
                continue
            real = path.resolve()
            if real in seen:
                continue
            seen.add(real)
            yield path


def has_metadata_marker(path):
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return "--bc-metadata" in text or "def bc_metadata" in text


def inspect_commands(bc_dir, timeout=3):
    commands = []
    diagnostics = []
    bc_dir = Path(bc_dir)
    env = command_env(bc_dir)
    for path in candidate_paths(bc_dir):
        if not has_metadata_marker(path):
            continue
        try:
            proc = subprocess.run(
                [str(path), "--bc-metadata"],
                cwd=str(bc_dir),
                env=env,
                text=True,
                capture_output=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            diagnostics.append({
                "path": str(path),
                "status": "timeout",
                "message": f"metadata command exceeded {timeout}s",
            })
            continue
        except Exception as exc:
            diagnostics.append({
                "path": str(path),
                "status": "error",
                "message": str(exc),
            })
            continue
        if proc.returncode != 0:
            diagnostics.append({
                "path": str(path),
                "status": "failed",
                "returncode": proc.returncode,
                "stderr": proc.stderr.strip(),
            })
            continue
        try:
            metadata = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            diagnostics.append({
                "path": str(path),
                "status": "invalid-json",
                "message": str(exc),
            })
            continue
        if not isinstance(metadata, dict) or not metadata.get("name"):
            diagnostics.append({
                "path": str(path),
                "status": "invalid-schema",
                "message": "metadata must be an object with a non-empty name",
            })
            continue
        metadata["_path"] = str(path)
        commands.append(metadata)
    commands.sort(key=lambda item: item["name"])
    return {"commands": commands, "diagnostics": diagnostics}


def discover_commands(bc_dir, timeout=3):
    return inspect_commands(bc_dir, timeout=timeout)["commands"]


def public_commands(commands):
    public = []
    for command in commands:
        item = dict(command)
        item.pop("_path", None)
        public.append(item)
    return public


def config_defaults(commands):
    defaults = {}
    for command in commands:
        for section, keys in command.get("config_sections", {}).items():
            for entry in keys:
                defaults[f"{section}.{entry['key']}"] = entry.get("default", "")
    return defaults


def config_sections(commands):
    sections = {}
    for command in commands:
        for section, keys in command.get("config_sections", {}).items():
            sections[section] = [
                (entry["key"], entry.get("default", ""), entry.get("description", ""))
                for entry in keys
            ]
    return sections
