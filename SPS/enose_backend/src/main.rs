// ===============================
 //  RUST E-NOSE BACKEND v2.1
 //  Arduino → Rust → GUI → InfluxDB 2 + STATUS BROADCAST
// ===============================

use std::io::{self, BufRead, BufReader, Write, Read};
use std::net::{TcpListener, TcpStream};
use std::sync::{mpsc, Arc, Mutex};
use std::thread;
use std::time::Duration;

use chrono::Utc;
use serde::{Deserialize, Serialize};
use reqwest::blocking::Client;

// ------------------------------
// KONFIGURASI (DITAMBAH PORT STATUS)
// ------------------------------
const ARDUINO_WIFI_ADDR: &str = "0.0.0.0:8081";
const GUI_DATA_ADDR:     &str = "127.0.0.1:8085";  // Diubah jadi 8085 biar match GUI terbaru
const GUI_CMD_ADDR:      &str = "0.0.0.0:8082";
const GUI_STATUS_ADDR:   &str = "127.0.0.1:8087";  // PORT BARU BUAT STATUS INFLUXDB

const SERIAL_PORT:       &str = "COM12";  
const BAUD_RATE: u32 = 9600;

// INFLUXDB v2 CONFIG
const INFLUX_URL:   &str = "http://localhost:8086/api/v2/write";
const INFLUX_TOKEN: &str = "jOeyQdgu58KLPoPOiMhGcnUZVjIKU80HT7umg30mU0z5V6wdzKpfSeT4X_g-MGLpuBaL_kmfZxznSs9irQfaUA==";
const INFLUX_ORG:   &str = "ITS";
const INFLUX_BUCKET:&str = "Cuz";

// ===============================
//    STRUCT RECORD SENSOR
// ===============================
#[derive(Clone, Debug, Serialize, Deserialize)]
struct SensorRecord {
    no2_gm: f64,
    ethanol_gm: f64,
    voc_gm: f64,
    co_gm: f64,
    co_mics: f64,
    ethanol_mics: f64,
    voc_mics: f64,
    state: i32,
    level: i32,
    timestamp: i128,
}

// ===============================
//   TULIS KE INFLUXDB V2 + BROADCAST STATUS
// ===============================
fn write_influx(record: &SensorRecord) -> bool {
    let line = format!(
        "gas_data no2_gm={},ethanol_gm={},voc_gm={},co_gm={},co_mics={},ethanol_mics={},voc_mics={},state={},level={} {}",
        record.no2_gm, record.ethanol_gm, record.voc_gm, record.co_gm,
        record.co_mics, record.ethanol_mics, record.voc_mics,
        record.state, record.level, record.timestamp
    );

    let client = Client::new();
    let url = format!("{}?org={}&bucket={}&precision=ns", INFLUX_URL, INFLUX_ORG, INFLUX_BUCKET);

    let success = client
        .post(&url)
        .header("Authorization", format!("Token {}", INFLUX_TOKEN))
        .header("Content-Type", "text/plain")
        .body(line.clone())
        .send()
        .map(|r| r.status().is_success())
        .unwrap_or(false);

    // BROADCAST STATUS KE GUI (real-time)
    let status_msg = if success { "INFLUX:OK" } else { "INFLUX:ERROR" };
    if let Ok(mut stream) = TcpStream::connect(GUI_STATUS_ADDR) {
        let _ = stream.write_all(status_msg.as_bytes());
    }

    if success {
        println!("InfluxDB: Data saved");
    } else {
        eprintln!("InfluxDB: Failed to save this point");
    }
    success
}

// ===============================
//            MAIN
// ===============================
fn main() {
    println!("=== RUST E-NOSE BACKEND v2.1 + INFLUXDB STATUS ===");

    let history = Arc::new(Mutex::new(Vec::<SensorRecord>::new()));
    let (tx_cmd, rx_cmd) = mpsc::channel::<String>();

    // SENSOR SERVER
    {
        let h = history.clone();
        thread::spawn(move || { 
            if let Err(e) = sensor_server(h) { 
                eprintln!("Sensor server error: {}", e); 
            } 
        });
    }

    // COMMAND SERVER
    {
        let tx = tx_cmd.clone();
        let h = history.clone();
        thread::spawn(move || { 
            if let Err(e) = command_server(tx, h) { 
                eprintln!("Command server error: {}", e); 
            } 
        });
    }

    // SERIAL WRITER (ke Arduino)
    thread::spawn(move || { 
        if let Err(e) = serial_sender(rx_cmd) { 
            eprintln!("Serial error: {}", e); 
        } 
    });

    loop { thread::sleep(Duration::from_secs(60)); }
}

