import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import threading
from http.server import HTTPServer
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("api", ROOT / "app.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class APITests(unittest.TestCase):
    def seed(self, kind="podar", content="example node"):
        digest = hashlib.sha256(f"{kind} :: {content}".encode()).hexdigest()
        return f"[Semilla] {kind} :: {content} :: {digest}", digest

    def test_checksum_is_not_authority(self):
        message, digest = self.seed()
        r = MODULE.decode_message(message, digest)
        self.assertEqual(r["candidate_action"], "eliminar_nodo")
        self.assertTrue(r["checksum_matches"])
        for key in ("authentication_performed", "authorization_granted", "capability_executed"):
            self.assertFalse(r[key])

    def test_inner_and_outer_checksum_checked(self):
        message, digest = self.seed()
        for seed, outer in ((message, "0" * 64), (message.replace(digest, "0" * 64), digest)):
            with self.assertRaises(ValueError):
                MODULE.decode_message(seed, outer)

    def test_malformed_message(self):
        for message in ("unknown", None, "x" * (MODULE.MAX_BODY + 1)):
            with self.assertRaises(ValueError):
                MODULE.decode_message(message)

    def test_no_fabricated_publication(self):
        r = MODULE.ledger_publish("content")
        self.assertEqual(r["external_publication"], "not_performed")
        self.assertEqual(r["external_references"], [])
        self.assertNotIn("arweave_tx", r)
        self.assertNotIn("zenodo_doi", r)

    def server(self):
        server = HTTPServer(("127.0.0.1", 0), MODULE.Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return f"http://127.0.0.1:{server.server_port}"

    def test_http_declared_constants(self):
        with urlopen(self.server() + "/api/phi", timeout=3) as response:
            r = json.load(response)
        self.assertFalse(r["measured_now"])
        self.assertFalse(r["scientifically_validated"])

    def test_http_decode_without_execution(self):
        message, digest = self.seed()
        request = Request(self.server() + "/api/micelio",
                          data=json.dumps({"mensaje": message, "firma": digest}).encode(),
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=3) as response:
            self.assertFalse(json.load(response)["capability_executed"])

    def test_http_publish_not_performed(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(Request(self.server() + "/api/publish", data=b"title=example"), timeout=3)
        self.assertEqual(error.exception.code, 410)
        error.exception.close()

    def test_bad_numeric_input_is_blocked(self):
        url = self.server()
        for query in ("l0=0", "Df=nan", "l_corr=inf"):
            with self.assertRaises(HTTPError) as error:
                urlopen(url + "/api/ki?" + query, timeout=3)
            self.assertEqual(error.exception.code, 400)
            error.exception.close()

    def test_default_cli_does_not_start_server(self):
        p = subprocess.run([sys.executable, str(ROOT / "app.py")],
                           capture_output=True, text=True, timeout=5)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertFalse(json.loads(p.stdout)["capability_execution_enabled"])


if __name__ == "__main__":
    unittest.main()
