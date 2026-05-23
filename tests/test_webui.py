import pathlib
import time
import unittest

try:
    from webui.app import create_app
except ModuleNotFoundError as exc:
    if exc.name == "flask":
        create_app = None
    else:
        raise


ROOT = pathlib.Path(__file__).resolve().parents[1]


@unittest.skipIf(create_app is None, "Flask is not installed")
class WebUiTests(unittest.TestCase):
    def test_run_starts_pollable_job(self):
        app = create_app(ROOT, ROOT)
        client = app.test_client()

        response = client.post(
            "/api/run",
            json={
                "mode": "raw",
                "cwd": str(ROOT),
                "command_line": "bashcommon doctor --timeout 1",
            },
        )

        self.assertEqual(200, response.status_code, response.get_data(as_text=True))
        job = response.get_json()["job"]
        self.assertEqual("running", job["status"])

        for _ in range(40):
            response = client.get(f"/api/jobs/{job['id']}")
            self.assertEqual(200, response.status_code, response.get_data(as_text=True))
            job = response.get_json()["job"]
            if job["status"] != "running":
                break
            time.sleep(0.1)

        self.assertEqual("finished", job["status"])
        self.assertEqual(0, job["returncode"], job["stderr"])
        self.assertIn("Discovered", job["stdout"])


if __name__ == "__main__":
    unittest.main()
