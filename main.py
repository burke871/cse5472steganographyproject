import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui_main import Ui_MainWindow

class StegoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect buttons to placeholders
        self.ui.loadImageButton.clicked.connect(self.load_image)
        self.ui.encodeButton.clicked.connect(self.encode_message)
        self.ui.decodeButton.clicked.connect(self.decode_message)
        self.ui.saveImageButton.clicked.connect(self.save_image)

    def load_image(self):
        print("Load image clicked")

    def encode_message(self):
        print("Encode clicked")

    def decode_message(self):
        print("Decode clicked")

    def save_image(self):
        print("Save image clicked")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StegoApp()
    window.show()
    sys.exit(app.exec_())
