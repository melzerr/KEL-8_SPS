import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QComboBox, QGroupBox, QGridLayout, QFileDialog, 
                             QMessageBox, QScrollArea)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import pyqtgraph as pg
import numpy as np
from datetime import datetime
import csv
import json
import os
import socket
import requests

# InfluxDB imports
try:
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False
    print("Warning: influxdb-client not installed. Run: pip install influxdb-client")

# ===============================
# RUST BACKEND CONFIGURATION
# ===============================
RUST_DATA_PORT = 8085      # Terima data dari Rust
RUST_CMD_PORT = 8082       # Kirim command ke Rust
RUST_STATUS_PORT = 8087    # Terima status InfluxDB dari Rust

# ===============================
# THREAD UNTUK TERIMA DATA DARI RUST
# ===============================
class DataReceiverThread(QThread):
    data_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('127.0.0.1', RUST_DATA_PORT))
            server.listen(1)
            server.settimeout(1.0)
            print(f"Data receiver listening on port {RUST_DATA_PORT}")
            
            while self.running:
                try:
                    conn, addr = server.accept()
                    print(f"Rust backend connected: {addr}")
                    
                    while self.running:
                        data = conn.recv(1024).decode('utf-8').strip()
                        if data:
                            for line in data.split('\n'):
                                if line.startswith('SENSOR:'):
                                    self.data_received.emit(line)
                        else:
                            break
                    conn.close()
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Data receiver error: {e}")
                    
        except Exception as e:
            print(f"Failed to start data receiver: {e}")
    
    def stop(self):
        self.running = False

# ===============================
# THREAD UNTUK TERIMA STATUS INFLUXDB
# ===============================
class StatusReceiverThread(QThread):
    status_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('127.0.0.1', RUST_STATUS_PORT))
            server.listen(1)
            server.settimeout(1.0)
            print(f"Status receiver listening on port {RUST_STATUS_PORT}")
            
            while self.running:
                try:
                    conn, addr = server.accept()
                    while self.running:
                        data = conn.recv(1024).decode('utf-8').strip()
                        if data:
                            self.status_received.emit(data)
                        else:
                            break
                    conn.close()
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Status receiver error: {e}")
                    
        except Exception as e:
            print(f"Failed to start status receiver: {e}")
    
    def stop(self):
        self.running = False

