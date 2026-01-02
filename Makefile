VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Windows support
ifeq ($(OS),Windows_NT)
	PYTHON := $(VENV)/Scripts/python.exe
	PIP := $(VENV)/Scripts/pip.exe
endif

# .PHONY: linux_prepare
# linux_prepare:
# 	sudo apt-get install -y libportaudio2

$(VENV):
	python -m venv $(VENV)

$(VENV)/.installed: $(VENV) pyproject.toml
	$(PIP) install --upgrade pip
	$(PIP) install .
	@touch $(VENV)/.installed

$(VENV)/.installed_debug: $(VENV)/.installed pyproject.toml
	$(PIP) install --upgrade pip
	$(PIP) install ".[debug]"
	@touch $(VENV)/.installed_debug

.PHONY: run
run: $(VENV)/.installed
	PYTHONPATH=src $(PYTHON) -m pyleucht

.PHONY: run_sim
run_sim: $(VENV)/.installed_debug
	PYTHONPATH=src $(PYTHON) -m pyleucht --debug

.PHONY: clean
clean:
	rm -rf $(VENV)
