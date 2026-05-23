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
        self.assertEqual([], report["diagnostics"])


if __name__ == "__main__":
    unittest.main()
