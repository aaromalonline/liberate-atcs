<p align="center">
  <img src="./assets/liberatelogo-gif.gif" alt="Liberate Logo">
</p>

# **Liberate : ATCS - Adaptive Typing & Control System**  
### *Freedom Beyond Barriers*  

[![Repository Status](https://img.shields.io/badge/Repository%20Status-Prototype-dark%20green.svg)](https://github.com/aaromalonline/liberate)
[![Author](https://img.shields.io/badge/Author-Aaromal%20A-purple.svg)](https://www.linkedin.com/in/aaromalonline/)
[![Latest Release](https://img.shields.io/badge/Latest%20Release-11%20Feb%202025-yellow.svg)](https://github.com/aaromalonline/liberate)
<a href="https://github.com/aaromalonline/liberate/blob/master/LICENSE"><img alt="License" src="http://img.shields.io/:license-mit-blue.svg?style=flat-square?style=flat-square" /></a>

**Liberate:ATCS** is a muscle-twitch-based communication system that translates subtle muscle movements into control signals through an adaptive typing interface. By detecting slight facial or body muscle activity, it enables users to operate devices such as a computer cursor, wheelchair, or keyboard. This innovative, hands-free solution enhances accessibility and communication for individuals with limited mobility, bridging the gap between physical limitations and digital interaction. Designed for real-time responsiveness and ease of use, Liberate: ATCS offers an intuitive and efficient alternative for assistive control.

📢 [Presentation](https://www.canva.com/design/DAGgiwwJF50/0pNmzq6Z0drq8x91x3Nejg/view)

𝒎𝒂𝒅𝒆 𝒘𝒊𝒕𝒉 ❤️ 𝑻𝒆𝒂𝒎 𝑳𝒖𝒎𝒆𝒏 :
[![Contributor: Aaromal A](https://img.shields.io/badge/Contributor-Aaromal%20A-purple.svg)](https://www.linkedin.com/in/aaromalonline/) [![Contributor: Deeraj P Menon](https://img.shields.io/badge/Contributor-Deeraj%20P%20Menon-purple.svg)](https://www.linkedin.com/in/deeraj-p-menon-aa4b5231b/)

inspired by [Intel's ACAT](https://www.intel.com/content/www/us/en/developer/tools/open/acat/overview.html) 


## 🛠️ Technologies Used
- **Python** for signal processing & control logic
- **ESP32** for sensor data acquisition via I2C and encoding of muscle twitches to control signals
- **ADXL345 Digital Accelerometer/Tap Sensor** for muscle movement detection (also IR reflexive sensor)

## 🚀 Features
- **Muscle twitch detector/encoder** using ADXL345 digital accelerometer & ESP32 to convert muscle twitches to control signals/clicks
- **Muscle controlled keyboard** with QWERTY & Morse mode available as a PyQt5 python desktop
- **Built-in SOS & speech synthesis** using a specch engine like gTTS
- **A minimal, cost-effective design** for real-world usability

### 👀 Comming soon
- Auto AI typing suggestions
- UNiversal app interface 
- More control features like browse, advanced SOS messaging etc
- Multiple sensor inputs & Minimal hardware implimentation

## 💻 How it works? 
- **Sensor + Encoder** - When ON, The ADXL345 accelerometer records muscle twitches as 3-axis accelerations, which are encoded into clicks (0/1) using baseline calibration and filtering algorithms such as edge detection & debouncing filters.
- **Data Transmission** - Data is sent serially/wirelessly via ESP32 to the python application using I2C, where the user can control a keyboard interface using the decoded twitch clicks.
- **Dynamic Keyboard Interface in PyQt5** - Provides a moving highlight bar which spans across the rows of keyboard alternatively allowing the user to twitch to select a row and to select the key using the next twitch on circulating highlight.

## 📷 Project Images

<p align="center">
  <img src="assets/p1.jpeg" width="32%" style="margin: 5px;">
  <img src="assets/p2.jpeg" width="32%" style="margin: 5px;">
  <img src="assets/p3.jpeg" width="32%" style="margin: 5px;">
</p>

## 📥 Installation & Setup
1. Clone this repository:
   ```sh
   git clone https://github.com/your-username/Liberate.git
   cd Liberate
   ```
2. Install dependencies:
   ```sh
   pip install -r ./src/requirements.txt
   ```
3. Acquire hardware (comming soon), Upload arduino code to hardware & run main script
   ```sh
   python main.py
   ```

## 📜 License
This project is currently **proprietary**, but may be open-sourced in the future.

## 🤝 Support
Contributions are welcome! Feel free to submit issues or pull requests to improve the project.
⭐ support us by starring the repo ⭐

## 📬 Contact
For any queries or collaborations, reach out via **[aaromalonline@gmail.com]**.

---

> *"Breaking barriers, one motion at a time."*

