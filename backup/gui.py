from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QPushButton
from PyQt5.QtCore import QTimer
import pyautogui
import sys

# Define keyboard layout
keyboard = [
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
        
        self.initUI()
        
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

        # Twitch button (simulated selection)
        self.twitch_button = QPushButton("Simulate Twitch")
        self.twitch_button.clicked.connect(self.confirm_selection)
        self.layout.addWidget(self.twitch_button, len(keyboard) + 1, 0, 1, 10)

        self.update_highlight()

    def move_selection(self):
        if self.selecting_row:
            self.current_row = (self.current_row + 1) % len(keyboard)
        else:
            self.current_col = (self.current_col + 1) % len(keyboard[self.current_row])
        self.update_highlight()

    def confirm_selection(self):
        if self.selecting_row:
            self.selecting_row = False  # Now select column
        else:
            selected_key = keyboard[self.current_row][self.current_col]
            self.type_key(selected_key)
            self.selecting_row = True  # Reset to row selection
        self.update_highlight()

    def type_key(self, key):
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
        for row_idx, row in enumerate(self.buttons):
            for col_idx, button in enumerate(row):
                if self.selecting_row and row_idx == self.current_row:
                    button.setStyleSheet("background-color: yellow;")
                elif not self.selecting_row and row_idx == self.current_row and col_idx == self.current_col:
                    button.setStyleSheet("background-color: red;")
                else:
                    button.setStyleSheet("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MuscleKeyboard()
    ex.show()
    sys.exit(app.exec_())
