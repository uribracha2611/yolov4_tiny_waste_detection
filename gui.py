import os

import cv2
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot, QThread, QObject, pyqtSignal, QMutex, QUrl, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PIL import Image
import sys
from pathlib import Path
from tensorflow_functions import predict
import time


# threading to stop the application from freezing when process browse_button is clicked
class Worker(QThread):
    image_path = pyqtSignal(str)  # object that signal when the thread is done, and returns the image_path for the gui

    def __init__(self, parent=None):
        self._mutex = QMutex()  # QMutex is used to prevent mutation of the data used by the thread

        super().__init__()  # calling Qthread __init__()
    # function that runs the Thread and calls the predict function
    def run(self):
        self._mutex.lock()  # locking the data
        img = Image.open(file_save_path)  ## opning the image
        if not Path("saves").exists():
            os.mkdir("saves")  # creating save folder if it doesn't exist

        img_path_for_pred = Path("saves/" + time.strftime("%Y%m%d-%H%M%S") + ".jpg")  # crating path for save
        img.save(str(img_path_for_pred))  # saving

        img_path_for_show = predict(
            str(img_path_for_pred))  # calling prediction function see tensorflow_function code part
        self.image_path.emit(img_path_for_show)  # telling the gui the code is done

        self.finished.emit()  # QThread requires this line
        self._mutex.unlock()  # unlocking the data used by the thread
# thread for video showing during browse
class worker_video_browse(QThread):
    changePixmap = pyqtSignal(QImage) #signal for each frame

    def run(self):
        cap = cv2.VideoCapture(file_save_path)  # getting video
        ret, frame = cap.read()  # reading frames
        while ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # changing frame to image
                h, w, ch = rgbImage.shape # data of shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888) #reformatting
                p = convertToQtFormat.scaled(350, 350, Qt.KeepAspectRatio) #changing size of frame
                self.changePixmap.emit(p) #sending frame to gui
                QApplication.processEvents()
                ret, frame = cap.read()
        self.stop()
    def stop(self):
        self.threadactive = False
        self.wait()
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
        self.win.setGeometry(200, 200, 1200, 1200)
        width, height = self.win.frameGeometry().width(), self.win.frameGeometry().height()
        self.win.setWindowTitle("School project Uri Bracha-Gui app")
        self.worker = Worker()
        self.worker_video_browse=worker_video_browse()
        self.title = QLabel(self.win)  # title of the project
        self.title.setFont(QFont("Times", 14, QFont.Bold))
        self.title.setText("School project Uri Bracha-Gui app")
        self.title.adjustSize()
        self.title.move((width // 4) + 50, 0)

        self.chosen_image_name = QLabel(self.win)  # chosen_image_name for showing chosen image name
        self.chosen_image_name.setFont(QFont("Times", 14))
        self.chosen_image_name.setText("choose an image to process:")
        self.chosen_image_name.move(50, 75)
        self.chosen_image_name.adjustSize()

        self.browse_button = QPushButton(self.win)  # browse_button to allow browsing
        self.browse_button.setText("Browse..")
        self.browse_button.setFont(QFont("Times", 14))
        self.browse_button.adjustSize()
        self.browse_button.move(350, 75)
        self.browse_button.clicked.connect(self.file_dialog)

        self.file_text = QLabel(" file not chosen ...", self.win)  # label for showing name of chosen file
        self.file_text.setFont(QFont("Times", 14))
        self.file_text.adjustSize()
        self.file_text.move(500, 75)

        self.process_button = QPushButton(self.win)  # button to activate processing function(model)
        self.process_button.setText("process")
        self.process_button.setFont(QFont("Times", 14))
        self.process_button.adjustSize()
        self.process_button.clicked.connect(self.process_func)
        self.process_button.move(350, 175)

        self.image_show = QLabel(self.win)  # label that  shows the chosen image
        self.image_show.move(350, 175)

        self.image_result = QLabel(self.win)  # label that shows image after model processing

        self.win.show()  # activating gui
        sys.exit(self.app.exec_())  # code for exiting gui when close is clicked

    # function that runs when browse_button is clicked, opens file dialog for choosing image file
    # takes the file and shows the image on the gui
    def file_dialog(self):
        global file_save_path  # this variable keeps the file path to the chosen image,
        # it is global becuase it is used in Worker class
        file, check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()", "")  # opens file dialog

        path = Path(file)
        file_save_path = file  # sets the global variable
        self.file_text.setText(path.name)  # sets the label
        if path.suffix !=".avi" and path.suffix!=".mp4": #checks that file  is not video
            pix = QPixmap(file)  # create map of pixels for use in label
            # height and width regularization for pixel map
            if pix.height() > 350:
                pix = pix.scaled(pix.width(), 350, Qt.KeepAspectRatio, Qt.FastTransformation)
            if pix.width() > 350:
                pix = pix.scaled(350, pix.height(), Qt.KeepAspectRatio, Qt.FastTransformation)

            self.image_show.setPixmap(pix)  # sets label to map
            self.image_show.adjustSize()
        else:
            if self.worker_video_browse.isRunning():
                self.worker_video_browse.stop()
            # moves the button so it isn't covered
            self.process_button.move(350, 600)
            self.worker_video_browse.changePixmap.connect(self.show_browse_video)
            self.worker_video_browse.run()



    # function that runs when the process button is clicked, it's only is use is activating the thread
    def process_func(self):
        self.worker.image_path.connect(self.edit_image)  # sets the function that is run after the processing is done
        self.worker.start()  # starts the running of the thread

    # function that shows the image with the bounding boxes in gui, file_image_path is the path to the new image
    def edit_image(self, file_image_path):
        pix = QPixmap(file_image_path)  # creates pixel map from path
        # height and width regularization for pixel map
        if pix.height() > 350:
            pix = pix.scaled(pix.width(), 350, Qt.KeepAspectRatio, Qt.FastTransformation)
        if pix.width() > 350:
            pix = pix.scaled(350, pix.height(), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.image_result.setPixmap(pix) #sets the image to the label
        self.image_result.adjustSize()
        self.image_result.move(350, self.browse_button.height() + self.browse_button.y() + pix.height() + 200)
        #moving it so it doesn't cover other things
    #showing video during browse
    def show_browse_video(self,image):
        self.image_show.setPixmap(QPixmap.fromImage(image)) #sets the label to each frame as they come
        self.image_show.adjustSize()
if __name__ == '__main__':
    g = Gui()