# ===============================
# MAIN GUI CLASS
# ===============================
class ENoseGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("E-Nose - Data Acquisition System")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }
            QGroupBox {
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                padding: 15px;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 11pt;
            }
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 8px;
            }
            QComboBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 8px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QPushButton {
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 11pt;
                border: none;
            }
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #1a1a1a;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #505050;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                background-color: #1a1a1a;
                height: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #404040;
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #505050;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
        """)
        
        self.is_sampling = False
        self.sample_count = 0
        self.time_data = []
        self.sensor_data = {
            'CO (MCS)': [], 'Ethanol (MCS)': [], 'VOC (MCS)': [],
            'NO2 (GM)': [], 'Ethanol (GM)': [], 'VOC (GM)': [], 'CO (GM)': []
        }
        
        self.influx_record_count = 0
        
        # Start receiver threads
        self.data_thread = DataReceiverThread()
        self.data_thread.data_received.connect(self.handle_sensor_data)
        self.data_thread.start()
        
        self.status_thread = StatusReceiverThread()
        self.status_thread.status_received.connect(self.handle_influx_status)
        self.status_thread.start()
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # ===== PANEL KIRI DENGAN SCROLLBAR =====
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setMaximumWidth(450)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #0a0a0a; }")
        
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #0a0a0a;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 15, 0)
        
        # Sample Information
        sample_group = QGroupBox("Sample Information")
        sample_layout = QGridLayout()
        
        sample_layout.addWidget(QLabel("Nama Sampel:"), 0, 0)
        self.sample_name = QLineEdit()
        self.sample_name.setPlaceholderText("Kopi Arabika")
        sample_layout.addWidget(self.sample_name, 1, 0)
        
        sample_layout.addWidget(QLabel("Jenis Sampel Uji:"), 2, 0)
        self.sample_type = QComboBox()
        self.sample_type.addItems(["Kopi Arabika", "Kopi Robusta", "Kopi Luwak", "Lainnya"])
        sample_layout.addWidget(self.sample_type, 3, 0)
        
        sample_group.setLayout(sample_layout)
        left_layout.addWidget(sample_group)
        
        # Sampling Control
        control_group = QGroupBox("Sampling Control")
        control_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("Start Sampling")
        self.start_btn.setStyleSheet("background-color: #7FFF7F; color: #000000; font-weight: bold;")
        self.start_btn.clicked.connect(self.start_sampling)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet("background-color: #FFB6C6; color: #000000; font-weight: bold;")
        self.stop_btn.clicked.connect(self.stop_sampling)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.save_btn = QPushButton("Save Data")
        self.save_btn.setStyleSheet("background-color: #FFD88A; color: #000000; font-weight: bold;")
        self.save_btn.clicked.connect(self.show_save_menu)
        control_layout.addWidget(self.save_btn)
        
        self.edge_impulse_btn = QPushButton("Upload to Edge Impulse")
        self.edge_impulse_btn.setStyleSheet("background-color: #87CEEB; color: #000000; font-weight: bold;")
        self.edge_impulse_btn.clicked.connect(self.upload_to_edge_impulse)
        control_layout.addWidget(self.edge_impulse_btn)
        
        control_group.setLayout(control_layout)
        left_layout.addWidget(control_group)
        
        # Status Koneksi
        status_group = QGroupBox("Status Koneksi")
        status_layout = QVBoxLayout()
        
        self.rust_status = QLabel("● Rust Backend: Waiting...")
        self.rust_status.setStyleSheet("color: #FFB84D; font-weight: bold;")
        status_layout.addWidget(self.rust_status)
        
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #7FFF7F; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        self.sample_count_label = QLabel("Samples: 0")
        self.sample_count_label.setStyleSheet("color: #e0e0e0;")
        status_layout.addWidget(self.sample_count_label)
        
        status_group.setLayout(status_layout)
        left_layout.addWidget(status_group)
        
        # Status InfluxDB
        influx_group = QGroupBox("Status InfluxDB")
        influx_layout = QVBoxLayout()
        
        self.influx_status = QLabel("● Waiting for data...")
        self.influx_status.setStyleSheet("color: #FFB84D; font-size: 12pt; font-weight: bold;")
        influx_layout.addWidget(self.influx_status)
        
        self.influx_last_write = QLabel("Last Write: -")
        self.influx_last_write.setStyleSheet("color: #b0b0b0;")
        influx_layout.addWidget(self.influx_last_write)
        
        self.influx_records = QLabel("Records Sent: 0")
        self.influx_records.setStyleSheet("color: #b0b0b0;")
        influx_layout.addWidget(self.influx_records)
        
        influx_group.setLayout(influx_layout)
        left_layout.addWidget(influx_group)
        
        # Sensor Readings
        readings_group = QGroupBox("Sensor Readings")
        readings_layout = QVBoxLayout()
        
        self.sensor_labels = {}
        for sensor in self.sensor_data.keys():
            label = QLabel(f"{sensor}: 0.00")
            label.setStyleSheet("background-color: #2a2a2a; padding: 8px; border-radius: 5px; color: #e0e0e0;")
            readings_layout.addWidget(label)
            self.sensor_labels[sensor] = label
        
        readings_group.setLayout(readings_layout)
        left_layout.addWidget(readings_group)
        
        left_layout.addStretch()
        
        # Set scroll area content
        scroll_area.setWidget(left_panel)
        main_layout.addWidget(scroll_area)
        
        # ===== PANEL KANAN - GRAFIK =====
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        title = QLabel("Real-Time Sensor Visualization")
        title.setStyleSheet("color: #ffffff; font-size: 16pt; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(title)
        
        # Grafik
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#1a1a2e')
        self.plot_widget.setLabel('left', 'Sensor Value (ppm)', color='#e0e0e0', **{'font-size': '11pt'})
        self.plot_widget.setLabel('bottom', 'Time (s)', color='#e0e0e0', **{'font-size': '11pt'})
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        self.plot_widget.getAxis('left').setPen(pg.mkPen(color='#505050', width=1))
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen(color='#505050', width=1))
        self.plot_widget.getAxis('left').setTextPen(pg.mkPen(color='#e0e0e0'))
        self.plot_widget.getAxis('bottom').setTextPen(pg.mkPen(color='#e0e0e0'))
        self.plot_widget.setYRange(0, 25)
        self.plot_widget.setXRange(0, 6)
        
        legend = self.plot_widget.addLegend(offset=(10, 10))
        legend.setParentItem(self.plot_widget.getPlotItem())
        legend.setBrush(pg.mkBrush(color=(26, 26, 46, 180)))
        legend.setPen(pg.mkPen(color='#404040', width=1))
        
        # Warna cantik sesuai referensi
        colors = ['#FF6B8A', '#FFB84D', '#FFE66D', '#4ECDC4', '#A78BFA', '#60A5FA', '#34D399']
        self.curves = []
        
        for sensor, color in zip(self.sensor_data.keys(), colors):
            curve = self.plot_widget.plot(pen=pg.mkPen(color=color, width=2.5), name=sensor)
            self.curves.append(curve)
        
        right_layout.addWidget(self.plot_widget)
        main_layout.addWidget(right_panel)
    
    def send_command_to_rust(self, command):
        """Kirim command ke Rust backend"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', RUST_CMD_PORT))
            sock.send(command.encode('utf-8'))
            sock.close()
            print(f"Command sent to Rust: {command}")
            return True
        except Exception as e:
            print(f"Failed to send command: {e}")
            QMessageBox.critical(self, "Error", f"Tidak dapat terhubung ke Rust backend:\n{str(e)}")
            return False
    
    def handle_sensor_data(self, data):
        """Handle data dari Rust backend"""
        # Update status koneksi
        self.rust_status.setText("● Rust Backend: Connected")
        self.rust_status.setStyleSheet("color: #7FFF7F; font-weight: bold;")
        
        # Parse: SENSOR:no2,ethanol,voc,co,co_mics,ethanol_mics,voc_mics,state,level
        try:
            parts = data.split(':')[1].split(',')
            if len(parts) >= 7:
                self.sample_count += 1
                self.time_data.append(self.sample_count * 0.1)
                
                # Map data ke sensor yang benar
                sensor_values = [
                    float(parts[4]),  # CO (MCS)
                    float(parts[5]),  # Ethanol (MCS)
                    float(parts[6]),  # VOC (MCS)
                    float(parts[0]),  # NO2 (GM)
                    float(parts[1]),  # Ethanol (GM)
                    float(parts[2]),  # VOC (GM)
                    float(parts[3]),  # CO (GM)
                ]
                
                for i, (sensor, value) in enumerate(zip(self.sensor_data.keys(), sensor_values)):
                    self.sensor_data[sensor].append(value)
                    self.sensor_labels[sensor].setText(f"{sensor}: {value:.2f}")
                
                # Update grafik
                for sensor, curve in zip(self.sensor_data.keys(), self.curves):
                    curve.setData(self.time_data, self.sensor_data[sensor])
                
                # Auto-scroll
                if len(self.time_data) > 60:
                    self.plot_widget.setXRange(self.time_data[-60], self.time_data[-1])
                
                self.sample_count_label.setText(f"Samples: {self.sample_count}")
                
        except Exception as e:
            print(f"Error parsing sensor data: {e}")
    
    def handle_influx_status(self, status):
        """Handle status InfluxDB dari Rust"""
        now = datetime.now().strftime("%H:%M:%S")
        
        if status == "INFLUX:OK":
            self.influx_status.setText("● Connected")
            self.influx_status.setStyleSheet("color: #7FFF7F; font-size: 12pt; font-weight: bold;")
            self.influx_last_write.setText(f"Last Write: {now}")
            self.influx_record_count += 1
            self.influx_records.setText(f"Records Sent: {self.influx_record_count}")
        elif status == "INFLUX:ERROR":
            self.influx_status.setText("● Write Failed")
            self.influx_status.setStyleSheet("color: #FF6B8A; font-size: 12pt; font-weight: bold;")
    
    def start_sampling(self):
        if self.send_command_to_rust("START_SAMPLING"):
            self.is_sampling = True
            self.sample_count = 0
            self.influx_record_count = 0
            self.time_data = []
            for key in self.sensor_data:
                self.sensor_data[key] = []
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Status: Sampling...")
            self.status_label.setStyleSheet("color: #7FFF7F; font-weight: bold;")
            self.influx_records.setText("Records Sent: 0")
        
    def stop_sampling(self):
        if self.send_command_to_rust("STOP_SAMPLING"):
            self.is_sampling = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("Status: Stopped")
            self.status_label.setStyleSheet("color: #FFB6C6; font-weight: bold;")
    
    def show_save_menu(self):
        msg = QMessageBox()
        msg.setWindowTitle("Save Data")
        msg.setText("Pilih format untuk menyimpan data:")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
        """)
        
        csv_btn = msg.addButton("CSV", QMessageBox.ActionRole)
        json_btn = msg.addButton("JSON", QMessageBox.ActionRole)
        both_btn = msg.addButton("Both", QMessageBox.ActionRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)
        
        msg.exec_()
        
        if msg.clickedButton() == csv_btn:
            self.save_to_csv()
        elif msg.clickedButton() == json_btn:
            self.save_to_json()
        elif msg.clickedButton() == both_btn:
            self.save_to_csv()
            self.save_to_json()
    
    def save_to_csv(self):
        if not self.time_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk disimpan!")
            return
        
        sample_name = self.sample_name.text() or "sample"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{sample_name}_{timestamp}.csv"
        
        filepath, _ = QFileDialog.getSaveFileName(self, "Save CSV", filename, "CSV Files (*.csv)")
        
        if filepath:
            try:
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)
                    header = ['Time(s)'] + list(self.sensor_data.keys())
                    writer.writerow(header)
                    
                    for i in range(len(self.time_data)):
                        row = [self.time_data[i]]
                        for sensor in self.sensor_data.keys():
                            row.append(self.sensor_data[sensor][i])
                        writer.writerow(row)
                
                QMessageBox.information(self, "Success", f"CSV saved:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed:\n{str(e)}")
    
    def save_to_json(self):
        if not self.time_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk disimpan!")
            return
        
        sample_name = self.sample_name.text() or "sample"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{sample_name}_{timestamp}.json"
        
        filepath, _ = QFileDialog.getSaveFileName(self, "Save JSON", filename, "JSON Files (*.json)")
        
        if filepath:
            try:
                data_dict = {
                    "metadata": {
                        "sample_name": self.sample_name.text(),
                        "sample_type": self.sample_type.currentText(),
                        "timestamp": datetime.now().isoformat(),
                        "total_samples": len(self.time_data)
                    },
                    "data": []
                }
                
                for i in range(len(self.time_data)):
                    data_point = {"time": self.time_data[i], "sensors": {}}
                    for sensor in self.sensor_data.keys():
                        data_point["sensors"][sensor] = self.sensor_data[sensor][i]
                    data_dict["data"].append(data_point)
                
                with open(filepath, 'w') as f:
                    json.dump(data_dict, f, indent=2)
                
                QMessageBox.information(self, "Success", f"JSON saved:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed:\n{str(e)}")
    
    def upload_to_edge_impulse(self):
        if not self.time_data:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk diupload!")
            return

        EI_API_KEY = "ei_396c0281d6cfea3e2215c4d947e0bc9fdd208e1a7551b20e3b29c94dd5d28bf0"
        EI_PROJECT_ID = "827201"
        label = self.sample_type.currentText()
        sample_name = self.sample_name.text() or "sample"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"edge_impulse_{sample_name}_{timestamp}.csv"
        temp_path = os.path.join(os.getcwd(), temp_filename)

        numeric_header = ['timestamp'] + [str(i) for i in range(len(self.sensor_data))]

        try:
            with open(temp_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(numeric_header)

                start_time = int(datetime.now().timestamp() * 1000)
                for i in range(len(self.time_data)):
                    ts = start_time + int(self.time_data[i] * 1000)
                    row = [ts]
                    for sensor in self.sensor_data.keys():
                        row.append(self.sensor_data[sensor][i])
                    writer.writerow(row)

            url = "https://ingestion.edgeimpulse.com/api/training/files"
            
            with open(temp_path, 'rb') as file_obj:
                files = {'data': (os.path.basename(temp_path), file_obj, 'text/csv')}
                headers = {
                    "x-api-key": EI_API_KEY,
                    "x-file-name": os.path.basename(temp_path),
                    "x-label": label,
                    "x-project-id": EI_PROJECT_ID
                }
                response = requests.post(url, files=files, headers=headers, timeout=60)

            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Upload ke Edge Impulse berhasil!")
                self.status_label.setText("Status: Uploaded to EI")
                self.status_label.setStyleSheet("color: #87CEFA;")
            else:
                QMessageBox.critical(self, "Failed", f"Upload failed: {response.status_code}\n{response.text}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error:\n{str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def closeEvent(self, event):
        self.data_thread.stop()
        self.status_thread.stop()
        self.data_thread.wait()
        self.status_thread.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ENoseGUI()
    window.show()
    sys.exit(app.exec())