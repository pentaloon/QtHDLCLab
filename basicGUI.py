import sys, serial, logging, binascii
import serial.tools.list_ports
from PyQt5 import QtWidgets
from hdlc import HDLC

class QTextField(logging.Handler):
    def __init__(self, label = '', readonly = False):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self._label = QtWidgets.QLabel()
        self._label.setText(label)
        self.textField = QtWidgets.QPlainTextEdit()
        if readonly:
            self.textField.setReadOnly(True)
        self.layout.addWidget(self._label)
        self.layout.addWidget(self.textField)

    def emit(self, record):
        msg = self.format(record)
        self.textField.appendPlainText(msg)

class QTextLine(object):
    def __init__(self, label = '', readonly = False, text = '', inputMask = '', maxWidth = 0):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self._label = QtWidgets.QLabel()
        self._label.setText(label)
        self.line = QtWidgets.QLineEdit()
        self.line.setText(text)
        if readonly:
            self.line.setReadOnly(True)
            self.line.setStyleSheet('background: lightgray;')
        if inputMask != '':
            self.line.setInputMask(inputMask)
        if maxWidth > 0:
            self.line.setMaximumWidth(maxWidth)
        self.layout.addWidget(self._label)
        self.layout.addWidget(self.line)

    def get_bytes(self):
        return self.line.text().encode('utf-8')

class TxFrame(object):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QHBoxLayout()
        self._data = QTextLine('TX data', False, '00', 'hh hh hh hh hh hh hh hh hh hh hh hh hh hh hh hh')
        self._addr = QTextLine('addr', False, '00', 'Hh', 60)
        self._ctrl = QTextLine('ctrl', False, '00', 'Hh', 60)
        self._length = QTextLine('length', True, '', '', 60)
        self.layout.addLayout(self._data.layout)
        self.layout.addLayout(self._addr.layout)
        self.layout.addLayout(self._ctrl.layout)
        self.layout.addLayout(self._length.layout)

    def send(self, session):
        data = self.get_bytes()
        self._length.line.setText(str(len(data)))
        session.sendFrame(data)
   
    def get_bytes(self):
        addr = bytearray.fromhex(self._addr.line.text())
        ctrl = bytearray.fromhex(self._ctrl.line.text())
        payload = bytearray.fromhex(self._data.line.text())
        return addr + ctrl + payload


class RxFrame(object):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QHBoxLayout()
        self._data = QTextLine('RX data', True, '')
        self.layout.addLayout(self._data.layout)

    def retrieve(self, session):
        data = session.readFrame()
        logging.info(data)
        # self._data.line.setText(str(binascii.hexlify(data)))
        self._data.line.setText(' '.join('{:02x}'.format(x) for x in data))

class MainWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('HDLC Lab')
        self.setGeometry(200,200,600,400)
        self.session = None
        self.connection = QtWidgets.QHBoxLayout()
        self.port = QtWidgets.QComboBox()
        available_ports = serial.tools.list_ports.comports()
        for p in available_ports:
            logging.info(p.name)
            self.port.addItem(p.name)
        self.port.addItem('loop://')
        self.baudrate = QtWidgets.QComboBox()
        self.baudrate.addItems(['9600','115200','921600'])
        self.connection.addWidget(self.port)
        self.connection.addWidget(self.baudrate)
        self.port.currentIndexChanged.connect(self.update_session)
        self.baudrate.currentIndexChanged.connect(self.update_session)
        logger = QTextField('Log', True)
        logger.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s'))
        logging.getLogger().addHandler(logger)
        logging.getLogger().setLevel(logging.DEBUG)
        self.RX_frame = RxFrame()
        self.TX_frame = TxFrame()
        self._sendBtn = QtWidgets.QPushButton()
        self._sendBtn.setText('Send')
        self._sendBtn.setFocus()
        self._sendBtn.clicked.connect(self.on_click)
        grid = QtWidgets.QGridLayout()
        grid.addLayout(self.connection, 0,0)
        grid.addLayout(self.TX_frame.layout,1,0)
        grid.addLayout(self.RX_frame.layout,2,0)
        grid.addLayout(logger.layout,3,0)
        grid.addWidget(self._sendBtn, 4,0)
        self.setLayout(grid)

    def on_click(self):
        try:
            self.update_session()
            self.TX_frame.send(self.session)
            self.RX_frame.retrieve(self.session)
        except Exception as Argument:
            logging.exception('transmission failed')

    def update_session(self):
        self.serialConnection = serial.serial_for_url(str(self.port.currentText()), baudrate=int(self.baudrate.currentText()), timeout=1)
        self.session = HDLC(self.serialConnection)

# Log messages to stdout
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s %(name)s %(levelname)s %(message)s')
app = QtWidgets.QApplication(sys.argv)
mw = MainWindow()
mw.show()
mw.raise_()
sys.exit(app.exec_())