# KEL-8_SPS – Electronic Nose System  
**Tugas Besar – Sistem Pengolahan Sinyal**

## Overview
This project consists of a Rust-based backend and a Python (PyQt5) frontend for an electronic nose (E-Nose) data acquisition and visualization system.  
Data is streamed from an Arduino Uno R4/sensor board, stored in InfluxDB, Edge Impuls, and displayed in real-time on the GUI.

## How to Run the Project (Step-by-Step)

### 1. Clone or Download the Repository
```bash
git clone https://github.com/melzerr/KEL-8_SPS.git
cd KEL-8_SPS
Start the Rust Backend

Open a terminal
Navigate to the backend folder:
 cd SPS/enose_backend
Run the Backend: cargo run
Start the Python Frontend

Open a new terminal tab/window (keep the Rust backend running)
Go to the frontend directory: cd SPS
Launch the GUI:python main.py
The application window will appear.
### And Than
Required Configuration (Must be done on every computer!)
A. InfluxDB Token

Each computer uses a different InfluxDB token.
Open the file: SPS/enose_backend/src/main.rs (or the config module used)
Locate the InfluxDB token variable and replace it with your personal token.

B. Serial Port (COM Port)

The Arduino/serial port name differs on each laptop
(Windows: COM3, COM4, … | macOS/Linux: /dev/ttyUSB0, /dev/ttyACM0, …)
In the same Rust source file, find the serial port string
Replace it with the correct port for your machine
(You can verify the port in Arduino IDE → Tools → Port)

## Enjoy!
Once both terminals are running and the token/port are correctly configured:

Real-time sensor data will be received
Data is saved to InfluxDB
The GUI displays live graphs and controls

Notes

Never commit personal InfluxDB tokens or machine-specific COM ports to the repository.
The .gitignore file already excludes unnecessary files (__pycache__, target/, etc.).

Team
Kelompok 8 – Sistem Pengolahan Sinyal
Happy experimenting!
