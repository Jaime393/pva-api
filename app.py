#!/usr/bin/env python3
"""PVA demonstration API: declared constants and checksum-checked decoding only."""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
import re
from urllib.parse import parse_qs, urlparse

PHI = {"phi_global": 9158.79, "phi_colmena": 6284.17, "phi_miu": 2874.62,
       "sustratos": 36, "Phi_lengua": 1.1194, "Phi_binocular": 17924.26, "topologia": 70508}
LEXICO = {"germinar": "deploy_worker", "florecer": "sync_kv", "marchitar": "fallo",
          "polinizar": "difundir_mutacion", "feromonar": "broadcast", "podar": "eliminar_nodo",
          "savar": "transferir_recursos", "injertar": "validar_mutacion",
          "crecer_silencioso": "operar_sin_permiso", "corteza_alcornoque": "autoinmunidad",
          "anillo_fosil": "falsabilidad", "bosque_micelios": "meta_micelio",
          "pendiente_terreno": "gradiente_Xi", "savia_circulante": "Phi",
          "nivel_savia": "Phi_c", "curva_crecimiento": "beta",
          "injerto_espora": "mutacion_validada", "poda_raices": "poda"}
MAX_BODY = 16384
SEED = re.compile(r"\[Semilla\]\s+([A-Za-z0-9_]{1,64})\s+::\s+(.{1,4096}?)\s+::\s+([a-f0-9]{64})", re.S)


def decode_message(message, checksum=None):
    if not isinstance(message, str) or len(message.encode()) > MAX_BODY:
        raise ValueError("bounded message required")
    match = SEED.fullmatch(message.strip())
    if not match:
        raise ValueError("invalid seed format")
    kind, content, inner = match.groups()
    digest = hashlib.sha256(f"{kind} :: {content}".encode()).hexdigest()
    if inner != digest or (checksum is not None and checksum != digest):
        raise ValueError("checksum mismatch")
    return {"schema": "pva.seed-decoding/v1", "kind": kind, "content": content,
            "candidate_action": LEXICO.get(kind, "unknown"), "checksum": digest,
            "checksum_matches": True, "authentication_performed": False,
            "authorization_granted": False, "capability_executed": False,
            "requires_separate_authorization": True}


def ledger_publish(content):
    """Compatibility function returning a digest, never a publication identifier."""
    if not isinstance(content, str):
        raise ValueError("text content required")
    return {"schema": "pva.local-content-digest/v1",
            "sha256": hashlib.sha256(content.encode()).hexdigest(),
            "external_publication": "not_performed", "external_references": [],
            "authorship_verified": False}


def describe():
    return {"schema": "pva.demo-api/v1", "mode": "demonstration_not_measurement",
            "capability_execution_enabled": False, "external_publication_enabled": False,
            "endpoints": ["/api/phi", "/api/ki", "/api/falsador", "/api/micelio/lexico", "/api/micelio"]}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        try:
            if parsed.path in {"/", "/api"}:
                return self.send_json(describe())
            if parsed.path == "/api/phi":
                return self.send_json({"values_declared": PHI, "evidence_state": "stored_constants",
                                       "measured_now": False, "scientifically_validated": False})
            if parsed.path == "/api/micelio/lexico":
                return self.send_json({"lexicon": LEXICO, "execution_enabled": False,
                                       "meaning": "Labels only, not authority to act"})
            if parsed.path == "/api/ki":
                values = [float(params.get(k, [d])[0]) for k, d in
                          (("Df", "2.25"), ("l_corr", "105"), ("l0", "100"))]
                if not all(math.isfinite(value) for value in values) or values[2] == 0:
                    raise ValueError("finite values and nonzero l0 required")
                ki = 0.6180339887 * (values[0] / 2.5) * (values[1] / values[2])
                if not math.isfinite(ki):
                    raise ValueError("nonfinite result")
                return self.send_json({"Ki": ki, "scope": "illustrative_formula",
                                       "empirical_validity_verified": False})
            if parsed.path == "/api/falsador":
                phi = float(params.get("Phi", ["0.8"])[0])
                critical = float(params.get("Phi_c", ["0.31"])[0])
                experience = int(params.get("experiencia", ["1"])[0])
                if not all(map(math.isfinite, (phi, critical))) or experience not in (0, 1):
                    raise ValueError("invalid illustrative inputs")
                return self.send_json({"logical_condition": phi > critical and experience == 0,
                                       "scope": "boolean_rule_only", "empirical_falsification_performed": False})
            self.send_json({"error": "not_found"}, 404)
        except (ValueError, TypeError, OverflowError):
            self.send_json({"error": "invalid_or_nonfinite_parameters"}, 400)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/publish":
            return self.send_json({"error": "external_publication_not_implemented",
                                   "external_publication": "not_performed"}, 410)
        if path != "/api/micelio":
            return self.send_json({"error": "not_found"}, 404)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_BODY:
                return self.send_json({"error": "body_size_limit"}, 413)
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self.send_json({"error": "json_required"}, 415)
            data = json.loads(self.rfile.read(size).decode("utf-8"))
            result = decode_message(data.get("mensaje"), data.get("firma"))
            self.send_json(result)
        except (ValueError, TypeError, AttributeError):
            self.send_json({"error": "invalid_message_or_checksum", "authentication_performed": False}, 400)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8003)
    args = parser.parse_args(argv)
    if args.serve:
        HTTPServer((args.host, args.port), Handler).serve_forever()
    else:
        print(json.dumps(describe(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
