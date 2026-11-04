repro:
	python3 -m unittest discover -s tests -v
	python3 app.py

reproduce: repro

dev:
	python3 app.py --serve
