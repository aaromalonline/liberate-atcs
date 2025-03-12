import sys
import time
import pyautogui
import pyttsx3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QPainter, QFont

# Define keyboard layout with Speak, SOS, and Skip button
keyboard = [
    ['Speak', 'SOS', 'Skip'],
    ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'Skip'],
    ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'Skip'],
    ['U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', 'Skip'],
    ['5', '6', '7', '8', '9', '0', '␣', '⌫', '⏎', '.', 'Skip']
]

# Morse code dictionary
MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 
    'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', 
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', 
    '0': '-----', ' ': '/', '.': '.-.-.-', ',': '--..--', '?': '..--..'
}

# Reverse the dictionary to look up characters by their morse code
REVERSE_MORSE = {v: k for k, v in MORSE_CODE.items()}

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
        self.power_on = False
        
        # Morse code variables
        self.morse_input = ""
        self.last_signal_time = 0
        self.dot_time = 200  # ms
        self.dash_time = 600  # ms
        self.letter_gap_time = 1000  # ms
        self.word_gap_time = 2000  # ms
        
        self.initUI()
        
        # Start scanning timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_selection)
        self.timer.start(1000)  # 1 second interval
        
        # Timer for morse code timeouts
        self.morse_timer = QTimer(self)
        self.morse_timer.timeout.connect(self.check_morse_timeouts)
        self.morse_timer.start(100)  # Check every 100ms

    def initUI(self):
        self.setWindowTitle("Liberate - Muscle-Controlled Keyboard (Test Mode)")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create tabs
        self.tabs = QTabWidget()
        self.keyboard_tab = QWidget()
        self.morse_tab = QWidget()
        
        self.tabs.addTab(self.keyboard_tab, "Scanning Keyboard")
        self.tabs.addTab(self.morse_tab, "Morse Code")
        
        main_layout.addWidget(self.tabs)
        
        # Setup keyboard tab
        self.setup_keyboard_tab()
        
        # Setup morse code tab
        self.setup_morse_tab()

    def setup_keyboard_tab(self):
        layout = QVBoxLayout()
        self.keyboard_tab.setLayout(layout)

        # Top section with power indicator and test controls
        top_layout = QHBoxLayout()
        
        # Power indicator
        self.power_indicator = PowerIndicator()
        top_layout.addWidget(self.power_indicator)
        
        # Test control buttons
        self.toggle_power_button = QPushButton("Toggle Power")
        self.toggle_power_button.clicked.connect(self.toggle_power)
        top_layout.addWidget(self.toggle_power_button)
        
        self.select_button = QPushButton("Simulate Selection")
        self.select_button.clicked.connect(self.confirm_selection)
        top_layout.addWidget(self.select_button)
        
        self.speed_label = QLabel("Scan Speed (ms): 1000")
        top_layout.addWidget(self.speed_label)
        
        self.speed_up_button = QPushButton("Speed Up")
        self.speed_up_button.clicked.connect(self.speed_up)
        top_layout.addWidget(self.speed_up_button)
        
        self.slow_down_button = QPushButton("Slow Down")
        self.slow_down_button.clicked.connect(self.slow_down)
        top_layout.addWidget(self.slow_down_button)
        
        layout.addLayout(top_layout)

        # Display area
        self.display_label = QLabel("Message: ", self)
        self.display_label.setStyleSheet("font-size: 14pt; margin: 10px;")
        layout.addWidget(self.display_label)

        # Keyboard grid
        self.keyboard_layout = QGridLayout()
        layout.addLayout(self.keyboard_layout)

        for row_idx, row in enumerate(keyboard):
            button_row = []
            for col_idx, key in enumerate(row):
                button = QPushButton(key)
                button.setMinimumHeight(50)
                if key in ["Speak", "SOS"]:
                    button.setStyleSheet("background-color: lightblue;")
                self.keyboard_layout.addWidget(button, row_idx, col_idx)
                button_row.append(button)
            self.buttons.append(button_row)

        # Status bar
        self.status_label = QLabel("Test Mode: Hardware disconnected")
        self.status_label.setStyleSheet("color: blue;")
        layout.addWidget(self.status_label)

        self.update_highlight()
        
        # Set initial power status
        self.toggle_power()

    def setup_morse_tab(self):
        layout = QVBoxLayout()
        self.morse_tab.setLayout(layout)
        
        # Display areas
        self.morse_display = QLabel("Current Morse Input: ")
        self.morse_display.setStyleSheet("font-size: 14pt; margin: 10px;")
        layout.addWidget(self.morse_display)
        
        self.morse_message = QLabel("Message: ")
        self.morse_message.setStyleSheet("font-size: 14pt; margin: 10px;")
        layout.addWidget(self.morse_message)
        
        # Morse input buttons
        morse_buttons = QHBoxLayout()
        
        self.dot_button = QPushButton("·")
        self.dot_button.setFont(QFont("Arial", 24))
        self.dot_button.setMinimumHeight(80)
        self.dot_button.setMinimumWidth(120)
        self.dot_button.clicked.connect(self.add_dot)
        morse_buttons.addWidget(self.dot_button)
        
        self.dash_button = QPushButton("−")
        self.dash_button.setFont(QFont("Arial", 24))
        self.dash_button.setMinimumHeight(80)
        self.dash_button.setMinimumWidth(120)
        self.dash_button.clicked.connect(self.add_dash)
        morse_buttons.addWidget(self.dash_button)
        
        layout.addLayout(morse_buttons)
        
        # Timing controls
        timing_layout = QGridLayout()
        
        timing_layout.addWidget(QLabel("Dot Time (ms):"), 0, 0)
        self.dot_time_label = QLabel(str(self.dot_time))
        timing_layout.addWidget(self.dot_time_label, 0, 1)
        dot_up = QPushButton("+")
        dot_up.clicked.connect(lambda: self.adjust_timing('dot', 50))
        timing_layout.addWidget(dot_up, 0, 2)
        dot_down = QPushButton("-")
        dot_down.clicked.connect(lambda: self.adjust_timing('dot', -50))
        timing_layout.addWidget(dot_down, 0, 3)
        
        timing_layout.addWidget(QLabel("Dash Time (ms):"), 1, 0)
        self.dash_time_label = QLabel(str(self.dash_time))
        timing_layout.addWidget(self.dash_time_label, 1, 1)
        dash_up = QPushButton("+")
        dash_up.clicked.connect(lambda: self.adjust_timing('dash', 50))
        timing_layout.addWidget(dash_up, 1, 2)
        dash_down = QPushButton("-")
        dash_down.clicked.connect(lambda: self.adjust_timing('dash', -50))
        timing_layout.addWidget(dash_down, 1, 3)
        
        timing_layout.addWidget(QLabel("Letter Gap Time (ms):"), 2, 0)
        self.letter_gap_label = QLabel(str(self.letter_gap_time))
        timing_layout.addWidget(self.letter_gap_label, 2, 1)
        letter_up = QPushButton("+")
        letter_up.clicked.connect(lambda: self.adjust_timing('letter', 100))
        timing_layout.addWidget(letter_up, 2, 2)
        letter_down = QPushButton("-")
        letter_down.clicked.connect(lambda: self.adjust_timing('letter', -100))
        timing_layout.addWidget(letter_down, 2, 3)
        
        timing_layout.addWidget(QLabel("Word Gap Time (ms):"), 3, 0)
        self.word_gap_label = QLabel(str(self.word_gap_time))
        timing_layout.addWidget(self.word_gap_label, 3, 1)
        word_up = QPushButton("+")
        word_up.clicked.connect(lambda: self.adjust_timing('word', 200))
        timing_layout.addWidget(word_up, 3, 2)
        word_down = QPushButton("-")
        word_down.clicked.connect(lambda: self.adjust_timing('word', -200))
        timing_layout.addWidget(word_down, 3, 3)
        
        layout.addLayout(timing_layout)
        
        # Morse code reference chart
        layout.addWidget(QLabel("Morse Code Reference:"))
        
        reference_text = QTextEdit()
        reference_text.setReadOnly(True)
        
        reference_content = ""
        for i, (char, code) in enumerate(MORSE_CODE.items()):
            reference_content += f"{char}: {code}    "
            if (i + 1) % 5 == 0:
                reference_content += "\n"
        
        reference_text.setText(reference_content)
        layout.addWidget(reference_text)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.clear_morse_button = QPushButton("Clear Current Input")
        self.clear_morse_button.clicked.connect(self.clear_morse_input)
        control_layout.addWidget(self.clear_morse_button)
        
        self.space_button = QPushButton("Add Space")
        self.space_button.clicked.connect(self.add_space)
        control_layout.addWidget(self.space_button)
        
        self.backspace_button = QPushButton("Backspace")
        self.backspace_button.clicked.connect(self.morse_backspace)
        control_layout.addWidget(self.backspace_button)
        
        self.speak_morse_button = QPushButton("Speak Message")
        self.speak_morse_button.clicked.connect(self.speak_morse_message)
        control_layout.addWidget(self.speak_morse_button)
        
        layout.addLayout(control_layout)

    def update_highlight(self):
        for row_idx, row in enumerate(self.buttons):
            for col_idx, button in enumerate(row):
                key = keyboard[row_idx][col_idx]
                if self.selecting_row and row_idx == self.current_row:
                    button.setStyleSheet("background-color: yellow;")
                elif not self.selecting_row and row_idx == self.current_row and col_idx == self.current_col:
                    button.setStyleSheet("background-color: orange;")
                elif key in ["Speak", "SOS"]:
                    button.setStyleSheet("background-color: lightblue;")
                else:
                    button.setStyleSheet("")

    def move_selection(self):
        if not self.power_on:
            return
            
        if self.selecting_row:
            self.current_row = (self.current_row + 1) % len(keyboard)
        else:
            self.current_col = (self.current_col + 1) % len(keyboard[self.current_row])
        self.update_highlight()

    def confirm_selection(self):
        if not self.power_on:
            return
            
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
            # Comment out pyautogui for testing if needed
            pyautogui.press('space')
        elif key == '⌫':
            if self.typed_message:
                self.typed_message = self.typed_message[:-1]
                pyautogui.press('backspace')
        elif key == '⏎':
            self.typed_message += '\n'
            pyautogui.press('enter')
        else:
            self.typed_message += key
            pyautogui.write(key)
        self.display_label.setText(f"Message: {self.typed_message}")
        self.morse_message.setText(f"Message: {self.typed_message}")

    def speak_message(self):
        if self.typed_message:
            self.status_label.setText("Speaking message...")
            self.speech_engine.say(self.typed_message)
            self.speech_engine.runAndWait()
            self.status_label.setText("Test Mode: Hardware disconnected")

    def speak_morse_message(self):
        if self.typed_message:
            self.speech_engine.say(self.typed_message)
            self.speech_engine.runAndWait()

    def sos_alert(self):
        self.status_label.setText("SOS Alert Triggered!")
        pyautogui.alert("SOS Alert Triggered!")
        self.status_label.setText("Test Mode: Hardware disconnected")

    def toggle_power(self):
        self.power_on = not self.power_on
        self.power_indicator.set_power_status(self.power_on)
        status = "ON" if self.power_on else "OFF"
        self.status_label.setText(f"Test Mode: Power {status}")

    def speed_up(self):
        current_speed = self.timer.interval()
        if current_speed > 200:
            new_speed = current_speed - 200
            self.timer.setInterval(new_speed)
            self.speed_label.setText(f"Scan Speed (ms): {new_speed}")

    def slow_down(self):
        current_speed = self.timer.interval()
        new_speed = current_speed + 200
        self.timer.setInterval(new_speed)
        self.speed_label.setText(f"Scan Speed (ms): {new_speed}")
    
    # Morse code methods
    def add_dot(self):
        self.morse_input += "."
        self.last_signal_time = time.time() * 1000  # Convert to ms
        self.morse_display.setText(f"Current Morse Input: {self.morse_input}")

    def add_dash(self):
        self.morse_input += "-"
        self.last_signal_time = time.time() * 1000  # Convert to ms
        self.morse_display.setText(f"Current Morse Input: {self.morse_input}")

    def check_morse_timeouts(self):
        if not self.morse_input:
            return
            
        current_time = time.time() * 1000  # Convert to ms
        time_since_last_signal = current_time - self.last_signal_time
        
        # Check for letter gap
        if time_since_last_signal > self.letter_gap_time:
            # Try to translate the current morse code
            if self.morse_input in REVERSE_MORSE:
                char = REVERSE_MORSE[self.morse_input]
                self.typed_message += char
                # Update both displays
                self.display_label.setText(f"Message: {self.typed_message}")
                self.morse_message.setText(f"Message: {self.typed_message}")
                # Type to active application
                pyautogui.write(char)
            
            # Clear the morse input
            self.morse_input = ""
            self.morse_display.setText(f"Current Morse Input: {self.morse_input}")
            
            # Check for word gap
            if time_since_last_signal > self.word_gap_time:
                self.typed_message += " "
                self.display_label.setText(f"Message: {self.typed_message}")
                self.morse_message.setText(f"Message: {self.typed_message}")
                pyautogui.press('space')

    def clear_morse_input(self):
        self.morse_input = ""
        self.morse_display.setText(f"Current Morse Input: {self.morse_input}")

    def add_space(self):
        self.typed_message += " "
        self.display_label.setText(f"Message: {self.typed_message}")
        self.morse_message.setText(f"Message: {self.typed_message}")
        pyautogui.press('space')
        self.clear_morse_input()

    def morse_backspace(self):
        if self.morse_input:
            # First clear current morse input
            self.clear_morse_input()
        elif self.typed_message:
            # Then backspace from the message
            self.typed_message = self.typed_message[:-1]
            self.display_label.setText(f"Message: {self.typed_message}")
            self.morse_message.setText(f"Message: {self.typed_message}")
            pyautogui.press('backspace')

    def adjust_timing(self, param, change):
        if param == 'dot':
            self.dot_time = max(50, self.dot_time + change)
            self.dot_time_label.setText(str(self.dot_time))
        elif param == 'dash':
            self.dash_time = max(150, self.dash_time + change)
            self.dash_time_label.setText(str(self.dash_time))
        elif param == 'letter':
            self.letter_gap_time = max(300, self.letter_gap_time + change)
            self.letter_gap_label.setText(str(self.letter_gap_time))
        elif param == 'word':
            self.word_gap_time = max(500, self.word_gap_time + change)
            self.word_gap_label.setText(str(self.word_gap_time))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MuscleKeyboard()
    ex.show()
    sys.exit(app.exec_())