import sys
import serial
import time
import pyautogui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal

# Define keyboard layout
keyboard = [
    ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
    ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T'],
    ['U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4'],
    ['5', '6', '7', '8', '9', '0', '␣', '⌫', '⏎', '.']
]

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200

# Twitch Detection Thread
class TwitchDetector(QThread):
    twitchDetected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True
        self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)

    def run(self):
        while self.running:
            line = self.ser.readline().decode().strip()
            if line == "1":
                self.twitchDetected.emit()
            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

    def reset_baseline(self):
        self.ser.write(b"RESET\n")

# Main GUI
class MuscleKeyboard(QWidget):
    def __init__(self):
        super().__init__()
        self.current_row = 0
        self.current_col = 0
        self.selecting_row = True
        self.typed_message = ""
        self.initUI()

        # Start Twitch Detection Thread
        self.twitch_detector = TwitchDetector()
        self.twitch_detector.twitchDetected.connect(self.move_selection)
        self.twitch_detector.start()

    def initUI(self):
        self.setWindowTitle("Liberate - Muscle-Controlled Keyboard")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.display_label = QLabel("Message: ", self)
        self.layout.addWidget(self.display_label, 0, 0, 1, 10)

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
        self.layout.addWidget(self.reset_button, len(keyboard) + 1, 0, 1, 10)

        self.update_highlight()

    def move_selection(self):
        """Triggered by muscle twitch, moves selection."""
        if self.selecting_row:
            self.current_row = (self.current_row + 1) % len(keyboard)
        else:
            self.current_col = (self.current_col + 1) % len(keyboard[self.current_row])
        self.update_highlight()
        
    def confirm_selection(self):
        """Triggered when selection is confirmed."""
        if self.selecting_row:
            self.selecting_row = False
        else:
            self.type_key(keyboard[self.current_row][self.current_col])
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
        self.twitch_detector.reset_baseline()
        self.display_label.setText("Baseline Reset Requested...")

    def closeEvent(self, event):
        self.twitch_detector.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MuscleKeyboard()
    ex.show()
    sys.exit(app.exec_())
