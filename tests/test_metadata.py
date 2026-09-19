import pathlib
import importlib.machinery
import importlib.util
import tempfile
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
        expected = {"formats", "info", "convert", "concat", "crop",
                    "thumb", "normalise", "catalog"}
        self.assertEqual(expected, self._subcommand_names("video"))

    def test_video_config_sections(self):
        sections = self.commands["video"].get("config_sections", {})
        self.assertIn("video", sections)
        self.assertIn("video.convert", sections)
        self.assertIn("video.normalise", sections)

    def test_video_loads_config_from_external_volume_path(self):
        """video must honour the same external-directory overrides as bcconfig."""
        loader = importlib.machinery.SourceFileLoader("video_for_test", str(ROOT / "video"))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        video = importlib.util.module_from_spec(spec)
        loader.exec_module(video)

        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            path = pathlib.Path(tmp)
            (path / ".bcconfig").write_text(
                "[video.normalise]\ntarget_height = 1080\n", encoding="utf-8"
            )
            cfg = video._load_config(tmp)
            self.assertEqual("1080", cfg.get("video.normalise", "target_height"))

    def test_video_normalise_uses_limits_unless_forced(self):
        loader = importlib.machinery.SourceFileLoader("video_limits_test", str(ROOT / "video"))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        video = importlib.util.module_from_spec(spec)
        loader.exec_module(video)
        source = {
            "interlaced": False, "height": 480, "width": 640, "fps": "24",
            "video_codec": "h264", "audio_codec": "aac",
            "format": "mp4", "format_names": "mov,mp4",
        }

        limited = video._norm_assess(
            source, "auto", 1080, 30, "h264", "aac", "mp4"
        )
        self.assertTrue(limited["compliant"])

        forced = video._norm_assess(
            source, "auto", 1080, 30, "h264", "aac", "mp4", True
        )
        self.assertFalse(forced["compliant"])
        self.assertIn("scale 640×480→h=1080", forced["reasons"])
        self.assertIn("fps 24→30", forced["reasons"])

    def test_video_normalise_copies_audio_under_bitrate_ceiling(self):
        loader = importlib.machinery.SourceFileLoader("video_audio_test", str(ROOT / "video"))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        video = importlib.util.module_from_spec(spec)
        loader.exec_module(video)
        source = {
            "interlaced": False, "height": 720, "width": 1280, "fps": "30",
            "video_codec": "h264", "audio_codec": "aac", "audio_bitrate": 96_000,
            "format": "mp4", "format_names": "mov,mp4",
        }

        under_limit = video._norm_assess(
            source, "auto", 1080, 30, "h264", "aac", "mp4", False, 160_000
        )
        self.assertTrue(under_limit["compliant"])

        source["audio_bitrate"] = 192_000
        over_limit = video._norm_assess(
            source, "auto", 1080, 30, "h264", "aac", "mp4", False, 160_000
        )
        self.assertFalse(over_limit["compliant"])
        self.assertIn("clamp audio 192 kb/s→≤160 kb/s", over_limit["reasons"])

    def test_video_normalise_can_retain_configured_av1(self):
        loader = importlib.machinery.SourceFileLoader("video_av1_test", str(ROOT / "video"))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        video = importlib.util.module_from_spec(spec)
        loader.exec_module(video)
        source = {
            "interlaced": False, "height": 720, "width": 1280, "fps": "30",
            "video_codec": "av1", "audio_codec": "aac", "audio_bitrate": 96_000,
            "format": "mp4", "format_names": "mov,mp4",
        }

        default = video._norm_assess(
            source, "auto", 1080, 30, "h264", "aac", "mp4", False, 160_000
        )
        retained = video._norm_assess(
            source, "auto", 1080, 30, "h264", "aac", "mp4", False, 160_000,
            ("av1",)
        )
        self.assertFalse(default["compliant"])
        self.assertTrue(retained["compliant"])

    def test_incomplete_normalise_cleans_partial_output_and_restores_original(self):
        loader = importlib.machinery.SourceFileLoader("video_cleanup_test", str(ROOT / "video"))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        video = importlib.util.module_from_spec(spec)
        loader.exec_module(video)

        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            root = pathlib.Path(tmp)
            original = root / "clip.avi"
            backup = root / "clip.avi.orig"
            partial = root / "clip.mp4"
            backup.write_bytes(b"original")
            partial.write_bytes(b"partial")

            removed, restored = video._cleanup_incomplete_normalise(
                str(partial), False, False, False, str(backup), str(original)
            )
            self.assertTrue(removed)
            self.assertTrue(restored)
            self.assertFalse(partial.exists())
            self.assertEqual(b"original", original.read_bytes())

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
