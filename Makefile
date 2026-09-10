repro:
	python -m py_compile app.py
	python -c "import app; print('pva-api ok phi 9158.79')"

reproduce:
	python -m py_compile app.py

dev:
	uvicorn app:app --reload --port 8001
