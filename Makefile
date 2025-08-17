.PHONY: deps
deps: requirements.txt venv
	.venv/bin/pip install -r requirements.txt

.PHONY: venv
venv: .venv/.gitignore

.venv:
	python3 -m venv .venv

.venv/.gitignore: .venv
	echo '*' > .venv/.gitignore

.PHONY: clean
clean:
	rm -r .venv