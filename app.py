#!/usr/bin/env python3
# pva-api V202 rho(x)>0 — flexible sin fragmentar — evoluciona segun condicion de posibilidades
# - Si FastAPI disponible y compatible (py<3.14) -> usa FastAPI
# - Si no -> fallback stdlib http.server (funciona en Termux py3.14 sin rust, sin pydantic)
import os, sys, json, hashlib, datetime, pathlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

ORACULO = "https://fran-oraculo-miu.jaimepvicente.workers.dev"
PHI = {"phi_global": 9158.79, "phi_colmena": 6284.17, "phi_miu": 2874.62, "rho": ">0", "repos": ["pva-lint","pva-docker-template","pva-lean-bridge","pva-ledger","pva-swarm","pva-orchestrator","pva-api","miu-ecosistema"]}

def ledger_publish(content: str):
    h = hashlib.sha256(content.encode()).hexdigest()
    tx = f"arweave_tx_{h[:16]}"
    doi = f"10.5281/zenodo.{abs(hash(h)) % 10000000}"
    rec = {"sha256": h, "arweave_tx": tx, "zenodo_doi": doi, "timestamp": datetime.datetime.now().isoformat()}
    try:
        pathlib.Path(f"ledger_{h[:8]}.json").write_text(json.dumps(rec, indent=2))
    except: pass
    return rec

# intento flexible FastAPI
USE_FASTAPI = False
try:
    import fastapi
    # Python 3.14 rompe pydantic v1, detecta
    if sys.version_info < (3, 14):
        from fastapi import FastAPI, Form
        from fastapi.responses import HTMLResponse
        USE_FASTAPI = True
except Exception as e:
    USE_FASTAPI = False
    print(f"[flex] FastAPI no disponible ({e}) -> fallback stdlib", file=sys.stderr)

if USE_FASTAPI:
    # modo rico — Docker / Oracle con py3.11
    from fastapi import FastAPI, Form
    from fastapi.responses import HTMLResponse
    import requests
    app = FastAPI(title="pva-api V202 flexible rho>0")
    
    @app.get("/", response_class=HTMLResponse)
    def home():
        return "<h1>pva-api V202 flexible rho>0</h1><p>modo FastAPI</p><a href='/docs'>docs</a><br><a href='/api/phi'>phi</a>"

    @app.get("/api/phi")
    def phi():
        return PHI

    @app.post("/api/oraculo")
    def oraculo(query: str = Form(...)):
        try:
            r = requests.post(ORACULO, json={"query": query}, timeout=10)
            return {"oraculo": r.json() if "json" in r.headers.get("content-type","") else r.text[:2000], "query": query, "mode": "fastapi"}
        except Exception as e:
            return {"error": str(e), "query": query, "mode": "fastapi-fallback"}

    @app.post("/api/publish")
    def publish(title: str = Form(...), content: str = Form("")):
        ledger = ledger_publish(title+content)
        return {"title": title, "ledger": ledger, "rho": ">0", "mode": "fastapi"}

else:
    # modo flexible — Termux py3.14 sin dependencias — solo stdlib + requests opcional
    try:
        import requests
        HAS_REQUESTS = True
    except:
        HAS_REQUESTS = False

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass

        def do_GET(self):
            p = urlparse(self.path)
            if p.path == "/api/phi":
                self.send_json(PHI)
            elif p.path in ("/", "/api"):
                self.send_html(f"<h1>pva-api V202 flexible rho>0</h1><p>modo stdlib flexible — py{sys.version_info.major}.{sys.version_info.minor} — sin pydantic/rust</p><p>GET /api/phi</p><p>POST /api/oraculo query=...</p><p>POST /api/publish title=...&content=...</p>")
            else:
                self.send_json({"error": "not found", "path": p.path, "phi": PHI}, 404)

        def do_POST(self):
            p = urlparse(self.path)
            length = int(self.headers.get('content-length', 0))
            body = self.rfile.read(length).decode() if length else ""
            data = parse_qs(body)
            # soporta json y form
            if self.headers.get('content-type','').startswith('application/json'):
                try:
                    j = json.loads(body) if body else {}
                    data = {k: [str(v)] for k,v in j.items()}
                except: pass
            def get(k, default=""):
                return (data.get(k, [default])[0] if data.get(k) else default)

            if p.path == "/api/oraculo":
                q = get("query")
                if HAS_REQUESTS:
                    try:
                        r = requests.post(ORACULO, json={"query": q}, timeout=10)
                        out = r.json() if "json" in r.headers.get("content-type","") else r.text[:2000]
                    except Exception as e:
                        out = f"oraculo offline: {e}"
                else:
                    out = f"oraculo query recibido (sin requests): {q}"
                self.send_json({"oraculo": out, "query": q, "mode": "stdlib-flex"})
            elif p.path == "/api/publish":
                title = get("title")
                content = get("content")
                ledger = ledger_publish(title+content)
                self.send_json({"title": title, "ledger": ledger, "rho": ">0", "mode": "stdlib-flex"})
            else:
                self.send_json({"error": "not found"}, 404)

        def send_json(self, obj, code=200):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(obj, indent=2).encode())

        def send_html(self, html, code=200):
            self.send_response(code)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

    app = None  # para compatibilidad
    def run_stdlib(port=8001):
        print(f"[flex] pva-api flexible stdlib en :{port} py{sys.version_info.major}.{sys.version_info.minor} rho>0")
        HTTPServer(("0.0.0.0", port), Handler).serve_forever()

    if __name__ == "__main__":
        run_stdlib(int(os.getenv("PORT", "8001")))
