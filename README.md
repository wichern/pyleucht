# Wiring

see https://learn.adafruit.com/retro-gaming-with-raspberry-pi/adding-controls-hardware

# Windows

```
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install ".[debug]"
$env:PYTHONPATH="src"
.\.venv\Scripts\python.exe -m pyleucht --debug
```
