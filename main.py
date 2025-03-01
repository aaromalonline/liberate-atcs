import sys
import serial
import time
import pyautogui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QPushButton
from PyQt5.QtCore import QTimer, QThread, pyqtSignal

# Define keyboard layout
keyboard = [
    ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
    ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T'],
    ['U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4'],
    ['5', '6', '7', '8', '9', '0', '␣', '⌫', '⏎', '.']
]

# Define serial port (Update this based on your system)
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200


# Background Thread for Twitch Detection
class TwitchDetector(QThread):
    twitchDetected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True
        self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow Arduino to initialize

    def run(self):
        print("🎯 Listening for twitches from Arduino...")
        while self.running:
            line = self.ser.readline().decode().strip()
            if line == "1":  # Twitch detected
                self.twitchDetected.emit()
            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

    def reset_baseline(self):
        """Send RESET command to Arduino for recalibration"""
        self.ser.write(b"RESET\n")
        print("🔄 Resetting baseline values...")


# Main GUI Class
class MuscleKeyboard(QWidget):
    def __init__(self):
        super().__init__()

        self.current_row = 0
        self.current_col = 0
        self.selecting_row = True  # True = selecting row, False = selecting column
        self.typed_message = ""  # Stores selected characters
        
        self.initUI()

        # Start Twitch Detection Thread
        self.twitch_detector = TwitchDetector()
        self.twitch_detector.twitchDetected.connect(self.confirm_selection)
        self.twitch_detector.start()

        # Auto-selection timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_selection)
        self.timer.start(1000)  # Move every 1 sec

    def initUI(self):
        self.setWindowTitle("Liberate - Muscle-Controlled Keyboard")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Display panel for typed message
        self.display_label = QLabel("Message: ", self)
        self.layout.addWidget(self.display_label, 0, 0, 1, 10)  # Spanning 10 columns

        # Keyboard buttons
        self.buttons = []
        for row_idx, row in enumerate(keyboard):
            button_row = []
            for col_idx, key in enumerate(row):
                button = QPushButton(key)
                self.layout.addWidget(button, row_idx + 1, col_idx)
                button_row.append(button)
            self.buttons.append(button_row)

        # Reset Baseline Button
        self.reset_button = QPushButton("Reset Baseline")
        self.reset_button.clicked.connect(self.reset_baseline)
        self.layout.addWidget(self.reset_button, len(keyboard) + 1, 0, 1, 10)

        self.update_highlight()

    def move_selection(self):
        """Auto-move selection"""
        if self.selecting_row:
            self.current_row = (self.current_row + 1) % len(keyboard)  # Cycle through rows
        else:
            self.current_col = (self.current_col + 1) % len(keyboard[self.current_row])  # Cycle through columns
        self.update_highlight()

    def confirm_selection(self):
        """Triggered when a muscle twitch is detected"""
        if self.selecting_row:
            self.selecting_row = False  # Switch to column selection
            self.current_col = 0  # Reset column selection
        else:
            selected_key = keyboard[self.current_row][self.current_col]
            self.type_key(selected_key)
            self.selecting_row = True  # Reset to row selection
        self.update_highlight()

    def type_key(self, key):
        """Types the selected key"""
        if key == '␣':
            self.typed_message += ' '
            pyautogui.press('space')
        elif key == '⌫':
            self.typed_message = self.typed_message[:-1]  # Remove last char
            pyautogui.press('backspace')
        elif key == '⏎':
            self.typed_message += '\n'  # New line
            pyautogui.press('enter')
        else:
            self.typed_message += key
            pyautogui.write(key)
        self.display_label.setText(f"Message: {self.typed_message}")

    def update_highlight(self):
        """Updates keyboard highlight based on selection mode"""
        for row_idx, row in enumerate(self.buttons):
            for col_idx, button in enumerate(row):
                if self.selecting_row and row_idx == self.current_row:
                    button.setStyleSheet("background-color: yellow;")
                elif not self.selecting_row and row_idx == self.current_row and col_idx == self.current_col:
                    button.setStyleSheet("background-color: red;")
                else:
                    button.setStyleSheet("")

    def reset_baseline(self):
        """Triggers baseline reset in Arduino"""
        self.twitch_detector.reset_baseline()
        self.display_label.setText("Baseline Reset Requested...")

    def closeEvent(self, event):
        """Ensure the sensor thread is stopped when the GUI is closed"""
        self.twitch_detector.stop()
        event.accept()


# Run GUI Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MuscleKeyboard()
    ex.show()
    sys.exit(app.exec_())
