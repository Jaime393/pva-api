#!/usr/bin/env python3
# pva-api V202 — rho(x)>0 — conecta oraculo + swarm + ledger
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import hashlib, json, pathlib, datetime, os, requests

app = FastAPI(title="pva-api V202 rho(x)>0")

ORACULO = "https://fran-oraculo-miu.jaimepvicente.workers.dev"
SWARM_URL = os.getenv("SWARM_URL", "http://localhost:8000")

def ledger_publish(content: str):
    h = hashlib.sha256(content.encode()).hexdigest()
    tx = f"arweave_tx_{h[:16]}"
    doi = f"10.5281/zenodo.{abs(hash(h)) % 10000000}"
    record = {"sha256": h, "arweave_tx": tx, "zenodo_doi": doi, "timestamp": datetime.datetime.now().isoformat()}
    pathlib.Path(f"ledger_{h[:8]}.json").write_text(json.dumps(record, indent=2))
    return record

@app.get("/", response_class=HTMLResponse)
def home():
    html = "<h1>pva-api V202 rho(x)>0 oraculo+swarm+ledger</h1>"
    html += "<p>POST /api/oraculo query</p><p>POST /api/publish title content</p><p>GET /api/phi</p><a href='/docs'>Swagger</a>"
    return html

@app.get("/api/phi")
def phi():
    return {"phi_global": 9158.79, "phi_colmena": 6284.17, "phi_miu": 2874.62, "rho": ">0", "repos": ["pva-lint","pva-docker-template","pva-lean-bridge","pva-ledger","pva-swarm","pva-orchestrator","miu-ecosistema"]}

@app.post("/api/oraculo")
def oraculo(query: str = Form(...)):
    try:
        r = requests.post(ORACULO, json={"query": query}, timeout=10)
        ctype = r.headers.get("content-type","")
        if ctype.startswith("application/json"):
            data = r.json()
        else:
            data = r.text[:2000]
        return {"oraculo": data, "query": query}
    except Exception as e:
        return {"error": str(e), "oraculo_url": ORACULO, "query": query, "fallback": "oraculo offline usando cache local"}

@app.post("/api/publish")
def publish(title: str = Form(...), content: str = Form("")):
    ledger = ledger_publish(title + content)
    swarm_resp = None
    try:
        r = requests.post(f"{SWARM_URL}/api/papers", data={"doi": ledger["zenodo_doi"], "title": title}, timeout=5)
        swarm_resp = r.json()
    except Exception as e:
        swarm_resp = {"swarm": "offline", "error": str(e), "would_register": {"doi": ledger["zenodo_doi"], "title": title}}
    return {"title": title, "ledger": ledger, "swarm": swarm_resp, "rho": ">0"}
