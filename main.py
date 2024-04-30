import sys
from PyQt5.QtWidgets import QApplication
from HomePage import HomePage
# GUI styles
style_sheet = """
    QWidget {
        background-color: white;
    }
    QLineEdit {
        background-color: #f0f0f0; /* Light gray */
        border: 1px solid #ccc; /* Light gray border */
        border-radius: 3px;
        padding: 5px;
    }
    QLineEdit:focus {
        border-color: #33a6cc; /* Focus color */
    }
    QPushButton {
        background-color: #BED7DC; /* Light purple */
        color: white;
        font-size: 16px;
        padding: 5px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #B3C8CF; /* Dark purple */
    }
    QPushButton:pressed {
        background-color: #496989; /* Even darker purple */
    }
    QPushButton.remove_btn {
        background-color: #FF4D4D; /* Red */
        color: white;
    }

    SolveButton:pressed {
        background-color: #C6EBC5; /* Green */
        color: white;
    }
    DeleteButton{
        background-color:#DD5746
    }
    DeleteButton:hover{
    background-color:rgb(190,39,39)
    }
    DeleteButton:pressed{
        background-color:black
    }
"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)

    home_page = HomePage()
    home_page.show()
    sys.exit(app.exec_())
