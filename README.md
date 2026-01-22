# CAN Tooling

Virtual CAN simulation and parsing framework.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
sudo ./scripts/setup_vcan.sh
python -m simulator.fake_ecu ## -m runs as script
python -m apps.live_monitor
