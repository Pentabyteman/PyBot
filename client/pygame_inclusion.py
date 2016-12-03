from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
import pygame
import sys

class ImageWidget(QWidget):
    def __init__(self,surface,parent=None):
        super(ImageWidget,self).__init__(parent)
        w=surface.get_width()
        h=surface.get_height()
        self.data=surface.get_buffer().raw
        self.image=QImage(self.data,w,h, QImage.Format_RGB32)
        self.setFixedSize(w, h)

    def paintEvent(self,event):
        qp=QPainter()
        qp.begin(self)
        qp.drawImage(0,0,self.image)
        qp.end()


class MainWindow(QMainWindow):
    def __init__(self,surface,parent=None):
        super(MainWindow,self).__init__(parent)
        self.setCentralWidget(ImageWidget(surface))


pygame.init()
s=pygame.Surface((640,480))
s.fill((64,128,192,224))
pygame.draw.circle(s,(255,255,255,255),(100,100),50)

app=QApplication(sys.argv)
w=MainWindow(s)
w.show()
app.exec_()