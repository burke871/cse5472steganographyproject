from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QFileDialog
)

class Ui_MainWindow:
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("Simple Steganography App")
        MainWindow.resize(600, 400)

        # Central widget
        self.central_widget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central_widget)

        # Buttons
        self.loadImageButton = QPushButton("Load Image")
        self.encodeButton = QPushButton("Encode Message")
        self.decodeButton = QPushButton("Decode Message")
        self.saveImageButton = QPushButton("Save Image")

        # Text box
        self.messageBox = QTextEdit()
        self.messageBox.setPlaceholderText("Enter message here...")

        # Image preview
        self.imageLabel = QLabel("No image loaded")
        self.imageLabel.setFixedSize(300, 300)
        self.imageLabel.setStyleSheet("border: 1px solid black;")
        self.imageLabel.setScaledContents(True)

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.loadImageButton)
        button_layout.addWidget(self.encodeButton)
        button_layout.addWidget(self.decodeButton)
        button_layout.addWidget(self.saveImageButton)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.imageLabel)
        main_layout.addWidget(self.messageBox)

        self.central_widget.setLayout(main_layout)
