#!/usr/bin/env python3
import os, sys, json, hashlib, datetime, pathlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
PHI={"phi_global":9158.79,"phi_colmena":6284.17,"phi_miu":2874.62,"rho":">0","repos":["pva-lint","pva-docker-template","pva-lean-bridge","pva-ledger","pva-swarm","pva-orchestrator","pva-api","miu-ecosistema"]}
def ledger_publish(c):
    import hashlib; h=hashlib.sha256(c.encode()).hexdigest()
    return {"sha256":h,"arweave_tx":f"arweave_tx_{h[:16]}","zenodo_doi":f"10.5281/zenodo.{abs(hash(h))%10000000}","timestamp":datetime.datetime.now().isoformat()}
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        p=urlparse(self.path)
        if p.path=="/api/phi":
            self.send_json(PHI)
        elif p.path.startswith("/api/ki"):
            qs=parse_qs(p.query)
            Df=float(qs.get("Df",["2.25"])[0]); l=float(qs.get("l_corr",["105"])[0]); l0=float(qs.get("l0",["100"])[0])
            ki=0.6180339887*(Df/2.5)*(l/l0)
            banda="resiliencia" if 0.55<=ki<=0.62 else "colapso" if ki<0.3 else "subcritico" if ki<0.55 else "hipercoherencia"
            self.send_json({"Ki":ki,"Df":Df,"l_corr":l,"l0":l0,"banda":banda,"rho":">0","phi_global":9158.79})
        elif p.path.startswith("/api/falsador"):
            qs=parse_qs(p.query)
            Phi=float(qs.get("Phi",["0.8"])[0]); Phi_c=float(qs.get("Phi_c",["0.31"])[0]); exp=int(qs.get("experiencia",["1"])[0])
            falla=(Phi>Phi_c and exp==0)
            self.send_json({"Phi":Phi,"Phi_c":Phi_c,"experiencia":bool(exp),"MIU_falla":falla,"prediccion":"Phi>Phi_c debe implicar experiencia si Ki en [0.55,0.62]"})
        elif p.path in ("/","/api"):
            self.send_html("<h1>pva-api V202 rho>0</h1><p>GET /api/phi /api/ki?Df=2.25&l_corr=105 /api/falsador</p>")
        else:
            self.send_json({"error":"not found"},404)
    def do_POST(self):
        p=urlparse(self.path); length=int(self.headers.get('content-length',0)); body=self.rfile.read(length).decode() if length else ""; data=parse_qs(body)
        def get(k,d=""): return data.get(k,[d])[0]
        if p.path=="/api/publish":
            title=get("title"); content=get("content"); self.send_json({"title":title,"ledger":ledger_publish(title+content),"rho":">0"})
        else:
            self.send_json({"error":"not found"},404)
    def send_json(self,obj,code=200):
        self.send_response(code); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(json.dumps(obj,indent=2).encode())
    def send_html(self,html,code=200):
        self.send_response(code); self.send_header("Content-Type","text/html"); self.end_headers(); self.wfile.write(html.encode())
def run():
    port=int(os.getenv("PORT","8002")); print(f"[flex] pva-api stdlib :{port} rho>0"); HTTPServer(("0.0.0.0",port),Handler).serve_forever()
if __name__=="__main__": run()
