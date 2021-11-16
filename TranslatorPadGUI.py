import logging
from os import name
import sys
import webbrowser

from PySide6 import QtWidgets
import Translator
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QTextEdit,
    QWidget,
    QPushButton,
    QApplication,
)
from PySide6.QtCore import QRunnable, Qt, QThreadPool, QTimer, QTimerEvent


class TranslatorThread(QRunnable):
    def run(self):
        global name
        if not name:
            logging.warning("Name can't be empty")
        else:
            Translator.translatorloop(name)


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        self.init_ui()
        QTimer.startTimer(self, 700, timerType=Qt.CoarseTimer)
        
    def thread_count(self):
        logging.info("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def timerEvent(self, event: QTimerEvent) -> None:
        if Translator.active:
            self.square.setStyleSheet("background-color: green")
        else:
            self.square.setStyleSheet("background-color: red")
        self.charleftlbl.setText(
            "Translatable Characters left: " + str(Translator.char_left)
        )

        return super().timerEvent(event)

    def main_loop(self):
        global name
        name = self.name
        worker = TranslatorThread()
        self.threadpool.start(worker)

    def start_loop(self):
        if not self.name:
            pass
        else:
            Translator.start_loop()

    def stop_loop(self):
        Translator.stop_loop()

    def closeEvent(self, event):
        Translator.break_main_loop()
        logging.info("Program quit")

    def create_pads(self):
        if not self.name:
            logging.warning("Name can't be empty")
        else:
            Translator.create_pads(self.name)

    def set_name(self, event):
        self.name = event
        Translator.stop_loop()
        if self.name:
            self.sinkinput.setText("http://localhost:9001/p/" + self.name + "trans")
        else:
            self.sinkinput.setText("")

    def open_URL_source(self):
        url = f"http://localhost:9001/p/{self.name}"
        if not self.name:
            logging.warning("Name can't be empty")
        else:
            webbrowser.open(url, new=0, autoraise=True)

    def open_URL_sink(self):
        url = f"http://localhost:9001/p/{self.name}trans"
        if not self.name:
            pass
        else:
            webbrowser.open(url, new=0, autoraise=True)

    def init_ui(self):
        # Start Server and Translation Json Button
        self.startButton = QPushButton("Start \n Translation", self)
        self.startButton.move(20, 20)
        self.startButton.clicked.connect(self.start_loop)
        self.startButton.clicked.connect(self.main_loop)

        # Console
        self.console = QTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setFixedSize(210, 150)
        self.console.move(20, 300)
        self.console.setStyleSheet("color: white; background-color: black")

        # Stop Server and Translation Json Button
        self.StopButton = QPushButton("Stop \n Translation", self)
        self.StopButton.move(100, 20)
        self.StopButton.clicked.connect(self.stop_loop)

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
        self.sourceinput.textEdited.connect(Translator.break_main_loop)

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
        self.setWindowTitle("LTEP")
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
    ex.thread_count()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
