# RF Jamming Detection Dashboard

This project is a real-time RF monitoring and jamming detection dashboard, designed for the RTL-SDR Blog V4 and Raspberry Pi 5. It visualizes spectrum activity via waterfall and power graphs, and logs jamming events using user-set thresholds.

## Features

- Real-time RF power and waterfall plots via Dash
- Jamming detection using power thresholds set by user
- Auto IQ data recording upon detection
- CSV + SQLite logging with frequency, power, and timestamp
- Modular UI with Dash tabs for monitoring and visualization

---

## Installation Instructions

### System Dependencies (Raspberry Pi OS / Debian-based):
```bash
sudo apt update
sudo apt install libatlas-base-dev libusb-1.0-0-dev rtl-sdr
```

### Python Environment:
```bash
python3 -m venv sdr-env
source sdr-env/bin/activate
pip install -r requirements.txt
```

Or, manually:
```bash
pip install dash plotly pyrtlsdr dash-bootstrap-components numpy==1.24.2 --prefer-binary
```

---

## Run the Dashboard
```bash
source sdr-env/bin/activate
python run.py
```

Then open your browser to: [http://127.0.0.1:8050](http://127.0.0.1:8050)

---

## Project Structure

```text
rf-jamming-dashboard/
├── app/                # Dash app initializer
├── callbacks/          # All callback logic (live graphing, event handling)
├── layouts/            # Dash layout code (tabs, plots)
├── core/               # SDR and logging utilities
├── db/                 # SQLite models
├── assets/             # CSS styling
├── run.py              # App entrypoint
├── config.py           # Global parameters
├── requirements.txt
└── README.md
```

---

## License

This project is for educational and research purposes. Built by Caleb Humber at Montana State University's Spectrum Lab.
