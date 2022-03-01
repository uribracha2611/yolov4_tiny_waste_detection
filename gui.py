import sys

import cv2
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot, QThread, QObject, pyqtSignal, QMutex, QUrl, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
# Class that manages the gui
class Gui:
    def __init__(self):
        global file_save_path  # file path of chosen image, used later
        file_save_path = None
        # most of the following lines builds the Parts of the gui
        # QApplication is for the application, Qlabel is for showing text and images, QPushButton is for buttons
        # setFont is function to set the font,
        # #setText sets the text of move places the widgit in the gui and
        # connect connects a function to somthing that happens (usually click
        self.app = QApplication(sys.argv)  # creating application
        self.win = QMainWindow()
        self.worker=Thread() #thread for video recording
        self.worker.changePixmap.connect(self.setImage)
        self.win.setGeometry(200, 200, 1200, 1200)
        width, height = self.win.frameGeometry().width(), self.win.frameGeometry().height()
        self.win.setWindowTitle("School project Uri Bracha-Gui app")
        self.show_video=QLabel(self.win)
        self.show_video.move(280, 120)

        self.show_video.resize(300, 300)
        self.start_button=QPushButton(self.win)
        self.start_button.setText("start video")
        self.start_button.move(280,450)
        self.start_button.clicked.connect(lambda : self.worker.start())

        self.start_button = QPushButton(self.win)
        self.start_button.setText("stop video")
        self.start_button.move(620, 450)

        self.win.show()  # activating gui
        sys.exit(self.app.exec_())  # code for exiting gui when close is clicked

    def setImage(self, image):
        self.show_video.setPixmap(QPixmap.fromImage(image))
class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(300, 300, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


if __name__ == '__main__':
    g = Gui()