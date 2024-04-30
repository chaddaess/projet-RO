from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QMovie
from PyQt5 import QtCore
from PLNE_Problem import CelebrityWidget
from PL_Problem import ToyFactoryGUI


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Home Page')
        self.setFixedSize(600, 600)
        layout = QVBoxLayout()

        # Add a label with some text
        label = QLabel("Welcome To Our End Of Course Project !")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        gif_label = QLabel()
        movie = QMovie("burn-elmo.gif")
        gif_label.setMovie(movie)
        movie.start()
        gif_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(gif_label)

        label = QLabel(
            "In this project, we explored two different well-known operational research problems.")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        button1 = QPushButton(
            'Go to PL-Problem (Toy Factory Profit Maximization)')
        button1.clicked.connect(self.open_page1)
        layout.addWidget(button1)

        button2 = QPushButton('Go to PLNE-Problem (Celebrities)')
        button2.clicked.connect(self.open_page2)
        layout.addWidget(button2)

        self.setLayout(layout)
        self.page1 = None  # Initialize page1 as None
        self.page2 = None  # Initialize page1 as None

    def open_page1(self):
        self.hide()  # Hide the home page
        if not self.page1:  # Check if page1 is already created
            self.page1 = ToyFactoryGUI()
        self.page1.show()

    def open_page2(self):
        self.hide()  # Hide the home page
        if not self.page2:  # Check if page1 is already created
            self.page2 = CelebrityWidget()
        self.page2.show()
