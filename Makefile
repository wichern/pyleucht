VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Windows support
ifeq ($(OS),Windows_NT)
	PYTHON := $(VENV)/Scripts/python.exe
	PIP := $(VENV)/Scripts/pip.exe
endif

.PHONY: linux_prepare
linux_prepare:
	sudo apt-get install -y libportaudio2

$(VENV):
	python -m venv $(VENV)

$(VENV)/.installed: $(VENV) pyproject.toml
	@if ! dpkg -s libportaudio2 >/dev/null 2>&1; then \
		echo "libportaudio2 is not installed. Please run 'make linux_prepare'."; \
		exit 1; \
	fi
	$(PIP) install --upgrade pip
	$(PIP) install .
	@touch $(VENV)/.installed

.PHONY: run
run: $(VENV)/.installed
	PYTHONPATH=src $(PYTHON) -m pyleucht

.PHONY: run_sim
run_sim: $(VENV)/.installed
	PYTHONPATH=src $(PYTHON) -m pyleucht --debug

.PHONY: clean
clean:
	rm -rf $(VENV)
