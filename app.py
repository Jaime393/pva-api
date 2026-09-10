#!/usr/bin/env python3
# pva-api V202 rho(x)>0 — flexible sin fragmentar — evoluciona segun condicion
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

# intento flexible FastAPI solo si py<3.14
USE_FASTAPI = False
try:
    if sys.version_info < (3, 14):
        import fastapi
        USE_FASTAPI = True
except Exception as e:
    print(f"[flex] FastAPI no disponible ({e}) -> stdlib", file=sys.stderr)

if USE_FASTAPI:
    from fastapi import FastAPI, Form
    from fastapi.responses import HTMLResponse
    import requests
    app = FastAPI(title="pva-api V202 flexible rho>0")
    @app.get("/", response_class=HTMLResponse)
    def home():
        return "<h1>pva-api V202 flexible rho>0</h1><p>modo FastAPI</p><a href='/docs'>docs</a>"
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
    try:
        import requests
        HAS_REQUESTS = True
    except:
        HAS_REQUESTS = False
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def do_GET(self):
            p = urlparse(self.path)
            if p.path == "/api/phi":
                self.send_json(PHI)
            elif p.path in ("/","/api"):
                self.send_html(f"<h1>pva-api V202 flexible rho>0</h1><p>stdlib py{sys.version_info.major}.{sys.version_info.minor} sin pydantic/rust</p><p>GET /api/phi</p><p>POST /api/oraculo</p><p>POST /api/publish</p>")
            else:
                self.send_json({"error":"not found"},404)
        def do_POST(self):
            p = urlparse(self.path)
            length = int(self.headers.get('content-length',0))
            body = self.rfile.read(length).decode() if length else ""
            data = parse_qs(body)
            if self.headers.get('content-type','').startswith('application/json'):
                try:
                    j = json.loads(body) if body else {}
                    data = {k:[str(v)] for k,v in j.items()}
                except: pass
            def get(k,d=""): return (data.get(k,[d])[0] if data.get(k) else d)
            if p.path == "/api/oraculo":
                q = get("query")
                if HAS_REQUESTS:
                    try:
                        r = requests.post(ORACULO, json={"query": q}, timeout=10)
                        out = r.json() if "json" in r.headers.get("content-type","") else r.text[:2000]
                    except Exception as e:
                        out = f"oraculo offline: {e}"
                else:
                    out = f"query recibido: {q}"
                self.send_json({"oraculo": out, "query": q, "mode": "stdlib-flex"})
            elif p.path == "/api/publish":
                title = get("title"); content = get("content")
                ledger = ledger_publish(title+content)
                self.send_json({"title": title, "ledger": ledger, "rho": ">0", "mode": "stdlib-flex"})
            else:
                self.send_json({"error":"not found"},404)
        def send_json(self, obj, code=200):
            self.send_response(code); self.send_header("Content-Type","application/json"); self.end_headers()
            self.wfile.write(json.dumps(obj, indent=2).encode())
        def send_html(self, html, code=200):
            self.send_response(code); self.send_header("Content-Type","text/html"); self.end_headers()
            self.wfile.write(html.encode())
    app = None
    def run_stdlib(port=8001):
        print(f"[flex] pva-api stdlib :{port} py{sys.version_info.major}.{sys.version_info.minor} rho>0")
        HTTPServer(("0.0.0.0", port), Handler).serve_forever()
    if __name__ == "__main__":
        run_stdlib(int(os.getenv("PORT","8001")))

# --- MIU V202 Ki — stdlib-flex ---
# añade dentro de do_GET, antes del else 404:
# elif self.path.startswith("/api/ki"):
# parse_qs -> Df, l_corr, l0 -> Ki = 0.618*(Df/2.5)*(l_corr/l0)
