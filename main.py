import sys, pandas as pd
# import pdf
import remaining as pdf
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QFileDialog, QLabel, QComboBox, QTableWidget,
    QTableWidgetItem, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont

class IDCardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ID Card Generator")
        self.resize(800, 600)
        
        container = QWidget()
        container.setStyleSheet("""
                                background: $fff;
                            """)
        layout = QVBoxLayout()
        
        self.load_button = QPushButton("Load Excel")
        self.load_button.setFixedSize(260,30)
        self.load_button.clicked.connect(self.load_excel)
        self.load_button.setFont(QFont("Arial", 12))
        self.load_button.setStyleSheet("""
                                        background: #38b6ff; 
                                        color: white; 
                                        border-radius: 10%;
                                        margin: auto;
                                       """) 
        self.vertical = QHBoxLayout()
        self.vertical.addWidget(self.load_button)
        layout.addLayout(self.vertical)
        
        self.orientation_box = QComboBox()
        self.orientation_box.addItems(["Landscape", "Portrait"])
        layout.addWidget(QLabel("Page Orientation:"))
        layout.addWidget(self.orientation_box)
        
        # self.design = QComboBox()
        # self.design.addItems(["BCom / BA", "BBA", "MCom / MA", "BJMS"])
        # layout.addWidget(QLabel("Design Layout:"))
        # layout.addWidget(self.design)
        
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        self.generate_button = QPushButton("Generate PDF")
        self.generate_button.clicked.connect(self.generate_pdf)
        layout.addWidget(self.generate_button)
        
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_excel(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        if file:
            self.df = pd.read_excel(file)
            self.display_data(self.df)
            # pdf.create_pdf(df[0])


    def display_data(self, df):
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(df.columns)
        for r in range(df.shape[0]):
            for c in range(df.shape[1]):
                self.table.setItem(r, c, QTableWidgetItem(str(df.iat[r, c])))

    def generate_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save PDF Report", 
            "", 
            "PDF Files (*.pdf)"
        )
        if file_path:
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            try:
                pdf.create_pdf_4x2(self.df, file_path)
                print(f"Success: PDF saved to {file_path}")
            except Exception as e:
                print(f"Error saving PDF: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = IDCardApp()
    win.show()
    sys.exit(app.exec_())
