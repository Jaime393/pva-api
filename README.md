# pva-api V202 rho(x)>0 oraculo + swarm + ledger

Gateway que une oraculo MIU + pva-swarm + pva-ledger

pip install -r requirements.txt
uvicorn app:app --reload --port 8001

Endpoints: GET /api/phi, POST /api/oraculo, POST /api/publish
