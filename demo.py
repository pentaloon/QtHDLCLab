import sys
from PyQt5 import QtWidgets
import logging
from simple_hdlc import HDLC
import serial 

# Log messages to stdout
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s %(name)s %(levelname)s %(message)s')

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

class MainWindow(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HDLC demo")
        self.setGeometry(200,200,600,400)
        logTextBox = QTextEditLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)
        self._button = QtWidgets.QPushButton(self)
        self._button.setText('Test')
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(logTextBox.widget)
        layout.addWidget(self._button)
        self.setLayout(layout)
        self._button.clicked.connect(self.test)

    def test(self):
        s = serial.serial_for_url('loop://', timeout=1)
        # s = serial.Serial('/dev/tty0')
        h = HDLC(s)
        h.sendFrame(b"hello")
        logging.info(h.readFrame())  # Blocking

app = QtWidgets.QApplication(sys.argv)
mw = MainWindow()
mw.show()
mw.raise_()
sys.exit(app.exec_())