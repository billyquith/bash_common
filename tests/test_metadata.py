import pathlib
import unittest

from lib import bc_metadata


ROOT = pathlib.Path(__file__).resolve().parents[1]


class MetadataTests(unittest.TestCase):
    def test_discovers_metadata_backed_commands(self):
        report = bc_metadata.inspect_commands(ROOT)
        names = {command["name"] for command in report["commands"]}

        self.assertIn("video", names)
        self.assertIn("bashcommon", names)
        self.assertIn("android", names)
        self.assertEqual([], report["diagnostics"])

    def test_android_metadata_shape(self):
        report = bc_metadata.inspect_commands(ROOT)
        android = next((c for c in report["commands"] if c["name"] == "android"), None)
        self.assertIsNotNone(android, "android command should be discoverable")
        self.assertEqual("subcommands", android.get("command_style"))

        subcommand_names = {s["name"] for s in android.get("subcommands", [])}
        for expected in {"install", "uninstall", "run", "log", "list", "dump",
                         "activity", "devices", "adb", "config"}:
            self.assertIn(expected, subcommand_names, f"missing subcommand: {expected}")

        sections = android.get("config_sections", {})
        self.assertIn("android", sections)
        keys = {entry["key"] for entry in sections["android"]}
        for expected_key in {"adb", "unity_path", "apk", "package", "activity",
                             "log_file", "logopts"}:
            self.assertIn(expected_key, keys, f"missing config key: {expected_key}")


if __name__ == "__main__":
    unittest.main()
