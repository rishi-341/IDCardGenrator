import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Button Style & OnClick Example")
        self.setGeometry(200, 200, 400, 250)

        self.initUI()

    def initUI(self):
        # Label
        self.label = QLabel("Click the button below 👇", self)
        self.label.setFont(QFont("Arial", 12))
        self.label.setStyleSheet("color: blue;")   # Font color

        # Button
        self.button = QPushButton("Click Me!", self)
        self.button.setFont(QFont("Verdana", 14, QFont.Bold))
        self.button.setStyleSheet(
            "QPushButton {"
            "background-color: #4CAF50;"   # Green background
            "color: white;"               # White font
            "border-radius: 10px;"
            "padding: 10px;"
            "}"
            "QPushButton:hover {"
            "background-color: #45a049;"   # Darker green on hover
            "}"
        )
        self.button.clicked.connect(self.on_button_click)  # OnClick method call

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_button_click(self):
        """This method is called when button is clicked"""
        self.label.setText("✅ Button was clicked!")
        self.label.setStyleSheet("color: red;")  # Change font color dynamically


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
