# CAN Tooling

A Python-based virtual CAN bus simulation and parsing framework for automotive and embedded systems development. This is the subsection which deals with the actual fetching, parsing, categorizing and publishing aspects of the Risk Avoidance Systems. This module contains the scripts to initiate and set-up a new connection with a vehicle as well as the scripts to begin reading, categorizing and publishing risky data. The module also contains code to simulate test data as well as replay previous CAN data. Overall the CANbus data is read by the CL2000 which streams the raw data to a python script that proceeds to decode the data using a dbc file. A frame is produced every 16Hz (bumped down from 50Hz for performance reasons), each frame consists of the required vehicle data such as throttle, brake percentages, steering angle, gps coordinates, handbrake and turn signals statuses as well as door status. After the production of each frame, it is passed to a function responsible for determining risks present in the data by cross refrencing the frame against a set of rules constructed by us (i.e: Hard braking, turn without signal, unsafe acceleration), meanwhile theres a camera detection script which idenitfies the users attentiveness produces data which is also categorized alongside the frame. If risks have been found, the system publishes the risk object along with vehicle data to the RAS server which checks the geohash of the risky vehicle and notifies other vehicles around the risky car via each connected car's CarPlay/Android Auto Instances

Overall the RAS is composed of 4 subsystems: 

The CANBUS Categorization and Publish Module (This Github Repository)

The Video Dection Module: https://github.com/deep-patel21/VideoDetectionModule-RAS

The MQTT RAS Server: https://github.com/RyanKhuu/Capstone-MQTT

The Android Auto Interface: https://github.com/anmolp476/AndroidAutoAppForRAS

## Overview

CANTOOLING provides a comprehensive toolkit for working with Controller Area Network (CAN) bus systems in both simulated and real-world environments. The framework supports two operating modes:

- **Simulation Mode**: Uses virtual CAN (vcan) interfaces for hardware-free development, testing, and education
- **Network Mode**: Connects to physical CAN hardware (CL2000 interface) for real-world communication and data capture

This dual-mode approach makes CANTOOLING ideal for the complete development lifecycle—from initial prototyping and testing in simulation, to deployment and debugging with actual CAN bus hardware.

## Features

### Operating Modes

- **Simulation Mode**: Virtual CAN interface for hardware-free development and testing
- **Network Mode**: Direct integration with CL2000 CAN hardware for real-world communication

### Core Capabilities

- **Virtual CAN Simulation**: Create and manage virtual CAN (vcan) interfaces for hardware-free development
- **Telemetry Replay**: Replay logged CAN messages for testing and analysis
- **Live Monitoring**: Real-time visualization and monitoring of CAN bus messages
- **Signal Decoding**: Parse and decode CAN messages using DBC database files
- **Message Logging**: Capture and log CAN bus traffic for analysis
- **Hardware Integration**: Support for CL2000 CAN interface devices
- **Rich Terminal UI**: User-friendly terminal interface for monitoring and debugging

## Technology Stack

- **python-can**: CAN bus communication support for Python
- **cantools**: DBC file parsing, message encoding/decoding
- **rich**: Beautiful terminal UI and formatting

## Installation

### Prerequisites

**For Simulation Mode:**
- Python 3.10 or higher
- Linux-based system (for virtual CAN support)
- Root/sudo access (for vcan interface setup)

**For Network Mode (additional requirements):**
- CL2000 CAN interface device
- Appropriate device drivers and permissions

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Yanny24211/CANTOOLING.git
cd CANTOOLING
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the package in editable mode:
```bash
pip install -e .
```

4. Set up virtual CAN interface:
```bash
sudo ./scripts/setup_vcan.sh
```

## Quick Start

### Simulation Mode (No Hardware Required)

For testing and development without physical CAN hardware:

1. **Set up virtual CAN interface**:
```bash
sudo ./scripts/setup_vcan.sh
```

2. **Run test telemetry**:
```bash
python -m test_telemetry
```

