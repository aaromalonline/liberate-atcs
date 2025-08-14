#testing bluetooth/serial communication toggle mode

import sys
import serial
import time
import pyautogui
import pyttsx3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QPainter

# Define keyboard layout with Speak, SOS, and Skip button
keyboard = [
    ['Speak', 'SOS', 'Skip'],
    ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'Skip'],
    ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'Skip'],
    ['U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', 'Skip'],
    ['5', '6', '7', '8', '9', '0', '␣', '⌫', '⏎', '.', 'Skip']
]

# Define serial port (Update this based on your system)
SERIAL_PORT = "COM5" 
BAUD_RATE = 115200

# Power Indicator Widget
class PowerIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.power_on = False
        self.setFixedSize(20, 20)

    def set_power_status(self, status):
        self.power_on = status
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        color = QColor(255, 0, 0) if self.power_on else QColor(100, 0, 0)
        painter.setBrush(color)
        painter.drawEllipse(0, 0, 20, 20)

# Serial Reader Thread
class SerialThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        self.running = True

    def run(self):
        while self.running:
            if self.ser.in_waiting:
                line = self.ser.readline().decode().strip()
                self.data_received.emit(line)

    def stop(self):
        self.running = False
        self.ser.close()

# --- Communication Thread Factories ---
def create_serial_thread():
    return SerialThread()

def create_bluetooth_thread():
    # Placeholder for Bluetooth thread implementation
    # Example: return BluetoothThread()
    raise NotImplementedError("Bluetooth communication not implemented yet.")

# Main GUI Class
class MuscleKeyboard(QWidget):
    def __init__(self):
        super().__init__()
        self.current_row = 0
        self.current_col = 0
        self.selecting_row = True
        self.typed_message = ""
        self.speech_engine = pyttsx3.init()
        self.buttons = []

        self.initUI()
        
        # --- Choose communication method here ---
        self.serial_thread = create_serial_thread()  # Use serial by default
        # To use Bluetooth in the future, replace with:
        # self.serial_thread = create_bluetooth_thread()
        self.serial_thread.data_received.connect(self.handle_serial_data)
        self.serial_thread.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_selection)
        self.timer.start(1000)

    def initUI(self):
        self.setWindowTitle("Liberate - Muscle-Controlled Keyboard")
        self.setGeometry(100, 100, 600, 400)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.power_indicator = PowerIndicator()
        main_layout.addWidget(self.power_indicator)

        self.display_label = QLabel("Message: ", self)
        main_layout.addWidget(self.display_label)

        self.layout = QGridLayout()
        main_layout.addLayout(self.layout)

        for row_idx, row in enumerate(keyboard):
            button_row = []
            for col_idx, key in enumerate(row):
                button = QPushButton(key)
                if key in ["Speak", "SOS"]:
                    button.setStyleSheet("background-color: lightblue;")
                self.layout.addWidget(button, row_idx, col_idx)
                button_row.append(button)
            self.buttons.append(button_row)

        self.reset_button = QPushButton("Reset Baseline")
        self.reset_button.clicked.connect(self.reset_baseline)
        main_layout.addWidget(self.reset_button)

        self.update_highlight()

    def update_highlight(self):
        for row_idx, row in enumerate(self.buttons):
            for col_idx, button in enumerate(row):
                if self.selecting_row and row_idx == self.current_row:
                    button.setStyleSheet("background-color: yellow;")
                elif not self.selecting_row and row_idx == self.current_row and col_idx == self.current_col:
                    button.setStyleSheet("background-color: orange;")
                else:
                    button.setStyleSheet("")

    def move_selection(self):
        if self.selecting_row:
            self.current_row = (self.current_row + 1) % len(keyboard)
        else:
            self.current_col = (self.current_col + 1) % len(keyboard[self.current_row])
        self.update_highlight()

    def confirm_selection(self):
        if self.selecting_row:
            self.selecting_row = False
            self.current_col = 0
        else:
            selected_key = keyboard[self.current_row][self.current_col]
            if selected_key == 'Skip':
                self.selecting_row = True
            elif selected_key == 'Speak':
                self.speak_message()
                self.selecting_row = True
            elif selected_key == 'SOS':
                self.sos_alert()
                self.selecting_row = True
            else:
                self.type_key(selected_key)
                self.selecting_row = True
        self.update_highlight()

    def type_key(self, key):
        if key == '␣':
            self.typed_message += ' '
            pyautogui.press('space')
        elif key == '⌫':
            self.typed_message = self.typed_message[:-1]
            pyautogui.press('backspace')
        elif key == '⏎':
            self.typed_message += '\n'
            pyautogui.press('enter')
        else:
            self.typed_message += key
            pyautogui.write(key)
        self.display_label.setText(f"Message: {self.typed_message}")

    def speak_message(self):
        if self.typed_message:
            self.speech_engine.say(self.typed_message)
            self.speech_engine.runAndWait()

    def sos_alert(self):
        pyautogui.alert("SOS Alert Triggered!")

    def reset_baseline(self):
        self.serial_thread.ser.write(b"RESET\n")
        self.display_label.setText("Baseline Reset Requested...")

    def handle_serial_data(self, line):
        if line == "1":
            self.confirm_selection()
        elif line == "ON":
            self.power_indicator.set_power_status(True)
        elif line == "OFF":
            self.power_indicator.set_power_status(False)

    def closeEvent(self, event):
        self.serial_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MuscleKeyboard()
    ex.show()
    sys.exit(app.exec_())
