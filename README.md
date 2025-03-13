# ![](./assets/liberatelogo.jpeg)

# **Liberate**  
### *Freedom Beyond Barriers*  

[![Repository Status](https://img.shields.io/badge/Repository%20Status-Prototype-dark%20green.svg)](https://github.com/aaromalonline/liberate)
[![Author](https://img.shields.io/badge/Author-Aaromal%20A-purple.svg)](https://www.linkedin.com/in/aaromalonline/)
[![Latest Release](https://img.shields.io/badge/Latest%20Release-11%20Feb%202025-yellow.svg)](https://github.com/aaromalonline/liberate)
<a href="https://github.com/aaromalonline/liberate/blob/master/LICENSE"><img alt="License" src="http://img.shields.io/:license-mit-blue.svg?style=flat-square?style=flat-square" /></a>

**Liberate** is a muscle movement detection system that converts subtle muscle activity into control signals. By detecting slight facial or body muscle movements, the system enables users to control devices like a **computer cursor, wheelchair, or keyboard**. This innovation offers an intuitive, hands-free interface, enhancing accessibility and communication for individuals with limited mobility.

<div style="position: relative; width: 100%; height: 0; padding-top: 56.2500%;
 padding-bottom: 0; box-shadow: 0 2px 8px 0 rgba(63,69,81,0.16); margin-top: 1.6em; margin-bottom: 0.9em; overflow: hidden;
 border-radius: 8px; will-change: transform;">
  <iframe loading="lazy" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none; padding: 0;margin: 0;"
    src="https://www.canva.com/design/DAGgiwwJF50/0pNmzq6Z0drq8x91x3Nejg/view?embed" allowfullscreen="allowfullscreen" allow="fullscreen">
  </iframe>
</div>
<a href="https:&#x2F;&#x2F;www.canva.com&#x2F;design&#x2F;DAGgiwwJF50&#x2F;0pNmzq6Z0drq8x91x3Nejg&#x2F;view?utm_content=DAGgiwwJF50&amp;utm_campaign=designshare&amp;utm_medium=embeds&amp;utm_source=link" target="_blank" rel="noopener">Presentation</a> 

𝒎𝒂𝒅𝒆 𝒘𝒊𝒕𝒉 ❤️ 𝑻𝒆𝒂𝒎 𝑳𝒖𝒎𝒆𝒏 : [Aaromal A](https://www.linkedin.com/in/aaromalonline/), [Deeraj P Menon](https://www.linkedin.com/in/deeraj-p-menon-aa4b5231b/)

## 🛠️ Technologies Used
- **Python** for signal processing & control logic
- **ESP32** for sensor data acquisition via I2C and encoding of muscle twitches to control signals
- **ADXL345 Digital Accelerometer/Tap Sensor** for muscle movement detection (also IR reflexive sensor)

## 🚀 Features
- **Muscle twitch detector/encoder** using ADXL345 digital accelerometer & ESP32 to convert muscle twitches to control signals/clicks
- **Muscle controlled keyboard** with QWERTY & Morse mode available as a PyQt5 python desktop
- **Built-in SOS & speech synthesis** using a specch engine like gTTS
- **A minimal, cost-effective design** for real-world usability

## 💻 How it works? 
- **Sensor + Encoder** - When ON, The ADXL345 accelerometer records muscle twitches as 3-axis accelerations, which are encoded into clicks (0/1) using baseline calibration and filtering algorithms.
- **Data Transmission** - Data is sent serially/wirelessly via ESP32 to the python application using I2C, where the user can control a keyboard interface using the decoded twitch clicks.
- **Dynamic Keyboard Interface in PyQt5** - Provides a moving highlight bar which spans across the rows of keyboard alternatively allowing the user to twitch to select a row and to select the key using the next twitch on circulating highlight.

## 📷 Project Image
<img src="assets/p1.jpeg" width="45%"> <img src="assets/p2.jpeg" width="45%">

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

