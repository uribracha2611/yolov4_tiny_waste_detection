import os

from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot, QThread, QObject, pyqtSignal, QMutex, QUrl,Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PIL import Image
import sys
from pathlib import Path
from tensorflow_functions import predict
import time


class Worker(QThread):
    image_path = pyqtSignal(str)
    def __init__(self,parent=None):

        self._mutex = QMutex()

        super().__init__()

    def run(self):
        self._mutex.lock()
        img = Image.open(file_save_path)
        if not Path("saves").exists():
            os.mkdir("saves")

        img_path_for_pred = Path("saves/" + time.strftime("%Y%m%d-%H%M%S") + ".jpg")
        img.save(str(img_path_for_pred))

        img_path_for_show = predict(str(img_path_for_pred))
        self.image_path.emit(img_path_for_show)

        self.finished.emit()
        self._mutex.unlock()


class Gui:
    def __init__(self):
        global  file_save_path
        Is_Image=None
        file_save_path=None
        self.app = QApplication(sys.argv)
        self.win = QMainWindow()
        self.win.setGeometry(200, 200, 1200, 1200)
        width, height = self.win.frameGeometry().width(), self.win.frameGeometry().height()
        self.win.setWindowTitle("School project Uri Bracha-Gui app")
        self.worker=Worker()

        self.title = QLabel(self.win)
        self.title.setFont(QFont("Times", 14, QFont.Bold))
        self.title.setText("School project Uri Bracha-Gui app")
        self.title.adjustSize()
        self.title.move((width // 4) + 50, 0)

        self.text = QLabel(self.win)
        self.text.setFont(QFont("Times", 14))
        self.text.setText("choose an image to process:")
        self.text.move(50, 75)
        self.text.adjustSize()

        self.button = QPushButton(self.win)
        self.button.setText("Browse..")
        self.button.setFont(QFont("Times", 14))
        self.button.adjustSize()
        self.button.move(350, 75)
        self.button.clicked.connect(self.file_dialog)

        self.file_text = QLabel(" file not chosen ...", self.win)
        self.file_text.setFont(QFont("Times", 14))
        self.file_text.adjustSize()
        self.file_text.move(500, 75)

        self.submit = QPushButton(self.win)
        self.submit.setText("process")
        self.submit.setFont(QFont("Times", 14))
        self.submit.adjustSize()
        self.submit.clicked.connect(self.submit_func)
        self.submit.move(350, 175)


        self.image_show = QLabel(self.win)
        self.image_show.move(350, 175)

        self.image_result=QLabel(self.win)

        self.image_result = QLabel(self.win)

        self.win.show()
        sys.exit(self.app.exec_())

    def file_dialog(self):
        global file_save_path
        file, check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()", "")

        path = Path(file)
        file_save_path = file
        self.file_text.setText(path.name)
        pix=QPixmap(file)
        if pix.height()>500:
            pix =pix.scaled (pix.width(), 500, Qt.KeepAspectRatio, Qt.FastTransformation)
        if pix.width()>500:
            pix =pix.scaled (500, pix.height(), Qt.KeepAspectRatio, Qt.FastTransformation)

        self.image_show.setPixmap(pix)
        self.image_show.adjustSize()
        self.submit.move(350,75+pix.height())

    def submit_func(self):
            # Step 2: Create a QThread object
            self.worker.image_path.connect(self.edit_image)
            self.worker.start()

    def edit_image(self,t):
        pix=QPixmap(t)
        if pix.height()>350:
            pix =pix.scaled (pix.width(), 350, Qt.KeepAspectRatio, Qt.FastTransformation)
        if pix.width()>350:
            pix =pix.scaled (350, pix.height(), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.image_result.setPixmap(pix)
        self.image_result.adjustSize()
        self.image_result.move(350,self.button.height()+self.button.y()+pix.height()+150)

if __name__ == '__main__':
    g = Gui()
