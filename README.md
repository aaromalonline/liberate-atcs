# ![](./assets/liberatelogo.jpeg)

# **Liberate**  
### *Freedom Beyond Barriers*  

**Liberate** is a muscle movement detection system that converts subtle muscle activity into control signals. By detecting slight facial or body muscle movements, the system enables users to control devices like a **computer cursor, wheelchair, or keyboard**. This innovation offers an intuitive, hands-free interface, enhancing accessibility and communication for individuals with limited mobility.

**UPDATE STAGE** - Prototype

[Presentation](https://bit.ly/3XrDsM3)

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

