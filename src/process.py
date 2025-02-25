import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
)
from PyQt5.QtGui import QFont, QFontDatabase, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer

class InstallScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OrangDebloat Installer")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowState(Qt.WindowFullScreen | Qt.WindowActive)
        self.load_chakra_petch_font()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Debloating In Progress")
        title_label.setStyleSheet("color: white; font-weight: bold;")
        title_label.setFont(QFont("Minecraftia", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        body_label = QLabel("Sit and relax while program finishes it's work. System will restart automaticly.")
        body_label.setStyleSheet("color: white;")
        body_label.setFont(QFont("Minecraftia", 18))
        body_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(body_label)
        
        layout.addSpacing(30)
        spinner_layout = QHBoxLayout()
        spinner_layout.setAlignment(Qt.AlignCenter)
        
        self.spinner = LoadingSpinner()
        spinner_layout.addWidget(self.spinner)
        self.spinner.start_spinning()
        
        layout.addLayout(spinner_layout)
        self.setLayout(layout)

    def load_chakra_petch_font(self):
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(base_path, "Minecraftia-Regular.ttf")
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id == -1:
                print("Failed to load font.")
            else:
                print("Font loaded successfully.")
        except Exception as e:
            print(f"Error loading font: {e}")
class LoadingSpinner(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedSize(100, 100)
        self.setStyleSheet("background-color: transparent;")
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start(30)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(6)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        rect = self.rect().adjusted(10, 10, -10, -10)
        painter.drawArc(rect, self.angle * 16, 100 * 16)

    def start_spinning(self):
        self.angle = 0
        self.update()
    def on_timeout(self):
        self.angle -= 5
        if self.angle <= -360:
            self.angle = 0
        self.update()