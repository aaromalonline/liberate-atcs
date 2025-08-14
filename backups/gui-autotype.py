from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QGridLayout, QPushButton, 
                             QHBoxLayout, QVBoxLayout, QTabWidget, QSpinBox, QFrame)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import pyautogui
import sys
import pyttsx3

# Define keyboard layout
keyboard = [
    ['SPEAK', 'SOS'],  # Added action buttons as a new row
    ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
    ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T'],
    ['U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4'],
    ['5', '6', '7', '8', '9', '0', '␣', '⌫', '⏎', '.']
]

class MuscleKeyboard(QWidget):
    def __init__(self):
        super().__init__()

        self.current_row = 0
        self.current_col = 0
        self.selecting_row = True  # True = selecting row, False = selecting column
        self.typed_message = ""  # Stores selected characters
        self.is_powered = False
        
        # Auto-typing setup
        self.target_text = "This is Liberate"
        self.current_char_index = 0
        self.auto_typing = True
        self.waiting_for_char = False
        self.text_completed = False  # Flag to indicate if text typing is complete
        self.speaking_mode = False   # Flag to indicate if we're trying to click SPEAK
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        
        self.initUI()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_selection)
        # Timer starts when powered on

    def initUI(self):
        self.setWindowTitle("Liberate - Adaptive Typing & Control System")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)

        # Scanning Keyboard Tab
        scanning_tab = QWidget()
        self.tab_widget.addTab(scanning_tab, "Scanning Keyboard")
        
        # Morse Code Tab (placeholder)
        morse_tab = QWidget()
        morse_layout = QVBoxLayout()
        morse_label = QLabel("Morse Code Interface - Coming Soon")
        morse_label.setAlignment(Qt.AlignCenter)
        morse_layout.addWidget(morse_label)
        morse_tab.setLayout(morse_layout)
        self.tab_widget.addTab(morse_tab, "Morse Code")

        main_layout.addWidget(self.tab_widget)

        # Setup scanning keyboard tab content
        scanning_layout = QVBoxLayout()
        scanning_tab.setLayout(scanning_layout)

        # Control panel
        control_panel = self.create_control_panel()
        scanning_layout.addWidget(control_panel)

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        scanning_layout.addWidget(line)

        # Display panel for typed message
        self.display_label = QLabel("Message: ", self)
        self.display_label.setStyleSheet("background-color: white; padding: 10px; border: 1px solid #ccc;")
        self.display_label.setFont(QFont("Arial", 12))
        scanning_layout.addWidget(self.display_label)

        # Keyboard layout
        keyboard_widget = QWidget()
        keyboard_layout = QGridLayout()
        keyboard_widget.setLayout(keyboard_layout)
        
        # Keyboard buttons
        self.buttons = []
        for row_idx, row in enumerate(keyboard):
            button_row = []
            for col_idx, key in enumerate(row):
                button = QPushButton(key)
                button.setMinimumSize(50, 50)
                button.setFont(QFont("Arial", 14, QFont.Bold))
                keyboard_layout.addWidget(button, row_idx, col_idx)
                button_row.append(button)
            self.buttons.append(button_row)

        scanning_layout.addWidget(keyboard_widget)
        self.update_highlight()

    def create_control_panel(self):
        """Create the control panel with all buttons and controls"""
        panel = QFrame()
        panel.setStyleSheet("background-color: #e8e8e8; padding: 10px;")
        panel.setMaximumHeight(80)
        
        layout = QHBoxLayout()
        panel.setLayout(layout)

        # Power indicator and toggle
        self.power_indicator = QLabel("●")
        self.power_indicator.setStyleSheet("color: red; font-size: 20px;")
        layout.addWidget(self.power_indicator)

        self.toggle_power_btn = QPushButton("Toggle Power")
        self.toggle_power_btn.clicked.connect(self.toggle_power)
        self.toggle_power_btn.setStyleSheet("padding: 5px 10px;")
        layout.addWidget(self.toggle_power_btn)

        # Separator
        layout.addWidget(self.create_separator())

        # Scan Speed controls
        speed_label = QLabel("Scan Speed (ms):")
        layout.addWidget(speed_label)

        self.speed_spinbox = QSpinBox()
        self.speed_spinbox.setRange(100, 3000)
        self.speed_spinbox.setValue(1000)
        self.speed_spinbox.valueChanged.connect(self.update_scan_speed)
        layout.addWidget(self.speed_spinbox)

        self.speed_up_btn = QPushButton("Speed Up")
        self.speed_up_btn.clicked.connect(self.speed_up)
        self.speed_up_btn.setStyleSheet("padding: 5px 10px;")
        layout.addWidget(self.speed_up_btn)

        self.slow_down_btn = QPushButton("Slow Down")
        self.slow_down_btn.clicked.connect(self.slow_down)
        self.slow_down_btn.setStyleSheet("padding: 5px 10px;")
        layout.addWidget(self.slow_down_btn)

        # Stretch to fill remaining space
        layout.addStretch()

        return panel

    def create_separator(self):
        """Create a vertical separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setMaximumWidth(2)
        return separator

    def toggle_power(self):
        """Toggle the power state of the system"""
        self.is_powered = not self.is_powered
        
        if self.is_powered:
            self.power_indicator.setStyleSheet("color: green; font-size: 20px;")
            self.timer.start(self.speed_spinbox.value())
        else:
            self.power_indicator.setStyleSheet("color: red; font-size: 20px;")
            self.timer.stop()

    def create_action_buttons(self):
        """Create the action buttons (Speak, SOS)"""
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)
        
        # Create action buttons with light blue background
        self.speak_btn = QPushButton("Speak")
        self.speak_btn.setStyleSheet("background-color: #ADD8E6; padding: 10px 20px; font-size: 12px; border: 1px solid #ccc;")
        self.speak_btn.setMinimumSize(80, 40)
        self.speak_btn.clicked.connect(self.speak_text)
        
        self.sos_btn = QPushButton("SOS")
        self.sos_btn.setStyleSheet("background-color: #ADD8E6; padding: 10px 20px; font-size: 12px; border: 1px solid #ccc;")
        self.sos_btn.setMinimumSize(80, 40)
        self.sos_btn.clicked.connect(self.send_sos)
        
        layout.addWidget(self.speak_btn)
        layout.addWidget(self.sos_btn)
        layout.addStretch()  # Push buttons to the left
        
        return widget

    def update_scan_speed(self):
        """Update the scanning speed"""
        if self.is_powered and self.timer.isActive():
            self.timer.start(self.speed_spinbox.value())

    def speed_up(self):
        """Decrease the scan time (speed up)"""
        current_value = self.speed_spinbox.value()
        new_value = max(100, current_value - 100)
        self.speed_spinbox.setValue(new_value)

    def slow_down(self):
        """Increase the scan time (slow down)"""
        current_value = self.speed_spinbox.value()
        new_value = min(3000, current_value + 100)
        self.speed_spinbox.setValue(new_value)

    def find_char_position(self, target_char):
        """Find the row and column of a character in the keyboard layout"""
        target_char = target_char.upper()
        
        # Handle special characters
        if target_char == ' ':
            target_char = '␣'
        elif target_char == "'":
            # Apostrophe not in layout, we'll skip it for demo
            return None, None
            
        for row_idx, row in enumerate(keyboard):
            for col_idx, key in enumerate(row):
                if key == target_char:
                    return row_idx, col_idx
        return None, None

    def move_selection(self):
        if not self.auto_typing or not self.is_powered:
            return
            
        if self.current_char_index >= len(self.target_text) and not self.text_completed:
            self.text_completed = True
            self.speaking_mode = True
            self.waiting_for_char = True
            self.selecting_row = True
            self.current_row = len(keyboard) - 1  # Start from bottom row
            self.current_col = 0
            return

        if self.speaking_mode:
            if self.selecting_row:
                if self.current_row == 0:  # First row has SPEAK button
                    self.selecting_row = False  # Move to column selection
                else:
                    self.current_row = (self.current_row + 1) % len(keyboard)
            else:
                if self.current_col == 0:  # SPEAK button position
                    self.confirm_selection()
                    self.timer.stop()
                else:
                    self.current_col = (self.current_col + 1) % len(keyboard[self.current_row])
            self.update_highlight()
            return

        if self.waiting_for_char:
            # We're in the process of selecting a character
            if self.selecting_row:
                target_char = self.target_text[self.current_char_index]
                target_row, target_col = self.find_char_position(target_char)
                
                if target_row is None:
                    # Skip characters not in our keyboard (like apostrophe)
                    self.current_char_index += 1
                    self.waiting_for_char = False
                    return
                
                if self.current_row == target_row:
                    # Found the target row, simulate twitch to select it
                    self.confirm_selection()
                else:
                    # Continue from current row position
                    self.current_row += 1
                    if self.current_row >= len(keyboard):  # If we reach bottom
                        self.current_row = 0  # Start from top again
            else:
                target_char = self.target_text[self.current_char_index]
                target_row, target_col = self.find_char_position(target_char)
                
                if self.current_col == target_col:
                    # Found the target column, simulate twitch to select it
                    self.confirm_selection()
                    self.waiting_for_char = False  # Character selected, move to next
                    self.current_char_index += 1
                else:
                    # Keep moving through columns
                    self.current_col = (self.current_col + 1) % len(keyboard[self.current_row])
        else:
            # Start selecting the next character
            self.waiting_for_char = True
            # Keep the current row position, don't reset to 0
            self.current_col = 0
            self.selecting_row = True
            
        self.update_highlight()

    def confirm_selection(self):
        if self.selecting_row:
            self.selecting_row = False  # Now select column
        else:
            selected_key = keyboard[self.current_row][self.current_col]
            self.type_key(selected_key)
            self.selecting_row = True  # Reset to row selection

    def type_key(self, key):
        if key == 'SPEAK':
            self.speak_text()
            return
        elif key == 'SOS':
            self.send_sos()
            return
        elif key == '␣':
            self.typed_message += ' '
        elif key == '⌫':
            self.typed_message = self.typed_message[:-1]  # Remove last char
        elif key == '⏎':
            self.typed_message += '\n'  # New line
        else:
            self.typed_message += key
            
        self.display_label.setText(f"Message: {self.typed_message}")

    def update_highlight(self):
        for row_idx, row in enumerate(self.buttons):
            for col_idx, button in enumerate(row):
                if self.selecting_row and row_idx == self.current_row:
                    button.setStyleSheet("background-color: yellow; font-size: 14px; font-weight: bold;")
                elif not self.selecting_row and row_idx == self.current_row and col_idx == self.current_col:
                    button.setStyleSheet("background-color: red; color: white; font-size: 14px; font-weight: bold;")
                else:
                    button.setStyleSheet("font-size: 14px; font-weight: bold;")

    def speak_text(self):
        """Speak the current message using text-to-speech"""
        if self.typed_message:
            print(f"Speaking: {self.typed_message}")
            self.engine.say(self.typed_message)
            self.engine.runAndWait()
            self.speaking_mode = False  # Reset speaking mode after speaking
    
    def send_sos(self):
        """Send SOS message"""
        # In a real implementation, this would send an emergency message
        self.typed_message = "SOS - EMERGENCY HELP NEEDED"
        self.display_label.setText(f"Message: {self.typed_message}")
        print("SOS message sent!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MuscleKeyboard()
    ex.show()
    sys.exit(app.exec_())