// ===============================
//     SENSOR SERVER (Arduino → Rust)
// ===============================
fn sensor_server(history: Arc<Mutex<Vec<SensorRecord>>>) -> io::Result<()> {
    let listener = TcpListener::bind(ARDUINO_WIFI_ADDR)?;
    println!("SENSOR: Listening on {}", ARDUINO_WIFI_ADDR);

    for stream in listener.incoming() {
        let s = stream?;
        let h = history.clone();
        thread::spawn(move || {
            if let Err(e) = forward_to_gui_and_store(s, h) {
                eprintln!("forward error: {}", e);
            }
        });
    }
    Ok(())
}

fn forward_to_gui_and_store(stream: TcpStream, history: Arc<Mutex<Vec<SensorRecord>>>) -> io::Result<()> {
    let mut reader = BufReader::new(stream);
    let mut line = String::new();

    while reader.read_line(&mut line)? > 0 {
        let data = line.trim().to_string();
        if data.starts_with("SENSOR:") {
            println!("DATA: {}", data);

            if let Some(rec) = parse_sensor(&data) {
                // Simpan ke history
                {
                    let mut h = history.lock().unwrap();
                    h.push(rec.clone());
                }

                // AUTO SAVE + BROADCAST STATUS
                write_influx(&rec);

                // Kirim ke GUI
                if let Ok(mut gui) = TcpStream::connect(GUI_DATA_ADDR) {
                    let _ = gui.write_all(format!("{}\n", data).as_bytes());
                } else {
                    eprintln!("Could not connect to GUI at {}", GUI_DATA_ADDR);
                }
            }
        }
        line.clear();
    }
    Ok(())
}

// ===============================
//      PARSE SENSOR STRING
// ===============================
fn parse_sensor(raw: &str) -> Option<SensorRecord> {
    let parts: Vec<&str> = raw.split(':').nth(1)?.split(',').collect();
    if parts.len() < 9 { return None; }

    Some(SensorRecord {
        no2_gm: parts[0].parse().ok()?,
        ethanol_gm: parts[1].parse().ok()?,
        voc_gm: parts[2].parse().ok()?,
        co_gm: parts[3].parse().ok()?,
        co_mics: parts[4].parse().ok()?,
        ethanol_mics: parts[5].parse().ok()?,
        voc_mics: parts[6].parse().ok()?,
        state: parts[7].parse().ok()?,
        level: parts[8].parse().ok()?,
        timestamp: Utc::now().timestamp_nanos_opt()? as i128,
    })
}

// ===============================
//     COMMAND SERVER (GUI → Rust)
// ===============================
fn command_server(tx: mpsc::Sender<String>, history: Arc<Mutex<Vec<SensorRecord>>>) -> io::Result<()> {
    let listener = TcpListener::bind(GUI_CMD_ADDR)?;
    println!("COMMAND: Listening on {}", GUI_CMD_ADDR);

    for stream in listener.incoming() {
        let mut stream = stream?;
        let mut buf = String::new();
        stream.read_to_string(&mut buf)?;
        let cmd = buf.trim().to_uppercase();

        match cmd.as_str() {
            "START_SAMPLING" | "STOP_SAMPLING" => {
                let _ = tx.send(cmd.to_string());
                println!("Command sent to Arduino: {}", cmd);
            }
            "SAVE_INFLUX" | "SAVE_DATABASE" => {
                println!("FORCE SAVE TO INFLUXDB triggered from GUI");
                let data = history.lock().unwrap().clone();
                let mut success_count = 0;
                for rec in data.iter() {
                    if write_influx(rec) {
                        success_count += 1;
                    }
                }
                // Kirim status akhir ke GUI
                let final_status = if success_count == data.len() { "INFLUX:OK" } else { "INFLUX:ERROR" };
                if let Ok(mut s) = TcpStream::connect(GUI_STATUS_ADDR) {
                    let _ = s.write_all(final_status.as_bytes());
                }
                println!("FORCE SAVE complete: {}/{} points saved", success_count, data.len());
            }
            other => println!("Unknown command: {}", other),
        }
    }
    Ok(())
}

// ===============================
//   SERIAL WRITER (Rust → Arduino)
// ===============================
fn serial_sender(rx: mpsc::Receiver<String>) -> Result<(), Box<dyn std::error::Error>> {
    println!("SERIAL: Opening {}...", SERIAL_PORT);
    let mut port = serialport::new(SERIAL_PORT, BAUD_RATE)
        .timeout(Duration::from_millis(100))
        .open()?;

    println!("SERIAL: Connected to Arduino!");

    while let Ok(cmd) = rx.recv() {
        let line = format!("{}\n", cmd);
        port.write_all(line.as_bytes())?;
        port.flush()?;
        println!("→ Arduino: {}", cmd);
    }
    Ok(())
}