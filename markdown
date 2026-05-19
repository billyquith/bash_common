#!/usr/bin/env python3
# markdown - render Markdown to HTML via markdown2
#
# Thin wrapper around the markdown2 command-line interface.
# All arguments are passed directly to markdown2.
#
# Usage: markdown [OPTIONS] [FILE...]
#   -h / --help   show markdown2 help
#
# Requires: pip install markdown2  (or run bcinit)

import sys
import markdown2

markdown2.main(sys.argv)
