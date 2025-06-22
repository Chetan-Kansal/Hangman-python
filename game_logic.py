import sys
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QFrame
)
from PyQt5.QtGui import QFont, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl

# from PyQt5.QtMultimedia import QSoundEffect

class HangmanDrawing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 400)
        self.max_parts = 7
        self.parts_remaining = self.max_parts
        self.animating = False
        self.melt_step = 0
        self.current_melting = None
        self.part_scales = [1.0] * self.max_parts  # scale of each part (1.0 = full size)
        self.bg_image = QPixmap("assets/images/background.jpg")

    def set_wrong_guesses(self, count):
        if self.animating:
            return  # prevent overlapping animations

        melt_index = self.max_parts - count
        if melt_index < 0 or melt_index >= self.max_parts:
            return

        self.current_melting = melt_index
        self.animating = True
        self.melt_step = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_melt)
        self.timer.start(50)  # every 50ms

        # self.melt_sound = QSoundEffect()
        # self.melt_sound.setSource(QUrl.fromLocalFile("melt.wav"))
        # self.melt_sound.setVolume(0.8)


    def animate_melt(self):
        if self.melt_step < 10:
            # shrink part by 10% each time
            self.part_scales[self.current_melting] -= 0.1
            self.melt_step += 1
            self.update()
        else:
            # Done melting
            self.part_scales[self.current_melting] = 0.0
            self.animating = False
            self.current_melting = None
            self.timer.stop()
            self.update()
        
        # self.melt_sound.play()
        

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        center_x = 150
        painter.drawPixmap(self.rect(), self.bg_image)
        painter.setBrush(Qt.white)  # Solid white snowballs


        def draw_scaled_ellipse(x, y, w, h, scale):
            if scale > 0:
                # Convert all arguments to int
                painter.drawEllipse(
                    int(center_x - w * scale / 2 + x),
                    int(y + (1 - scale) * h),
                    int(w * scale),
                    int(h * scale)
                )

        def draw_scaled_line(x1, y1, x2, y2, scale):
            if scale > 0:
                # Interpolate toward center for shrinking
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                x1 = cx + (x1 - cx) * scale
                y1 = cy + (y1 - cy) * scale
                x2 = cx + (x2 - cx) * scale
                y2 = cy + (y2 - cy) * scale
                # Convert line coordinates to int as well
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Snowman Parts (scaled)

        if self.part_scales[0] > 0:
            draw_scaled_ellipse(0, 250, 100, 100, self.part_scales[0])  # Base
        if self.part_scales[1] > 0:
            draw_scaled_ellipse(0, 180, 80, 80, self.part_scales[1])  # Middle
        if self.part_scales[2] > 0:
            draw_scaled_ellipse(0, 130, 60, 60, self.part_scales[2])  # Head
        if self.part_scales[3] > 0:
            draw_scaled_line(center_x - 40, 200, center_x - 90, 170, self.part_scales[3])  # Left arm
        if self.part_scales[4] > 0:
            draw_scaled_line(center_x + 40, 200, center_x + 90, 170, self.part_scales[4])  # Right arm
        if self.part_scales[5] > 0:
            # Face - also needs int conversion for ellipse arguments
            painter.drawEllipse(
                int(center_x - 15),
                int(150),
                int(5 * self.part_scales[5]),
                int(5 * self.part_scales[5])
            )
            painter.drawEllipse(
                int(center_x + 10),
                int(150),
                int(5 * self.part_scales[5]),
                int(5 * self.part_scales[5])
            )
            # drawArc typically takes int arguments, ensure they are int as well
            painter.drawArc(int(center_x - 15), int(165), int(30), int(15), int(0), int(-180 * 16))
        if self.part_scales[6] > 0:
            # drawLine and drawRect also need int arguments
            painter.drawLine(int(center_x - 30), int(130), int(center_x + 30), int(130))  # Hat brim
            painter.drawRect(int(center_x - 20), int(100), int(40), int(30))  # Hat top
        
    def reset(self):
        self.parts_remaining = self.max_parts
        self.animating = False
        self.current_melting = None
        self.part_scales = [1.0] * self.max_parts
        self.update()



class HangmanGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman Game")
        self.setGeometry(100, 100, 800, 500)

        self.word_bank = {
            "Fruits": ["apple", "banana", "orange", "grape"],
            "Animals": ["tiger", "elephant", "giraffe", "kangaroo"]
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
    window = HangmanGame()
    window.show()
    sys.exit(app.exec_())
