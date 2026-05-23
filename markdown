#!/usr/bin/env python3
# markdown - render Markdown to HTML via markdown2
#
# Thin wrapper around the markdown2 command-line interface.
# All arguments are passed directly to markdown2.
#
# Usage: markdown [OPTIONS] [FILE...]
#   -h / --help   show markdown2 help
#
# Requires: markdown2 in bash_common's local .venv (run bcinit)

import os
import sys


script_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(script_dir, ".venv", "bin", "python")
if os.path.exists(venv_python) and os.path.abspath(sys.executable) != os.path.abspath(venv_python):
    os.execv(venv_python, [venv_python, __file__, *sys.argv[1:]])

try:
    import markdown2
except ModuleNotFoundError:
    print("Error: markdown2 is not installed. Run 'bcinit' to install dependencies.", file=sys.stderr)
    sys.exit(1)

markdown2.main(sys.argv)
