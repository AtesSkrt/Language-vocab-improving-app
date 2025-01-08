import sys
import csv
import os
import time
import random
import pygame

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QLabel, QTextEdit, QDialogButtonBox, QProgressBar
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QCloseEvent

# Import the UI setup from ui.py
from ui import LanguageLearningUI


class LanguageLearningApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Instantiate the UI class and build the interface
        self.ui = LanguageLearningUI()
        self.ui.setup_ui(self)

        # -------------- WORDS & LAPS --------------
        self.words = [
            "Hello", "Goodbye", "Thank you", "Please", "Sorry",
            "Morning", "Evening", "Night", "Computer", "Music"
        ]
        self.lap_counter = 1
        self.remaining_words = []
        self.word_index = 0
        self.current_word = ""

        # -------------- TIMER --------------
        self.session_active = False
        self.session_timer = QTimer(self)
        self.session_timer.timeout.connect(self.update_timer)
        self.word_start_time = None  # Time when the current word began showing

        # -------------- SCOREBOARD --------------
        self.scoreboard_file = "scoreboard.csv"
        self.scoreboard_data = {}
        self.load_scoreboard()


        # -------------- PYGAME SOUND --------------
        pygame.mixer.init()
        self.sfx_start = pygame.mixer.Sound("sfx_start.wav")
        self.sfx_yes = pygame.mixer.Sound("sfx_yes.wav")
        self.sfx_no = pygame.mixer.Sound("sfx_no.wav")
        self.sfx_finish = pygame.mixer.Sound("sfx_finish.wav")
        self.sfx_reset = pygame.mixer.Sound("sfx_reset.wav")

        # -------------- UI CONNECTIONS --------------
        self.start_button.clicked.connect(self.toggle_session)
        self.yes_button.clicked.connect(lambda: self.record_response("yes"))
        self.no_button.clicked.connect(lambda: self.record_response("no"))
        self.volume_slider.valueChanged.connect(self.adjust_volume)
        self.scoreboard_button.clicked.connect(self.show_scoreboard)
        self.manage_words_button.clicked.connect(self.manage_words)
        self.reset_scoreboard_button.clicked.connect(self.reset_scoreboard)

        # Set up the progress bar and lap label
        self.progress_bar.setRange(0, len(self.words))
        self.progress_bar.setValue(0)
        self.lap_label.setText(f"Lap: {self.lap_counter}")

    # ----------------------------------------------------------
    #                      SESSION LOGIC
    # ----------------------------------------------------------
    def toggle_session(self):
        """Toggles between Start and Finish states."""
        if not self.session_active:
            # START the session
            self.session_active = True
            self.start_button.setText("Finish")
            self.play_sound(self.sfx_start)

            if self.word_index == 0 and len(self.remaining_words) == 0:
                # Begin a new lap
                self.start_new_lap()

            # Start updating the timer
            self.session_timer.start(100)

            # Show first word if not already displayed
            if not self.current_word:
                self.show_next_word()
        else:
            # FINISH the session
            self.session_active = False
            self.start_button.setText("Start")
            self.play_sound(self.sfx_finish)

            # Stop the timer
            self.session_timer.stop()

    def start_new_lap(self):
        """Resets the list of words for a new lap and shuffles them."""
        self.lap_label.setText(f"Lap: {self.lap_counter}")
        self.remaining_words = self.words.copy()
        random.shuffle(self.remaining_words)
        self.word_index = 0
        self.progress_bar.setRange(0, len(self.words))
        self.progress_bar.setValue(0)

    def show_next_word(self):
        """Displays the next word from the shuffled list."""
        if not self.remaining_words:
            # Done with this lap
            self.lap_counter += 1
            self.start_new_lap()

        self.current_word = self.remaining_words.pop()
        self.word_index += 1
        self.progress_bar.setValue(self.word_index)

        self.word_start_time = time.time()
        self.word_label.setText(self.current_word)

    def update_timer(self):
        """Updates the displayed timer (time spent on the current word)."""
        if self.word_start_time and self.session_active:
            current_time = time.time()
            elapsed = current_time - self.word_start_time
            self.timer_label.setText(f"Time: {elapsed:.3f}s")

    def record_response(self, response_type: str):
        """Called when user clicks Yes/No; updates scoreboard and proceeds to next word."""
        if not self.session_active or not self.current_word:
            return

        # Calculate time for this word
        current_time = time.time()
        time_spent = current_time - self.word_start_time

        # Update scoreboard
        self.update_scoreboard(self.current_word, response_type, time_spent)

        # Play sound
        if response_type == "yes":
            self.play_sound(self.sfx_yes)
        else:
            self.play_sound(self.sfx_no)

        # Display next word
        self.show_next_word()

    # ----------------------------------------------------------
    #                      SCOREBOARD LOGIC
    # ----------------------------------------------------------
    def load_scoreboard(self):
        """Load existing scoreboard data or create a new file with headers if none."""
        if not os.path.exists(self.scoreboard_file):
            with open(self.scoreboard_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Word", "Yes Count", "No Count", "Avg Time", "Not Learned"])
            return

        with open(self.scoreboard_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                word = row["Word"]
                yes = int(row["Yes Count"])
                no = int(row["No Count"])
                avg_time_str = row["Avg Time"] or "0"
                # We won't store "avg_time" directly because we reconstruct from times
                # However, we can keep an empty list for times. The CSV only has the final average.
                self.scoreboard_data[word] = {
                    "yes": yes,
                    "no": no,
                    "times": []  # We'll update times going forward
                }

    def update_scoreboard(self, word, response_type, time_spent):
        """Updates scoreboard data in memory, then writes to CSV."""
        if word not in self.scoreboard_data:
            self.scoreboard_data[word] = {"yes": 0, "no": 0, "times": []}

        if response_type == "yes":
            self.scoreboard_data[word]["yes"] += 1
        else:
            self.scoreboard_data[word]["no"] += 1

        self.scoreboard_data[word]["times"].append(time_spent)

        # Re-save entire scoreboard
        self.save_scoreboard()

    def save_scoreboard(self):
        """Writes in-memory scoreboard data to the CSV file."""
        with open(self.scoreboard_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Word", "Yes Count", "No Count", "Avg Time", "Not Learned"])
            for word, stats in self.scoreboard_data.items():
                yes_count = stats["yes"]
                no_count = stats["no"]
                times = stats["times"]
                avg_time = round(sum(times)/len(times), 3) if times else 0.0
                not_learned = "Yes" if no_count > yes_count else "No"
                writer.writerow([word, yes_count, no_count, avg_time, not_learned])

    def show_scoreboard(self):
        """Opens a dialog that displays the scoreboard contents in a QTableWidget."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Scoreboard")
        dialog.setGeometry(150, 150, 600, 400)

        # Create a QTableWidget
        table = QTableWidget(dialog)

        # Read CSV to fill table
        with open(self.scoreboard_file, mode='r', newline='') as file:
            rows = list(csv.reader(file))
            if rows:
                headers = rows[0]
                data_rows = rows[1:]
                table.setColumnCount(len(headers))
                table.setRowCount(len(data_rows))
                table.setHorizontalHeaderLabels(headers)

                for i, rowdata in enumerate(data_rows):
                    for j, cell in enumerate(rowdata):
                        table.setItem(i, j, QTableWidgetItem(cell))
            else:
                # If empty
                table.setColumnCount(5)
                table.setHorizontalHeaderLabels(["Word", "Yes Count", "No Count", "Avg Time", "Not Learned"])
                table.setRowCount(0)

        # Enable sorting
        table.setSortingEnabled(True)

        # Add the table to the dialog layout
        layout = QVBoxLayout(dialog)
        layout.addWidget(table)

        # Add a close button
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.exec_()

    def reset_scoreboard(self):
        """Resets the scoreboard by clearing all data and rewriting the CSV file."""
        # Play reset sound
        self.play_sound(self.sfx_reset)

        # Reset in-memory scoreboard data
        self.scoreboard_data = {}

        # Overwrite the CSV file with just the headers
        with open(self.scoreboard_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Word", "Yes Count", "No Count", "Avg Time", "Not Learned"])

        # Provide feedback to the user
        self.word_label.setText("Scoreboard has been reset.")
        self.timer_label.setText("Time: 0.000s")
        self.progress_bar.setValue(0)
        self.lap_label.setText(f"Lap: {self.lap_counter}")

        print("Scoreboard reset successfully.")

    # ----------------------------------------------------------
    #                     MANAGE WORDS
    # ----------------------------------------------------------
    def manage_words(self):
        """Dialog to add or delete words (comma-separated)."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add/Delete Words")
        dialog.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout(dialog)
        info_label = QLabel("Edit the words below (separate with commas):", dialog)
        layout.addWidget(info_label)

        text_box = QTextEdit(dialog)
        text_box.setText(", ".join(self.words))
        layout.addWidget(text_box)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)

        def apply_changes():
            new_text = text_box.toPlainText()
            new_word_list = [w.strip() for w in new_text.split(",") if w.strip()]
            self.words = new_word_list

            # Reset session data so new words take effect immediately
            self.session_timer.stop()
            self.session_active = False
            self.start_button.setText("Start")
            self.word_label.setText("Press 'Start' to begin")
            self.timer_label.setText("Time: 0.000s")
            self.current_word = ""
            self.remaining_words = []
            self.word_index = 0
            self.progress_bar.setValue(0)

            dialog.accept()

        button_box.accepted.connect(apply_changes)
        button_box.rejected.connect(dialog.reject)

        dialog.exec_()

    # ----------------------------------------------------------
    #                     SOUND & VOLUME
    # ----------------------------------------------------------
    def play_sound(self, sound):
        sound.play()

    def adjust_volume(self, value):
        volume = value / 100.0
        self.sfx_start.set_volume(volume)
        self.sfx_yes.set_volume(volume)
        self.sfx_no.set_volume(volume)
        self.sfx_finish.set_volume(volume)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LanguageLearningApp()
    window.show()
    sys.exit(app.exec_())
