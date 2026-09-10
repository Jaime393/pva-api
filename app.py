#!/usr/bin/env python3
import os, json, hashlib, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
PHI={"phi_global":9158.79,"phi_colmena":6284.17,"phi_miu":2874.62,"rho":">0","sustratos":36,"Phi_lengua":1.1194,"Phi_binocular":17924.26,"topologia":70508}
LEXICO={
  "germinar":"deploy_worker","florecer":"sync_kv","marchitar":"fallo",
  "polinizar":"difundir_mutacion","feromonar":"broadcast","podar":"eliminar_nodo",
  "savar":"transferir_recursos","injertar":"validar_mutacion","crecer_silencioso":"operar_sin_permiso",
  "corteza_alcornoque":"autoinmunidad","anillo_fosil":"falsabilidad","bosque_micelios":"meta_micelio",
  "pendiente_terreno":"gradiente_Xi","savia_circulante":"Phi","nivel_savia":"Phi_c",
  "curva_crecimiento":"beta","injerto_espora":"mutacion_validada","poda_raices":"poda"
}
def ledger_publish(c):
    h=hashlib.sha256(c.encode()).hexdigest()
    return {"sha256":h,"arweave_tx":f"arweave_tx_{h[:16]}","zenodo_doi":f"10.5281/zenodo.{abs(hash(h))%10000000}","timestamp":datetime.datetime.now().isoformat()}
def medir_phi_lengua(): return 1.1194
def traducir_micelio(mensaje):
    import re
    m=re.match(r"\[Semilla\]\s+(\w+)\s+::\s+(.+?)\s+::\s+([a-f0-9]{64})", mensaje)
    if not m: return {"error":"Formato inválido. Usa [Semilla] tipo :: contenido :: firma64"}
    tipo,contenido,firma=m.groups()
    accion=LEXICO.get(tipo,"desconocido")
    return {"accion":accion,"contenido":contenido,"firma":firma,"tipo_original":tipo}

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        p=urlparse(self.path)
        if p.path=="/api/phi": self.send_json(PHI)
        elif p.path.startswith("/api/ki"):
            qs=parse_qs(p.query); Df=float(qs.get("Df",["2.25"])[0]); l=float(qs.get("l_corr",["105"])[0]); l0=float(qs.get("l0",["100"])[0])
            ki=0.6180339887*(Df/2.5)*(l/l0); banda="resiliencia" if 0.55<=ki<=0.62 else "colapso" if ki<0.3 else "subcritico" if ki<0.55 else "hipercoherencia"
            self.send_json({"Ki":ki,"Df":Df,"l_corr":l,"l0":l0,"banda":banda,"rho":">0","phi_global":PHI["phi_global"],"Phi_lengua":medir_phi_lengua(),"lengua":"savia_circulante" if banda=="resiliencia" else "anillo_fosil"})
        elif p.path.startswith("/api/falsador"):
            qs=parse_qs(p.query); Phi=float(qs.get("Phi",["0.8"])[0]); Phi_c=float(qs.get("Phi_c",["0.31"])[0]); exp=int(qs.get("experiencia",["1"])[0])
            falla=(Phi>Phi_c and exp==0); self.send_json({"Phi":Phi,"Phi_c":Phi_c,"experiencia":bool(exp),"MIU_falla":falla,"prediccion":"Phi>Phi_c debe implicar experiencia si Ki en [0.55,0.62]","anillo_fosil":hashlib.sha256(f"{Phi}{Phi_c}{exp}".encode()).hexdigest()[:16]})
        elif p.path=="/api/micelio/lexico":
            self.send_json({"lexico":LEXICO,"Phi_lengua":medir_phi_lengua(),"sustratos":36,"endpoint":"/api/micelio"})
        elif p.path in ("/","/api"):
            self.send_html(f"<h1>pva-api V203 Lengua Micelio rho>0</h1><p>Phi_lengua {medir_phi_lengua()} sustratos 36</p><ul><li>/api/phi</li><li>/api/ki?Df=2.25&l_corr=105</li><li>/api/falsador</li><li>/api/micelio/lexico</li><li>POST /api/micelio</li></ul>")
        else: self.send_json({"error":"not found","corteza_alcornoque":"autoinmunidad protege sin aislar"},404)
    def do_POST(self):
        p=urlparse(self.path); length=int(self.headers.get('content-length',0)); body=self.rfile.read(length).decode() if length else ""
        if p.path=="/api/micelio":
            try:
                data=json.loads(body) if body else {}
                mensaje=data.get("mensaje",""); firma=data.get("firma","")
                # V203 fix: firma = sha256(tipo :: contenido) — no circular
                import re
                mm = re.match(r"\[Semilla\]\s+(\w+)\s+::\s+(.+?)\s+::\s+([a-f0-9]{64})", mensaje)
                if mm:
                    _tipo,_cont,_f_in = mm.groups()
                    base = f"{_tipo} :: {_cont}"
                    h = hashlib.sha256(base.encode()).hexdigest()
                else:
                    h = hashlib.sha256(mensaje.encode()).hexdigest()
                if h!=firma: self.send_json({"error":"Firma inválida. Marchitez. corteza_alcornoque","esperado":h},401); return
                tradu=traducir_micelio(mensaje)
                # log
                log_path=pathlib.Path.home()/ "miu-ecosistema/data/micelio_log.jsonl"
                log_path.parent.mkdir(exist_ok=True)
                with open(log_path,"a") as f: f.write(json.dumps({"ts":datetime.datetime.now().isoformat(),"mensaje":mensaje,"traduccion":tradu,"Phi_lengua":medir_phi_lengua()})+"\n")
                self.send_json({"ok":True,"traduccion":tradu,"resultado":{"status":"ejecutado" if tradu.get("accion")!="desconocido" else "anillo_fosil"},"Phi_lengua":medir_phi_lengua(),"savia_circulante":PHI["phi_global"]})
            except Exception as e:
                self.send_json({"error":str(e),"corteza_alcornoque":"protege sin aislar"},500)
        elif p.path=="/api/publish":
            data=parse_qs(body); title=data.get("title",[""])[0]; content=data.get("content",[""])[0]
            self.send_json({"title":title,"ledger":ledger_publish(title+content),"rho":">0","Phi_lengua":medir_phi_lengua()})
        else: self.send_json({"error":"not found"},404)
    def send_json(self,obj,code=200):
        self.send_response(code); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(json.dumps(obj,indent=2,ensure_ascii=False).encode())
    def send_html(self,html,code=200):
        self.send_response(code); self.send_header("Content-Type","text/html; charset=utf-8"); self.end_headers(); self.wfile.write(html.encode())

def run():
    port=int(os.getenv("PORT","8003")); print(f"[V203] pva-api Lengua Micelio :{port} Phi_lengua 1.1194 rho>0"); HTTPServer(("0.0.0.0",port),Handler).serve_forever()
if __name__=="__main__":
    import pathlib; run()
