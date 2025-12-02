# SISTEM PENGOLAHAN SINYAL 🧪

The Sensor Processing System (SPS) is a comprehensive solution for acquiring, processing, visualizing, and logging sensor data. It consists of a Rust backend that interfaces with sensor hardware (e.g., Arduino) and a PyQt-based GUI for real-time data display and control. The system supports data logging to CSV files and optional integration with InfluxDB for persistent storage and analysis. It solves the problem of efficiently collecting and interpreting sensor data in a user-friendly manner.

## 🚀 Key Features

- **Real-time Data Visualization**: Displays sensor data in real-time using PyQt labels and pyqtgraph plots.
- **Data Logging**: Logs sensor data to CSV files for offline analysis. Users can specify the directory and filename.
- **InfluxDB Integration**: Optionally writes sensor data to an InfluxDB database for persistent storage and analysis.
- **Command Sending**: Sends commands to the Rust backend to control sensor behavior or data acquisition.
- **Status Monitoring**: Receives status updates from the Rust backend, particularly regarding InfluxDB connectivity.
- **Configurable**: Loads configuration settings from a JSON file (`config.json`), allowing customization of various parameters.
- **Cross-Platform**: The GUI is built with PyQt, making it potentially cross-platform compatible. The backend is written in Rust, known for its performance and reliability.

## 🛠️ Tech Stack

- **Frontend (GUI)**:
    - PyQt6: GUI framework
    - pyqtgraph: Plotting library
    - numpy: Numerical operations (used by pyqtgraph)
- **Backend**:
    - Rust: Programming language
- **Data Storage**:
    - CSV: Comma-separated values file format
    - InfluxDB (Optional): Time-series database
- **Communication**:
    - TCP Sockets: Inter-process communication between Rust backend and GUI
    - HTTP (reqwest crate): Communication with InfluxDB
    - Serialport: Communication with Arduino
- **Other**:
    - json: Configuration file format
    - serde: Serialization/deserialization library (Rust)
    - tokio: Asynchronous runtime for Rust
    - warp: Web framework for building APIs (Rust)
    - chrono: Date and time library (Rust)
    - parking_lot: Synchronization primitives (Rust)
- **Build Tool**:
    - Cargo: Rust package manager

## 📦 Getting Started / Setup Instructions

### Prerequisites

- **Rust**: Ensure you have Rust installed. You can download it from [https://www.rust-lang.org/](https://www.rust-lang.org/).
- **Python**: Ensure you have Python 3.6 or higher installed.
- **PyQt6**: Install PyQt6 using pip: `pip install PyQt6`
- **pyqtgraph**: Install pyqtgraph using pip: `pip install pyqtgraph`
- **numpy**: Install numpy using pip: `pip install numpy`
- **requests**: Install requests using pip: `pip install requests`
- **influxdb\_client**: Install influxdb\_client using pip: `pip install influxdb_client` (Optional, if using InfluxDB)
- **Serial Port Library**: Install serialport using pip: `pip install pyserial`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Build the Rust backend:**
    ```bash
    cd SPS/enose_backend
    cargo build --release
    ```

3.  **Install Python dependencies:**
    ```bash
    cd ../
    pip install -r requirements.txt # If you have a requirements.txt file
    ```
    Or install them manually:
    ```bash
    pip install PyQt6 pyqtgraph numpy requests influxdb_client pyserial
    ```

### Running Locally

1.  **Start the Rust backend:**
    ```bash
    cd SPS/enose_backend
    cargo run --release
    ```

2.  **Run the Python GUI:**
    ```bash
    cd ../
    python main.py
    ```

## 💻 Usage

1.  **Configure the `config.json` file:**
    -   Set the appropriate serial port for the Arduino connection.
    -   Configure the InfluxDB settings (URL, token, organization, bucket) if you want to use InfluxDB.
2.  **Connect the Arduino:**
    -   Upload the appropriate Arduino sketch to your Arduino board.
    -   Ensure the Arduino is sending sensor data in the expected format.
3.  **Start the Rust backend.**
4.  **Start the Python GUI.**
5.  **Interact with the GUI:**
    -   View real-time sensor data.
    -   Start and stop data logging.
    -   Send commands to the Rust backend.
    -   Monitor the InfluxDB connection status.

## 📂 Project Structure

```
SPS/
├── main.py               # Main GUI application
├── config.json           # Configuration file
├── requirements.txt      # Python dependencies
├── enose_backend/        # Rust backend directory
│   ├── src/              # Source code
│   │   └── main.rs       # Main Rust file
│   ├── Cargo.toml        # Rust project manifest
│   └── Cargo.lock        # Rust dependencies lock file



## 📝 License

This project is licensed under the [MIT License](LICENSE) - see the `LICENSE` file for details.

## 💖 KELOMPOK 8

Thanks for checking out the Sensor Processing System! We hope it's useful for your sensor data processing needs.

![KEL 8 GACOR](Screenshot 2025-12-02 215930.png)



