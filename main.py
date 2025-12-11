import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
import os
from ui_main import Ui_MainWindow
from encode import encode
from decode import decode

class StegoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect buttons to placeholders
        self.ui.loadImageButton.clicked.connect(self.load_image)
        self.ui.loadSecretFileButton.clicked.connect(self.load_secret_file)
        self.ui.encodeButton.clicked.connect(self.encode_message)
        self.ui.decodeButton.clicked.connect(self.decode_message)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            # Store file path if you’ll need it later
            self.image_path = file_path

            pixmap = QPixmap(file_path)
            img = pixmap.toImage()

            img = img.mirrored(True, True)  # False = no horizontal flip, True = vertical flip

            pixmap = QPixmap.fromImage(img)
            pixmap = pixmap.scaled(
                self.ui.imageLabel.width(),
                self.ui.imageLabel.height()
            )
            self.ui.imageLabel.setPixmap(pixmap)
            self.ui.imageLabel.setStyleSheet("")  # Remove placeholder border
            print(f"Loaded image: {os.path.basename(file_path)}")

    def load_secret_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Secret File",
            "",
            "All Files (*.*)"
        )
        if file_path:
            self.secret_file_path = file_path
            print(f"Loaded secret file: {file_path}")

    def encode_message(self):
        print("Encode clicked")
        encode(self.image_path, self.secret_file_path)

    def decode_message(self):
        print("Decode clicked")
        decode(self.image_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StegoApp()
    window.show()
    sys.exit(app.exec_())
