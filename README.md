# pva-api V202 flexible — sin fragmentar — evoluciona segun condicion

Un solo app.py que:
- si FastAPI+pydantic disponible (py3.11 Docker/Oracle) -> usa FastAPI
- si no (Termux py3.14 sin rust) -> fallback stdlib http.server

No fragmenta: mismo codigo, dos modos.

```bash
pip install requests -q
python app.py # stdlib :8001
# o
pip install fastapi uvicorn python-multipart
uvicorn app:app --port 8001 # si compatible
```

Endpoints: GET /api/phi, POST /api/oraculo, POST /api/publish
Phi 9158.79 rho>0
