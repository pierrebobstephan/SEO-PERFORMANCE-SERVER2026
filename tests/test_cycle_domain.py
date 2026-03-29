from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import json
import unittest

from electri_city_ops.orchestrator import run_cycle


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/sitemap.xml":
            payload = b"<urlset></urlset>"
            self.send_response(200)
            self.send_header("Content-Type", "application/xml; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        html = """
        <html lang="de">
          <head>
            <title>Electri City Studios 24/7</title>
            <meta name="description" content="Studio monitoring landing page" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <meta name="robots" content="index,follow" />
            <link rel="canonical" href="http://127.0.0.1/" />
          </head>
          <body>
            <h1>Studio Status</h1>
          </body>
        </html>
        """.strip().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "max-age=60")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


class DomainCycleTests(unittest.TestCase):
    def test_cycle_captures_raw_domain_results(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            with TemporaryDirectory() as tmp:
                root = Path(tmp)
                config_dir = root / "config"
                config_dir.mkdir(parents=True)
                config_path = config_dir / "settings.toml"
                config_path.write_text(
                    f"""
[system]
mode = "observe_only"
timezone = "UTC"

[targets]
domains = ["http://127.0.0.1:{server.server_port}"]
user_agent = "ElectriCityOps/Test"
request_timeout_seconds = 5
max_response_bytes = 65536

[permissions]
allow_remote_fetch = true
allow_external_changes = false
allow_workspace_self_healing = true

[reports]
formats = ["json", "markdown"]
""",
                    encoding="utf-8",
                )

                result = run_cycle(config_path, root)

                self.assertEqual(result.status, "validated")
                self.assertEqual(len(result.target_results), 1)
                snapshot = result.target_results[0]
                self.assertEqual(snapshot.homepage_status_code, 200)
                self.assertEqual(snapshot.sitemap_status_code, 200)
                self.assertEqual(snapshot.title, "Electri City Studios 24/7")
                self.assertEqual(snapshot.meta_description, "Studio monitoring landing page")
                self.assertEqual(snapshot.h1_count, 1)
                self.assertEqual(snapshot.html_lang, "de")
                self.assertTrue(snapshot.viewport_present)
                self.assertEqual(snapshot.robots_meta, "index,follow")
                self.assertEqual(snapshot.cache_control, "max-age=60")

                latest_json = json.loads((root / "var" / "reports" / "latest.json").read_text(encoding="utf-8"))
                latest_md = (root / "var" / "reports" / "latest.md").read_text(encoding="utf-8")
                self.assertEqual(latest_json["target_results"][0]["title"], "Electri City Studios 24/7")
                self.assertIn("## Domain Results", latest_md)
                self.assertIn("Sitemap status code: `200`", latest_md)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()

