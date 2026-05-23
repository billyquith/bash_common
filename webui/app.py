"""Flask app for BC UI."""

import mimetypes
import os
import shlex
import subprocess
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

from lib.bc_metadata import command_env, config_defaults, discover_commands, public_commands
from lib.bc_output import strip_ansi


JOBS = []
JOBS_LOCK = threading.Lock()
MAX_JOBS = 50


def _command_map(commands):
    return {cmd["name"]: cmd for cmd in commands}


def _subcommand_map(command):
    return {sub["name"]: sub for sub in command.get("subcommands", [])}


def _option_flags(subcommand):
    flags = {}
    for opt in subcommand.get("options", []):
        for key in ("flag", "short_flag"):
            flag = opt.get(key)
            if flag:
                flags[flag] = opt
    return flags


def _run_bcconfig(bc_dir, cwd, *args):
    proc = subprocess.run(
        [str(bc_dir / "bcconfig"), *args],
        cwd=cwd,
        env=command_env(bc_dir),
        text=True,
        capture_output=True,
        timeout=10,
    )
    return {
        "argv": ["bcconfig", *args],
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _config_values(bc_dir, cwd, commands):
    values = {}
    for key, default in config_defaults(commands).items():
        proc = _run_bcconfig(bc_dir, cwd, "--get", key, "--fallback", str(default))
        if proc["returncode"] == 0:
            values[key] = proc["stdout"].strip()
        else:
            values[key] = str(default)
    return values


def _config_state(bc_dir, cwd, commands):
    return {
        "files": _run_bcconfig(bc_dir, cwd, "--files"),
        "effective": _run_bcconfig(bc_dir, cwd),
        "values": _config_values(bc_dir, cwd, commands),
    }


def _normalize_cwd(default_cwd):
    cwd = request.args.get("cwd") or (request.get_json(silent=True) or {}).get("cwd")
    cwd = cwd or default_cwd
    cwd = os.path.abspath(os.path.expanduser(cwd))
    if not os.path.isdir(cwd):
        raise ValueError(f"Working directory does not exist: {cwd}")
    return cwd


def _split_list(value):
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [part.strip() for part in str(value).replace("\n", ",").split(",") if part.strip()]


def _build_structured_argv(commands, data):
    command = _command_map(commands).get(data.get("command"))
    if not command:
        raise ValueError("Unknown command.")
    subcommand = _subcommand_map(command).get(data.get("subcommand"))
    if not subcommand:
        raise ValueError("Unknown subcommand.")

    argv = [subcommand["name"]]
    option_values = data.get("options") or {}
    arg_values = data.get("args") or {}

    for opt in subcommand.get("options", []):
        value = option_values.get(opt["name"])
        if opt.get("kind") == "boolean":
            if value:
                argv.append(opt["flag"])
            continue
        if value is None or str(value).strip() == "":
            continue
        argv.extend([opt["flag"], str(value)])

    for arg in subcommand.get("args", []):
        value = arg_values.get(arg["name"])
        if arg.get("required") and (value is None or str(value).strip() == ""):
            raise ValueError(f"Missing required argument: {arg['name']}")
        if value is None or str(value).strip() == "":
            continue
        if arg.get("kind") == "path-list":
            argv.extend(_split_list(value))
        else:
            argv.append(str(value))

    return command, subcommand, argv, option_values


def _validate_raw_argv(commands, command_line):
    parts = shlex.split(command_line)
    if not parts:
        raise ValueError("No command entered.")
    name = os.path.basename(parts[0])
    command = _command_map(commands).get(name)
    if not command:
        raise ValueError(f"Unsupported command: {name}")
    if command.get("command_style") != "subcommands":
        raise ValueError(f"Unsupported command style: {name}")
    if len(parts) < 2:
        raise ValueError(f"Missing subcommand for {name}.")
    subcommands = _subcommand_map(command)
    subcommand = subcommands.get(parts[1])
    if not subcommand:
        raise ValueError(f"Unsupported subcommand: {parts[1]}")
    if subcommand.get("passthrough"):
        return command, subcommand, parts[1:], {}

    flags = _option_flags(subcommand)
    option_values = {}
    i = 2
    while i < len(parts):
        token = parts[i]
        if not token.startswith("-"):
            i += 1
            continue
        opt = flags.get(token)
        if not opt:
            raise ValueError(f"Unsupported option for {name} {subcommand['name']}: {token}")
        if opt.get("kind") == "boolean":
            option_values[opt["name"]] = True
            i += 1
        else:
            if i + 1 >= len(parts):
                raise ValueError(f"Missing value for option: {token}")
            option_values[opt["name"]] = parts[i + 1]
            i += 2

    return command, subcommand, parts[1:], option_values


def _artifact_path(cwd, value):
    path = Path(os.path.expanduser(str(value)))
    if not path.is_absolute():
        path = Path(cwd) / path
    return path.resolve()


def _collect_artifacts(cwd, subcommand, option_values):
    artifacts = []
    for spec in subcommand.get("artifacts", []):
        opt_name = spec.get("path_option")
        if not opt_name:
            continue
        value = option_values.get(opt_name)
        if not value:
            continue
        path = _artifact_path(cwd, value)
        if not path.exists() or not path.is_file():
            continue
        mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        artifacts.append({
            "name": path.name,
            "path": str(path),
            "kind": spec.get("kind") or mime,
            "mime": mime,
            "size": path.stat().st_size,
        })
    return artifacts


def _store_job(job):
    with JOBS_LOCK:
        JOBS.insert(0, job)
        del JOBS[MAX_JOBS:]


def _public_job(job):
    public = {key: value for key, value in job.items() if not key.startswith("_")}
    public["artifacts"] = [
        {
            "name": artifact["name"],
            "kind": artifact["kind"],
            "mime": artifact["mime"],
            "size": artifact["size"],
            "url": f"/api/artifacts/{job['id']}/{idx}",
        }
        for idx, artifact in enumerate(job.get("artifacts", []))
    ]
    return public


def _find_job(job_id):
    with JOBS_LOCK:
        for job in JOBS:
            if job["id"] == job_id:
                return job
    return None


def _append_output(job, key, text):
    if not text:
        return
    with JOBS_LOCK:
        job[key] += strip_ansi(text)


def _set_job(job, **values):
    with JOBS_LOCK:
        job.update(values)


def _read_stream(job, pipe, key):
    try:
        for chunk in iter(pipe.readline, ""):
            _append_output(job, key, chunk)
    finally:
        pipe.close()


def _run_job(job, full_argv, cwd, env, subcommand, option_values, started):
    try:
        proc = subprocess.Popen(
            full_argv,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
        )
        _set_job(job, pid=proc.pid, _process=proc)

        stdout_thread = threading.Thread(
            target=_read_stream,
            args=(job, proc.stdout, "stdout"),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=_read_stream,
            args=(job, proc.stderr, "stderr"),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()

        returncode = proc.wait()
        stdout_thread.join()
        stderr_thread.join()

        with JOBS_LOCK:
            was_cancelling = job.get("status") == "cancelling"
        status = "cancelled" if was_cancelling else "finished"
        _set_job(
            job,
            status=status,
            returncode=returncode,
            elapsed=time.monotonic() - started,
            artifacts=_collect_artifacts(cwd, subcommand, option_values),
        )
    except Exception as exc:
        _append_output(job, "stderr", f"{exc}\n")
        _set_job(
            job,
            status="error",
            returncode=-1,
            elapsed=time.monotonic() - started,
        )
    finally:
        _set_job(job, _process=None)


def create_app(bc_dir, default_cwd):
    bc_dir = Path(bc_dir).resolve()
    default_cwd = os.path.abspath(default_cwd)
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/state")
    def state():
        try:
            cwd = _normalize_cwd(default_cwd)
            commands = discover_commands(bc_dir)
            with JOBS_LOCK:
                jobs = [_public_job(job) for job in JOBS]
            return jsonify({
                "bc_dir": str(bc_dir),
                "cwd": cwd,
                "commands": public_commands(commands),
                "config": _config_state(bc_dir, cwd, commands),
                "jobs": jobs,
            })
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/run")
    def run_command():
        started = time.monotonic()
        data = request.get_json(force=True)
        try:
            cwd = _normalize_cwd(default_cwd)
            commands = discover_commands(bc_dir)
            if data.get("mode") == "raw":
                command, subcommand, argv, option_values = _validate_raw_argv(
                    commands, data.get("command_line", "")
                )
            else:
                command, subcommand, argv, option_values = _build_structured_argv(commands, data)

            full_argv = [command["_path"], *argv]
            job = {
                "id": uuid.uuid4().hex[:12],
                "status": "running",
                "command": command["name"],
                "subcommand": subcommand["name"],
                "argv": [command["name"], *argv],
                "cwd": cwd,
                "pid": None,
                "returncode": None,
                "stdout": "",
                "stderr": "",
                "elapsed": 0,
                "artifacts": [],
                "_process": None,
            }
            _store_job(job)
            thread = threading.Thread(
                target=_run_job,
                args=(job, full_argv, cwd, command_env(bc_dir), subcommand, option_values, started),
                daemon=True,
            )
            thread.start()
            return jsonify({"job": _public_job(job)})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @app.get("/api/jobs/<job_id>")
    def job_status(job_id):
        job = _find_job(job_id)
        if not job:
            return jsonify({"error": "Job not found."}), 404
        with JOBS_LOCK:
            return jsonify({"job": _public_job(job)})

    @app.post("/api/jobs/<job_id>/cancel")
    def cancel_job(job_id):
        job = _find_job(job_id)
        if not job:
            return jsonify({"error": "Job not found."}), 404
        with JOBS_LOCK:
            proc = job.get("_process")
            if job.get("status") != "running" or proc is None:
                return jsonify({"job": _public_job(job)})
            job["status"] = "cancelling"
        proc.terminate()
        with JOBS_LOCK:
            return jsonify({"job": _public_job(job)})

    @app.get("/api/artifacts/<job_id>/<int:index>")
    def artifact(job_id, index):
        job = _find_job(job_id)
        if job:
            with JOBS_LOCK:
                artifacts = list(job.get("artifacts", []))
            if 0 <= index < len(artifacts):
                artifact = artifacts[index]
                return send_file(artifact["path"], mimetype=artifact["mime"])
        return jsonify({"error": "Artifact not found."}), 404

    return app
