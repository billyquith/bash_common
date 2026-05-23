import os
import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def clean_env(home):
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("BASH_FUNC_")
    }
    env["HOME"] = str(home)
    env["BC_INSTALL_DIR"] = str(ROOT)
    env["LC_ALL"] = "C"
    return env


class ShellStartupTests(unittest.TestCase):
    def run_bash(self, script, home):
        return subprocess.run(
            ["bash", "--noprofile", "--norc", "-c", script],
            cwd=ROOT,
            env=clean_env(home),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_noninteractive_bashrc_is_quiet(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self.run_bash('source "$BC_INSTALL_DIR/.bashrc"; echo ok', tmp)

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual("ok\n", proc.stdout)
        self.assertEqual("", proc.stderr)

    def test_bookmarks_do_not_create_file_when_sourced(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self.run_bash(
                'source "$BC_INSTALL_DIR/commands/helpers.sh"; '
                'source "$BC_INSTALL_DIR/commands/bookmark.sh"; '
                '[ ! -e "$HOME/.sdirs" ]',
                tmp,
            )

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual("", proc.stdout)
        self.assertEqual("", proc.stderr)


if __name__ == "__main__":
    unittest.main()
