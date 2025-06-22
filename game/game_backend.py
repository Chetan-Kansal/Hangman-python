import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QFrame
)

from PyQt5.QtGui import QFont

from game_frontend import SnowmanDrawing

class SnowmanGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman Game")
        self.setGeometry(100, 100, 800, 500)

        self.word_bank = {
            "Animals": [
                "elephant", "giraffe", "kangaroo", "dolphin", "cheetah",
                "penguin", "butterfly", "squirrel", "rhinoceros", "chimpanzee",
                "crocodile", "flamingo", "chameleon", "hedgehog", "jellyfish",
                "leopard", "nightingale", "ostrich", "toucan", "walrus"
            ],
            "Countries": [
                "australia", "brazil", "canada", "denmark", "egypt",
                "france", "germany", "india", "japan", "mexico",
                "netherlands", "new zealand", "norway", "russia", "spain",
                "thailand", "turkey", "united kingdom", "united states", "vietnam"
            ],
            "Fruits & Vegetables": [
                "apple", "banana", "carrot", "grape", "broccoli",
                "mango", "orange", "potato", "strawberry", "tomato",
                "watermelon", "zucchini", "pineapple", "cucumber", "avocado",
                "blueberry", "cherry", "lettuce", "mushroom", "pear"
            ],
            "Occupations": [
                "teacher", "doctor", "engineer", "artist", "chef",
                "pilot", "scientist", "firefighter", "police officer", "programmer",
                "journalist", "architect", "musician", "lawyer", "nurse",
                "veterinarian", "electrician", "plumber", "accountant", "baker"
            ],
            "Sports": [
                "basketball", "soccer", "tennis", "baseball", "golf",
                "volleyball", "swimming", "cricket", "badminton", "athletics",
                "boxing", "cycling", "fencing", "gymnastics", "hockey",
                "judo", "rugby", "skiing", "surfing", "table tennis"
            ]
        }

        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e0f7fa, stop:1 #a7ffeb
                );
            }
        """)


        self.setup_ui()
        self.new_game()

    def setup_ui(self):
        main_layout = QHBoxLayout()

        # Left section (Word display, input, messages)
        left_layout = QVBoxLayout()

        self.category_label = QLabel("Category: ")
        self.category_label.setFont(QFont("Segoe UI", 14))
        left_layout.addWidget(self.category_label)

        self.word_display = QLabel("")
        self.word_display.setFont(QFont("Courier New", 24))
        left_layout.addWidget(self.word_display)

        self.input_label = QLabel("Enter a letter:")
        self.input_label.setFont(QFont("Segoe UI", 24))
        left_layout.addWidget(self.input_label)

        self.input_box = QLineEdit()
        self.input_box.setMaxLength(1)
        left_layout.addWidget(self.input_box)
        self.input_box.returnPressed.connect(self.handle_guess)  # Guess on Enter key

        self.input_box.setStyleSheet("""
            QLineEdit {
                border: 2px solid #00acc1;
                border-radius: 10px;
                padding: 6px;
                font-size: 16px;
                background: #ffffff;
            }
        """)

        self.submit_button = QPushButton("Guess")
        left_layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.handle_guess)

        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #26c6da;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #00acc1;
            }
        """)

        self.new_game_button = QPushButton("New Game")
        left_layout.addWidget(self.new_game_button)
        self.new_game_button.clicked.connect(self.new_game)

        self.new_game_button.setStyleSheet("""
            QPushButton {
                background-color: #66bb6a;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #43a047;
            }
        """)

        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)
        left_layout.addWidget(self.message_box)

        self.message_box.setStyleSheet("""
            QTextEdit {
                background-color: #f1f8e9;
                border: 2px solid #c5e1a5;
                border-radius: 10px;
                padding: 6px;
                font-size: 14px;
            }
        """)

        self.guessed_letters_label = QLabel("Guessed Letters: ")
        self.guessed_letters_label.setFont(QFont("Segoe UI", 12))
        left_layout.addWidget(self.guessed_letters_label)

        # Right section (Hangman drawing area)
        self.hangman_area = SnowmanDrawing()
        self.hangman_area.setMinimumWidth(300)

        main_layout.addLayout(left_layout, 2)
        main_layout.addWidget(self.hangman_area, 1)

        self.setLayout(main_layout)


    def new_game(self):
        self.category, words = random.choice(list(self.word_bank.items()))
        self.word = random.choice(words)
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.max_wrong = 7

        self.category_label.setText(f"Category: {self.category}")
        self.update_word_display()
        self.message_box.clear()
        self.submit_button.setEnabled(True)
        self.input_box.setEnabled(True)
        self.guessed_letters_label.setText("Guessed Letters: ")
        self.hangman_area.set_wrong_guesses(self.wrong_guesses)  # reset drawing
        self.hangman_area.reset()  # Reset snowman to full


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
    window = SnowmanGame()
    window.show()
    sys.exit(app.exec_())
