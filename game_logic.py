import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QFrame
)
from PyQt5.QtGui import QFont, QPainter, QPen
from PyQt5.QtCore import Qt

class HangmanDrawing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wrong_guesses = 0
        self.setMinimumSize(300, 400)

    def set_wrong_guesses(self, count):
        self.wrong_guesses = count
        self.update()  # trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.black, 3)
        painter.setPen(pen)

        # Draw the gallows base
        painter.drawLine(50, 350, 250, 350)   # base
        painter.drawLine(100, 350, 100, 50)   # pole
        painter.drawLine(100, 50, 200, 50)    # top bar
        painter.drawLine(200, 50, 200, 100)   # rope

        # Draw hangman parts based on wrong_guesses count

        if self.wrong_guesses > 0:
            # Head (circle)
            painter.drawEllipse(175, 100, 50, 50)

        if self.wrong_guesses > 1:
            # Body
            painter.drawLine(200, 150, 200, 250)

        if self.wrong_guesses > 2:
            # Left arm
            painter.drawLine(200, 180, 150, 220)

        if self.wrong_guesses > 3:
            # Right arm
            painter.drawLine(200, 180, 250, 220)

        if self.wrong_guesses > 4:
            # Left leg
            painter.drawLine(200, 250, 160, 300)

        if self.wrong_guesses > 5:
            # Right leg
            painter.drawLine(200, 250, 240, 300)


class HangmanGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman Game")
        self.setGeometry(100, 100, 800, 500)

        self.word_bank = {
            "Fruits": ["apple", "banana", "orange", "grape"],
            "Animals": ["tiger", "elephant", "giraffe", "kangaroo"]
        }

        self.setup_ui()
        self.new_game()

    def setup_ui(self):
        main_layout = QHBoxLayout()

        # Left section (Word display, input, messages)
        left_layout = QVBoxLayout()

        self.category_label = QLabel("Category: ")
        self.category_label.setFont(QFont("Arial", 14))
        left_layout.addWidget(self.category_label)

        self.word_display = QLabel("")
        self.word_display.setFont(QFont("Courier", 24))
        left_layout.addWidget(self.word_display)

        self.input_label = QLabel("Enter a letter:")
        left_layout.addWidget(self.input_label)

        self.input_box = QLineEdit()
        self.input_box.setMaxLength(1)
        left_layout.addWidget(self.input_box)
        self.input_box.returnPressed.connect(self.handle_guess)  # Guess on Enter key

        self.submit_button = QPushButton("Guess")
        left_layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.handle_guess)

        self.new_game_button = QPushButton("New Game")
        left_layout.addWidget(self.new_game_button)
        self.new_game_button.clicked.connect(self.new_game)

        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)
        left_layout.addWidget(self.message_box)

        self.guessed_letters_label = QLabel("Guessed Letters: ")
        self.guessed_letters_label.setFont(QFont("Arial", 12))
        left_layout.addWidget(self.guessed_letters_label)

        # Right section (Hangman drawing area)
        self.hangman_area = HangmanDrawing()
        self.hangman_area.setMinimumWidth(300)

        main_layout.addLayout(left_layout, 2)
        main_layout.addWidget(self.hangman_area, 1)

        self.setLayout(main_layout)

    def new_game(self):
        self.category, words = random.choice(list(self.word_bank.items()))
        self.word = random.choice(words)
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.max_wrong = 6

        self.category_label.setText(f"Category: {self.category}")
        self.update_word_display()
        self.message_box.clear()
        self.submit_button.setEnabled(True)
        self.input_box.setEnabled(True)
        self.guessed_letters_label.setText("Guessed Letters: ")
        self.hangman_area.set_wrong_guesses(self.wrong_guesses)  # reset drawing

    def update_word_display(self):
        display = ' '.join([letter if letter in self.guessed_letters else '_' for letter in self.word])
        self.word_display.setText(display)

    def handle_guess(self):
        letter = self.input_box.text().lower()
        self.input_box.clear()

        if not letter.isalpha() or len(letter) != 1:
            self.message_box.append("❗ Please enter a single letter.")
            return

        if letter in self.guessed_letters:
            self.message_box.append("🔁 You already guessed that letter.")
            return

        self.guessed_letters.add(letter)
        self.guessed_letters_label.setText("Guessed Letters: " + ', '.join(sorted(self.guessed_letters)))

        if letter in self.word:
            self.message_box.append(f"✅ Good guess: {letter}")
        else:
            self.wrong_guesses += 1
            self.message_box.append(f"❌ Wrong guess: {letter}")
            self.hangman_area.set_wrong_guesses(self.wrong_guesses)

        self.update_word_display()
        self.check_game_status()

    def check_game_status(self):
        if all(letter in self.guessed_letters for letter in self.word):
            self.word_display.setText(' '.join(self.word))  # Show full word on win
            self.message_box.append("🎉 You won!")
            self.submit_button.setEnabled(False)
            self.input_box.setEnabled(False)
        elif self.wrong_guesses >= self.max_wrong:
            self.word_display.setText(' '.join(self.word))  # Show full word on loss
            self.message_box.append(f"⚠️ You lost! The word was '{self.word}'.")
            self.submit_button.setEnabled(False)
            self.input_box.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HangmanGame()
    window.show()
    sys.exit(app.exec_())
