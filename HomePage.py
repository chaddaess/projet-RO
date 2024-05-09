from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QMovie
from PyQt5 import QtCore
from PLNE_Problem import CelebrityWidget
from PL_Problem import ToyFactoryGUI


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Home Page')
        self.setFixedSize(650, 650)
        layout = QVBoxLayout()

        # Add a label with some text
        label = QLabel("Welcome To Our End Of Course Project !")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-family: 'Arial'; margin-bottom: 20px; margin-top: 40px; font-weight: bold; color: #A67943  ;")
        layout.addWidget(label)
        gif_label = QLabel()
        movie = QMovie("welcome.gif")
        gif_label.setMovie(movie)
        movie.start()
        gif_label.setAlignment(QtCore.Qt.AlignCenter)
        gif_label.setStyleSheet("margin-top: 0px;")
        

        label = QLabel(
            "In this project,\n  we explored two different well-known operational research problems:")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-size: 20px; font-family: 'Calibri'; margin-bottom: 30px;color: #233154; font-weight: bold")
        layout.addWidget(label)
        layout.addWidget(gif_label)
        button1 = QPushButton(
            'Go to PL-Problem (Toy Factory Profit Maximization)')
        button1.setStyleSheet("font-size: 16px; font-family: 'Arial'; color: #233154 ; padding: 10px;font-weight: bold;")
        button1.clicked.connect(self.open_page1)
        layout.addWidget(button1)

        button2 = QPushButton('Go to PLNE-Problem (Celebrities)')
        button2.setStyleSheet("font-size: 16px; font-family: 'Arial'; color: #233154 ; padding: 10px; font-weight: bold;")
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
