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

#threading to stop the application from freezing when process browse_button is clicked
class Worker(QThread):
    image_path = pyqtSignal(str) # object that signal when the thread is done, and returns the image_path for the gui
    def __init__(self,parent=None):

        self._mutex = QMutex() #QMutex is used to prevent mutation of the data used by the thread

        super().__init__() # calling Qthread __init__()

# function that runs the Thread and calls the predict function
    def run(self):
        self._mutex.lock() # locking the data
        img = Image.open(file_save_path) ## opning the image
        if not Path("saves").exists():
            os.mkdir("saves") #creating save folder if it doesn't exist

        img_path_for_pred = Path("saves/" + time.strftime("%Y%m%d-%H%M%S") + ".jpg") #crating path for save
        img.save(str(img_path_for_pred)) # saving

        img_path_for_show = predict(str(img_path_for_pred)) #calling prediction function see tensorflow_function code part
        self.image_path.emit(img_path_for_show) #telling the gui the code is done

        self.finished.emit() # QThread requires this line
        self._mutex.unlock() # unlocking the data used by the thread

# Class that manages the gui
class Gui:
    def __init__(self):
        global  file_save_path #file path of chosen image, used later
        file_save_path=None
        #most of the following lines builds the Parts of the gui
        #QApplication is for the application, Qlabel is for showing text and images, QPushButton is for buttons
        #setFont is function to set the font,
        # #setText sets the text of move places the widgit in the gui and
        # connect connects a function to somthing that happens (usually click
        self.app = QApplication(sys.argv) # creating application
        self.win = QMainWindow()
        self.win.setGeometry(200, 200, 1200, 1200)
        width, height = self.win.frameGeometry().width(), self.win.frameGeometry().height()
        self.win.setWindowTitle("School project Uri Bracha-Gui app")
        self.worker=Worker()

        self.title = QLabel(self.win) #title of the project
        self.title.setFont(QFont("Times", 14, QFont.Bold))
        self.title.setText("School project Uri Bracha-Gui app")
        self.title.adjustSize()
        self.title.move((width // 4) + 50, 0)

        self.chosen_image_name = QLabel(self.win) # chosen_image_name for showing chosen image name
        self.chosen_image_name.setFont(QFont("Times", 14))
        self.chosen_image_name.setText("choose an image to process:")
        self.chosen_image_name.move(50, 75)
        self.chosen_image_name.adjustSize()

        self.browse_button = QPushButton(self.win) # browse_button to allow browsing
        self.browse_button.setText("Browse..")
        self.browse_button.setFont(QFont("Times", 14))
        self.browse_button.adjustSize()
        self.browse_button.move(350, 75)
        self.browse_button.clicked.connect(self.file_dialog)

        self.file_text = QLabel(" file not chosen ...", self.win) # label for showing name of chosen file
        self.file_text.setFont(QFont("Times", 14))
        self.file_text.adjustSize()
        self.file_text.move(500, 75)

        self.process_button = QPushButton(self.win) # button to activate processing function(model)
        self.process_button.setText("process")
        self.process_button.setFont(QFont("Times", 14))
        self.process_button.adjustSize()
        self.process_button.clicked.connect(self.process_func)
        self.process_button.move(350, 175)


        self.image_show = QLabel(self.win) #label that  shows the chosen image
        self.image_show.move(350, 175)

        self.image_result=QLabel(self.win) # label that shows image after model processing


        self.win.show() # activiting gui
        sys.exit(self.app.exec_())  # code for exiting gui when close is clicked

# function that runs when browse_button is clicked, opens fil
    def file_dialog(self):
        global file_save_path
        file, check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()", "")

        path = Path(file)
        file_save_path = file
        self.file_text.setText(path.name)
        pix=QPixmap(file)
        if pix.height()>350:
            pix =pix.scaled (pix.width(), 350, Qt.KeepAspectRatio, Qt.FastTransformation)
        if pix.width()>350:
            pix =pix.scaled (350, pix.height(), Qt.KeepAspectRatio, Qt.FastTransformation)

        self.image_show.setPixmap(pix)
        self.image_show.adjustSize()
        self.process_button.move(350,200+pix.height())

    def process_func(self):
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
        self.image_result.move(350, self.browse_button.height() + self.browse_button.y() + pix.height() + 200)

if __name__ == '__main__':
    g = Gui()
