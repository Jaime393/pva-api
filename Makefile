repro:
	python -m py_compile app.py
	python -c "import app; print('pva-api flexible ok phi 9158.79')"

reproduce: repro

dev:
	python app.py
