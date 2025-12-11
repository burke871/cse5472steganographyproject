from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QFileDialog
)

class Ui_MainWindow:
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("BPCS Steganography App")
        MainWindow.resize(1200, 800)

        # Central widget
        self.central_widget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central_widget)

        # Buttons
        self.loadImageButton = QPushButton("Load Image")
        self.loadSecretFileButton = QPushButton("Load Secret File")
        self.encodeButton = QPushButton("Encode Message")
        self.decodeButton = QPushButton("Decode Message")

        # Image preview
        self.imageLabel = QLabel("No image loaded")
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setStyleSheet("border: 1px solid black;")
        self.imageLabel.setScaledContents(True)

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.loadImageButton)
        button_layout.addWidget(self.loadSecretFileButton)
        button_layout.addWidget(self.encodeButton)
        button_layout.addWidget(self.decodeButton)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.imageLabel)

        self.central_widget.setLayout(main_layout)