3. **Replay logged data** (in a separate terminal):
```bash
python -m replay_log
```

4. **Monitor CAN traffic** (optional, in another terminal):
```bash
python -m apps.live_monitor
# or
can-monitor
```

### Network Mode (With CL2000 Hardware)

For real-world CAN bus communication with physical hardware:

1. **Connect the CL2000 device** to your system

2. **Run the telemetry script**:
```bash
python telemetry.py
```

> **Note**: Network mode requires the CL2000 CAN interface to be properly connected and configured.

## Project Structure

```
CANTOOLING/
├── apps/              # Application modules
│   ├── live_monitor   # Real-time CAN bus monitoring
│   └── logger         # CAN message logging
├── dbc/               # DBC database files for message definitions
├── rascan/            # CAN scanning utilities
├── scripts/           # Setup and utility scripts
│   └── setup_vcan.sh  # Virtual CAN interface setup
├── signals/           # Signal processing and decoding
├── simulator/         # ECU and traffic simulation
├── tests/             # Unit and integration tests
├── test_telemetry.py  # Simulation mode: test telemetry generator
├── replay_log.py      # Simulation mode: log replay utility
├── telemetry.py       # Network mode: CL2000 hardware interface
└── pyproject.toml     # Project configuration and dependencies
```

## Usage Examples

### Simulation Mode Workflow

1. Set up the virtual CAN interface once per system boot
2. Run test telemetry to generate CAN traffic
3. Use replay_log to replay captured messages
4. Monitor live traffic with the monitoring tools

### Network Mode Workflow

1. Connect the CL2000 CAN interface device
2. Run telemetry.py to establish communication
3. Use monitoring tools to observe real CAN bus traffic

### Working with DBC Files

DBC (Database CAN) files define the structure of CAN messages and signals. Place your DBC files in the `dbc/` directory to use them with the monitoring and simulation tools.

### Signal Analysis

Use the signals module to decode, process, and analyze specific signals from CAN messages based on your DBC definitions.

## Hardware

### CL2000 CAN Interface

The CL2000 is a CAN bus interface device used for network mode operation. When connected, it allows CANTOOLING to communicate with physical CAN networks for:

- Real-world data capture
- Production system testing
- Hardware-in-the-loop validation
- Field debugging and diagnostics

## CLI Commands

After installation, the following commands are available:

- `can-monitor`: Launch the live CAN bus monitor
- `can-logger`: Start logging CAN messages to file

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

The project follows a modular architecture:
- **apps/**: User-facing applications
- **simulator/**: Backend simulation logic
- **signals/**: Signal processing and decoding
- **rascan/**: Network scanning and discovery

## What is CAN Bus?

Controller Area Network (CAN) is a robust vehicle bus standard designed to allow microcontrollers and devices to communicate with each other without a host computer. It's widely used in:

- Automotive systems
- Industrial automation
- Medical devices
- Aerospace applications

## Virtual CAN (vcan)

This project uses Linux's virtual CAN interface (vcan), which allows CAN bus development and testing without physical CAN hardware. Virtual CAN provides:

- Zero-cost development environment
- Reproducible test scenarios
- Safe experimentation without risk to physical systems
- Perfect for CI/CD integration

## Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and create pull requests.

## License

This project is open source. Please check the repository for license details.

## Resources

- [python-can Documentation](https://python-can.readthedocs.io/)
- [cantools Documentation](https://cantools.readthedocs.io/)
- [CAN Bus Protocol Overview](https://en.wikipedia.org/wiki/CAN_bus)
- [DBC File Format Specification](https://www.csselectronics.com/pages/can-dbc-file-database-intro)

## Support

For questions, issues, or feature requests, please use the GitHub issue tracker.

## Author

Yanny Patel ([@Yanny24211](https://github.com/Yanny24211))

---

**Note**: This project is designed for development and testing purposes. Always ensure proper testing and validation before deploying any CAN bus related software in production environments, especially in safety-critical systems.
