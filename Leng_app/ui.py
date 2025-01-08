from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QSlider, QProgressBar, QTextEdit, QDialogButtonBox,
    QTableWidget, QTableWidgetItem, QDialog
)
from PyQt5.QtCore import Qt


class LanguageLearningUI:
    def setup_ui(self, main_window):
        # Set main window properties
        main_window.setWindowTitle("Language Learning App")
        main_window.setGeometry(100, 100, 700, 400)

        # Container for the main layout
        container = QWidget(main_window)
        main_layout = QVBoxLayout(container)

        # Word Display
        main_window.word_label = QLabel("Press 'Start' to begin", main_window)
        main_window.word_label.setAlignment(Qt.AlignCenter)
        main_window.word_label.setStyleSheet("font-size: 24px;")
        main_layout.addWidget(main_window.word_label)

        # Timer Display
        main_window.timer_label = QLabel("Time: 0.000s", main_window)
        main_window.timer_label.setAlignment(Qt.AlignCenter)
        main_window.timer_label.setStyleSheet("font-size: 18px;")
        main_layout.addWidget(main_window.timer_label)

        # Progress Bar + Lap Label
        progress_layout = QHBoxLayout()
        main_window.progress_bar = QProgressBar(main_window)
        progress_layout.addWidget(main_window.progress_bar)

        main_window.lap_label = QLabel("Lap: 1", main_window)
        main_window.lap_label.setStyleSheet("font-size: 16px;")
        progress_layout.addWidget(main_window.lap_label)

        main_layout.addLayout(progress_layout)

        # Start Button
        main_window.start_button = QPushButton("Start", main_window)
        main_window.start_button.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            height: 50px;
            width: 100px;
            border-radius: 10px;
            background-color: #9bb291;
            color: white;
        """)
        main_layout.addWidget(main_window.start_button, alignment=Qt.AlignCenter)

        # Buttons (Yes, No)
        button_layout = QHBoxLayout()

        main_window.yes_button = QPushButton("Yes", main_window)
        main_window.yes_button.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            height: 80px;
            width: 150px;
            border-radius: 10px;
            background-color: #9bb291;
            color: white;
        """)
        button_layout.addWidget(main_window.yes_button)

        main_window.no_button = QPushButton("No", main_window)
        main_window.no_button.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            height: 80px;
            width: 150px;
            border-radius: 10px;
            background-color: #9bb291;
            color: white;
        """)
        button_layout.addWidget(main_window.no_button)

        main_layout.addLayout(button_layout)

        # Volume Slider
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume:", main_window)
        volume_layout.addWidget(volume_label)

        main_window.volume_slider = QSlider(Qt.Horizontal, main_window)
        main_window.volume_slider.setRange(0, 100)
        main_window.volume_slider.setValue(100)
        volume_layout.addWidget(main_window.volume_slider)

        main_layout.addLayout(volume_layout)

        # Action Buttons (Reset, Scoreboard, Add/Delete Words)
        actions_layout = QHBoxLayout()

        # Reset Button
        main_window.reset_scoreboard_button = QPushButton("Reset", main_window)
        main_window.reset_scoreboard_button.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            width: 80px;
            height: 30px;
            border-radius: 5px;
            background-color: #9bb291;
            color: white;
        """)
        actions_layout.addWidget(main_window.reset_scoreboard_button)

        # Scoreboard Button
        main_window.scoreboard_button = QPushButton("Scoreboard", main_window)
        main_window.scoreboard_button.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            width: 150px;
            height: 30px;
            border-radius: 5px;
            background-color: #9bb291;
            color: white;
        """)
        actions_layout.addWidget(main_window.scoreboard_button)

        # Add/Delete Words Button
        main_window.manage_words_button = QPushButton("Add/Delete Words", main_window)
        main_window.manage_words_button.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            width: 150px;
            height: 30px;
            border-radius: 5px;
            background-color: #9bb291;
            color: white;
        """)
        actions_layout.addWidget(main_window.manage_words_button)

        main_layout.addLayout(actions_layout)

        # Set the layout on the main window
        main_window.setCentralWidget(container)
