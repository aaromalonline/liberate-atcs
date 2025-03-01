import sys
import serial
import time
import pyautogui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QPainter

# Define keyboard layout
keyboard = [
    ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'Skip'],
    ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'Skip'],
    ['U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', 'Skip'],
    ['5', '6', '7', '8', '9', '0', '␣', '⌫', '⏎', '.', 'Skip']
]

# Define serial port (Update this based on your system)
SERIAL_PORT = "/dev/ttyUSB0"
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

# Main GUI Class
class MuscleKeyboard(QWidget):
    def __init__(self):
        super().__init__()

        self.current_row = 0
        self.current_col = 0
        self.selecting_row = True
        self.typed_message = ""

        self.initUI()
        
        self.serial_thread = SerialThread()
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

        self.buttons = []
        for row_idx, row in enumerate(keyboard):
            button_row = []
            for col_idx, key in enumerate(row):
                button = QPushButton(key)
                self.layout.addWidget(button, row_idx + 1, col_idx)
                button_row.append(button)
            self.buttons.append(button_row)

        self.reset_button = QPushButton("Reset Baseline")
        self.reset_button.clicked.connect(self.reset_baseline)
        main_layout.addWidget(self.reset_button)

        self.update_highlight()

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

    def update_highlight(self):
        for row_idx, row in enumerate(self.buttons):
            for col_idx, button in enumerate(row):
                if self.selecting_row and row_idx == self.current_row:
                    button.setStyleSheet("background-color: yellow;")
                elif not self.selecting_row and row_idx == self.current_row and col_idx == self.current_col:
                    button.setStyleSheet("background-color: red;")
                else:
                    button.setStyleSheet("")

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
