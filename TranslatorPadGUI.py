import logging
from os import name
import sys
import ifcfg
import webbrowser
from PySide6 import QtWidgets
import Translator_for_GUI as Translator
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QTextEdit,
    QWidget,
    QPushButton,
    QApplication,
)
from PySide6.QtCore import Qt, QTimer, QTimerEvent


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.init_ui()
        QTimer.startTimer(self, 700, timerType=Qt.CoarseTimer)
        self.line_dic = {}
        self.gerold = []
        self.runtranslate= False
        self.nointernet = False
        self.currentip= ifcfg.interfaces()["Wireless LAN adapter Wi-Fi"]["inet"]
        self.internetflag=False
        if self.currentip == None:
            self.nointernet = True
        print(str(self.currentip))


    def timerEvent(self, event: QTimerEvent) -> None:
        if self.runtranslate:
            self.square.setStyleSheet("background-color: green")
            gertext, self.line_dic = Translator.translateonce(self.name, self.gerold, self.line_dic)
            self.gerold = gertext
        else:
            self.square.setStyleSheet("background-color: red")
        if not self.nointernet:
            self.charleftlbl.setText("Translatable Characters left: " + str(Translator.call_deepL_usage()))
        elif not self.internetflag:
            logging.error("No Internet")
            self.charleftlbl.setText("Offline, Please Restart with Internet")
            self.internetflag = True

        


        return super().timerEvent(event)

    def closeEvent(self, event):
        logging.info("Program quit")

    def create_pads(self):
        if not self.name:
            logging.warning("Name can't be empty")
        else:
            Translator.create_pads(self.name)

    def start_translate(self):
        self.runtranslate = True

    def stop_translate(self):
        self.runtranslate = False

    def set_name(self, event):
        self.name = event
        if self.name and not self.nointernet:
            self.sinkinput.setText(
                str(self.currentip) + ":9001/p/" + self.name + "trans"
                )
        elif self.nointernet:
            self.sinkinput.setText("No Internet")
        else:
            self.sinkinput.setText("")

    def open_URL_source(self):
        url = f"http://127.0.0.1:9001/p/{self.name}"
        if not self.name:
            logging.warning("Name can't be empty")
        else:
            webbrowser.open(url, new=0, autoraise=True)

    def open_URL_sink(self):
        url = f"http://127.0.0.1:9001/p/{self.name}trans"
        if not self.name:
            pass
        else:
            webbrowser.open(url, new=0, autoraise=True)

    def init_ui(self):
        # Start Server and Translation Json Button
        self.startButton = QPushButton("Start \n Translation", self)
        self.startButton.move(20, 20)
        self.startButton.clicked.connect(self.start_translate)

        # Console
        self.console = QTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setFixedSize(210, 150)
        self.console.move(20, 300)
        self.console.setStyleSheet("color: white; background-color: black")

        # Stop Server and Translation Json Button
        self.StopButton = QPushButton("Stop \n Translation", self)
        self.StopButton.move(100, 20)
        self.StopButton.clicked.connect(self.stop_translate)


        # Status LED
        self.square = QFrame(self)
        self.square.setGeometry(190, 30, 20, 20)
        self.square.setStyleSheet("background-color: black")

        # Label
        self.createpadlbl = QLabel("Create Pad", self)
        self.createpadlbl.move(20, 80)

        # English Pad URL
        self.sinkinput = QLineEdit(self)
        self.sinkinput.setReadOnly(True)
        self.sinkinput.move(20, 220)
        self.sinkinput.setFixedWidth(200)
        self.sinkinput.setPlaceholderText("English Pad URL")

        # German Pad Name Input
        self.sourceinput = QLineEdit(self)
        self.sourceinput.move(20, 100)
        self.sourceinput.setPlaceholderText("Pad Name")
        self.sourceinput.setFixedWidth(200)
        self.sourceinput.textEdited.connect(self.set_name)
        self.sourceinput.textEdited.connect(self.stop_translate)

        # Open current Pad in Browser
        self.opensourceButton = QPushButton("Open in \nBrowser", self)
        self.opensourceButton.move(20, 130)
        self.opensourceButton.clicked.connect(self.open_URL_source)

        # Create the Pad called "name" if it doesnt exist
        self.createButton = QPushButton("Create \n Pad", self)
        self.createButton.move(100, 130)
        self.createButton.clicked.connect(self.create_pads)

        # Label
        self.transpadlbl = QLabel("Translated Pad", self)
        self.transpadlbl.move(20, 200)

        # Open English Pad in Browser
        self.opensinkButton = QPushButton("Open in \nBrowser", self)
        self.opensinkButton.move(20, 250)
        self.opensinkButton.clicked.connect(self.open_URL_sink)

        # Displays remaining translatable characters
        self.charleftlbl = QLabel("", self)
        self.charleftlbl.setFixedSize(200, 20)
        self.charleftlbl.move(5, 460)

        # Main Window Properties
        self.setFixedSize(250, 480)
        self.setWindowTitle("LTP")
        self.show()


class QtLoggingHandler(logging.StreamHandler):
    def __init__(self, target: QtWidgets.QTextEdit):
        super().__init__()
        self._target = target

    def emit(self, record):
        msg = self.format(record)
        self._target.append(msg)


def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    app = QApplication(sys.argv)
    ex = GUI()
    handler = QtLoggingHandler(ex.console)
    handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()