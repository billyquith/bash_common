import pathlib
import unittest

from lib import bc_metadata


ROOT = pathlib.Path(__file__).resolve().parents[1]


class MetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        report = bc_metadata.inspect_commands(ROOT)
        cls.commands = {cmd["name"]: cmd for cmd in report["commands"]}
        cls.diagnostics = report["diagnostics"]

    def test_discovers_all_groups(self):
        expected = {"android", "bashcommon", "blender", "docs", "files",
                    "project", "safari", "video"}
        self.assertEqual(expected, set(self.commands.keys()))

    def test_no_diagnostics(self):
        self.assertEqual([], self.diagnostics)

    def _subcommand_names(self, group):
        return {s["name"] for s in self.commands[group].get("subcommands", [])}

    def _config_keys(self, group):
        sections = self.commands[group].get("config_sections", {})
        return {entry["key"] for entries in sections.values() for entry in entries}

    # --- android ---

    def test_android_subcommands(self):
        expected = {"install", "uninstall", "run", "log", "list", "dump",
                    "activity", "devices", "adb", "config"}
        self.assertEqual(expected, self._subcommand_names("android"))

    def test_android_config_keys(self):
        expected = {"adb", "unity_path", "apk", "package", "activity",
                    "log_file", "logopts"}
        self.assertEqual(expected, self._config_keys("android"))

    # --- bashcommon ---

    def test_bashcommon_subcommands(self):
        expected = {"init", "update", "config", "ui", "doctor", "list"}
        self.assertEqual(expected, self._subcommand_names("bashcommon"))

    # --- blender ---

    def test_blender_subcommands(self):
        self.assertEqual({"launch", "python", "config"}, self._subcommand_names("blender"))

    def test_blender_config_keys(self):
        expected = {"blender_path", "config_path", "gameplay_bin"}
        self.assertEqual(expected, self._config_keys("blender"))

    # --- docs ---

    def test_docs_subcommands(self):
        self.assertEqual({"cheat", "markdown"}, self._subcommand_names("docs"))

    def test_docs_config_keys(self):
        self.assertIn("cheat_dir", self._config_keys("docs"))

    # --- files ---

    def test_files_subcommands(self):
        self.assertEqual({"rename", "format-cpp"}, self._subcommand_names("files"))

    def test_files_config_keys(self):
        self.assertIn("uncrustify_config", self._config_keys("files"))

    # --- project ---

    def test_project_subcommands(self):
        expected = {"git-init", "unity-init", "shell-script", "cmake", "cmake-dir"}
        self.assertEqual(expected, self._subcommand_names("project"))

    # --- safari ---

    def test_safari_subcommands(self):
        self.assertEqual({"cookies"}, self._subcommand_names("safari"))

    def test_safari_config_keys(self):
        self.assertIn("cookies_file", self._config_keys("safari"))

    # --- video ---

    def test_video_subcommands(self):
        expected = {"formats", "info", "convert", "concat", "clamp",
                    "thumb", "normalise", "catalog"}
        self.assertEqual(expected, self._subcommand_names("video"))

    def test_video_config_sections(self):
        sections = self.commands["video"].get("config_sections", {})
        self.assertIn("video", sections)
        self.assertIn("video.convert", sections)
        self.assertIn("video.normalise", sections)

    # --- metadata shape ---

    def test_all_commands_have_subcommand_style(self):
        for name, cmd in self.commands.items():
            with self.subTest(command=name):
                self.assertEqual("subcommands", cmd.get("command_style"),
                                 f"{name} should declare command_style=subcommands")

    def test_all_subcommands_declare_safety(self):
        for name, cmd in self.commands.items():
            for sub in cmd.get("subcommands", []):
                with self.subTest(command=name, subcommand=sub["name"]):
                    self.assertIn("safety", sub,
                                  f"{name} {sub['name']} should declare safety")


if __name__ == "__main__":
    unittest.main()
