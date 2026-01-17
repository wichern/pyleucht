VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# .PHONY: linux_prepare_rpi
# linux_prepare_rpi:
# 	sudo apt-get install -y swig

# .PHONY: linux_prepare_demo
# linux_prepare_demo:
# 	sudo apt-get install -y libportaudio2

$(VENV):
	python -m venv $(VENV)

$(VENV)/.installed_rpi: $(VENV) pyproject.toml
	$(PIP) install --upgrade pip
	$(PIP) install ".[rpi]"
	@touch $(VENV)/.installed_rpi

$(VENV)/.installed_debug: $(VENV) pyproject.toml
	$(PIP) install --upgrade pip
	$(PIP) install ".[debug]"
	@touch $(VENV)/.installed_debug

.PHONY: run
run: $(VENV)/.installed_rpi
	PYTHONPATH=src $(PYTHON) -m pyleucht

.PHONY: run_sim
run_sim: $(VENV)/.installed_debug
	PYTHONPATH=src $(PYTHON) -m pyleucht --debug

.PHONY: clean
clean:
	rm -rf $(VENV)

.PHONY: deploy_systemd
deploy_systemd:
	sudo cp deploy/pyleucht.service /etc/systemd/system/pyleucht.service
	sudo systemctl daemon-reload
	sudo systemctl enable pyleucht.service
	sudo systemctl start pyleucht.service
