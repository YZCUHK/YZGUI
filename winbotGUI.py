import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QFileDialog
from winbotdesign import Ui_MainWindow
import serial
from time import sleep
import glv
import cv2
import threading
import random

class mwindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(mwindow, self).__init__()
        self.setupUi(self)
        glv.camcount = 0
        glv.serclc_flag = 1
        glv.distance = ''
        glv.force = ''

# function for communication
    def ps_bt(self):
        try:
            glv.serwcr = serial.Serial('/dev/usb_communicate', 57600, timeout=0.5)
            self.textBrowser.append('port %s, baudrate %s' % (glv.serwcr.port, glv.serwcr.baudrate))
            if glv.serwcr.isOpen() == 1:
                self.textBrowser.append('%s' % ('communication done!'))
            glv.serwcr.ropevel = 2000
            glv.serwcr.ropepos = 200000
            glv.serwcr.camposv = 130
            glv.serwcr.camposh = 100
        except Exception as e:
            QMessageBox.information(self, 'Warning', 'communication failure, check your'
                                                     ' connection')


# open camera
    def ps_bt2(self):
        try:
            glv.camcount = glv.camcount+1
            if (glv.camcount % 2) != 0:
                glv.cap = cv2.VideoCapture(1)  # if the picture is wrong, change parameter to 0,1,2 etc.
                while True:
                    ret, frame = glv.cap.read()
                    cv2.imshow("window viewer", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    if (glv.camcount % 2) == 0:
                        break
                glv.cap.release()
                cv2.destroyAllWindows()
        except Exception:
            QMessageBox.information(self, 'Warning', 'communication failure, check your'
                                                     ' connection')

# open cleaning unit,i.e.sewage pump,roller brush and clean pump
    def ps_bt3(self):
        glv.serwcr.write('ngd')
        self.textBrowser.append('%s' % 'sewage pump RUN')
        sleep(0.5)
        glv.serwcr.write('lgd')
        self.textBrowser.append('%s' % 'brush RUN')
        sleep(0.5)
        glv.serwcr.write('mgd')
        self.textBrowser.append('%s' % 'clean pump RUN')
        sleep(0.5)

# close cleaning unit,i.e.sewage pump,roller brush and clean pump
    def ps_bt4(self):
        glv.serwcr.write('mkd')
        self.textBrowser.append('%s' % 'clean pump STOP')
        sleep(0.5)
        glv.serwcr.write('lkd')
        self.textBrowser.append('%s' % 'brush STOP')
        sleep(0.5)
        glv.serwcr.write('nkd')
        self.textBrowser.append('%s' % 'sewage pump STOP')
        sleep(0.5)

# climb up the rope
    def ps_bt5(self):
        tempstr = '%se%sfogd' % (str(glv.serwcr.ropevel), str(glv.serwcr.ropepos))
        glv.serwcr.write(tempstr)
        self.textBrowser.append('%s' % 'climbing UP')
        self.textBrowser.append('vel: %s pos: %s' % (glv.serwcr.ropevel, glv.serwcr.ropepos))
        sleep(0.5)

# climb down the rope
    def ps_bt6(self):
        tempstr = '%se%sfohd' % (str(glv.serwcr.ropevel), str(glv.serwcr.ropepos))
        glv.serwcr.write(tempstr)
        self.textBrowser.append('%s' % 'climbing DOWN')
        self.textBrowser.append('vel: %s pos: %s' % (glv.serwcr.ropevel, glv.serwcr.ropepos))
        sleep(0.5)

    def ps_bt7(self):
        if self.lineEdit.text() != '':
            if (int(self.lineEdit.text()) >= 1000) and (int(self.lineEdit.text()) <= 3000):
                glv.serwcr.ropevel = self.lineEdit.text()
                self.textBrowser.append('vel: %s successfully set' % glv.serwcr.ropevel)
            else:
                QMessageBox.about(self, 'attention', 'velocity should be between 1000 and 3000')
        sleep(0.5)

    def ps_bt8(self):
        if self.lineEdit.text() != '':
            if (int(self.lineEdit.text()) >= 50000) and (int(self.lineEdit.text()) <= 200000):
                glv.serwcr.ropepos = self.lineEdit.text()
                self.textBrowser.append('pos: %s successfully set' % glv.serwcr.ropepos)
            else:
                QMessageBox.about(self, 'attention', 'position should be between 50000 and 200000')
        sleep(0.5)

    def ps_bt9(self):
        self.textBrowser.clear()

    def timer_sensor(self):
        if glv.serclc_flag % 2 == 0:
            temp1 = glv.serclc.readline()
            print(temp1)
            temp2 = glv.serclc.readline()
            print(temp2)
            if len(temp1) >= 2:
                if temp1[1] == 'u':
                    glv.distance = filter(str.isdigit, temp1)
                    glv.force = filter(str.isdigit, temp2)
                if temp1[1] == 't':
                    glv.distance = filter(str.isdigit, temp2)
                    glv.force = filter(str.isdigit, temp1)
            self.label_4.setText('%s' % str(glv.distance))
            self.label_6.setText('%s' % str(glv.force))
            glv.timer1 = threading.Timer(0.2, glv.w.timer_sensor)
            glv.timer1.start()
            glv.serclc.flushInput()
            glv.serclc.flushOutput()
#            print ('total threading number {}' .format(threading.activeCount()))

# data collection
    def ps_bt11(self):
        glv.serclc_flag = glv.serclc_flag+1
        try:
            if glv.serclc_flag % 2 == 0:
                glv.serclc = serial.Serial('/dev/usb_collection', 57600, timeout=0.5)
                self.textBrowser.append('port %s, baudrate %s' % (glv.serclc.port, glv.serclc.baudrate))
                if glv.serclc.isOpen() == 1:
                    self.textBrowser.append('%s' % ('collection start!'))
                self.label_4.setText('%s' % '')
                self.label_6.setText('%s' % '')
                glv.timer1 = threading.Timer(0.2, glv.w.timer_sensor)
                glv.timer1.start()
        except Exception as e:
            QMessageBox.information(self, 'Warning', 'communication failure, check your'
                                                     ' connection')

    def changevaluecampitch(self, value):
        glv.serwcr.camposh = str(value+100)
        self.textBrowser.append('pitch: %s' % glv.serwcr.camposh)

    def cammotion_pitch(self):
        tempstr = '%sfqgd' % str(glv.serwcr.camposh)
        glv.serwcr.write(tempstr)
        self.textBrowser.append('%s' % tempstr)

    def changevaluecamyaw(self, value):
        glv.serwcr.camposv = str(value+80)
        self.textBrowser.append('pitch: %s' % glv.serwcr.camposv)

    def cammotion_yaw(self):
        tempstr = '%sfpgd' % str(glv.serwcr.camposv)
        glv.serwcr.write(tempstr)
        self.textBrowser.append('%s' % tempstr)

    def sendsercommand(self):
        tempstr =self.lineEdit_2.text()
        glv.serwcr.write(tempstr)
        self.textBrowser.append('%s' % tempstr)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    glv.w = mwindow()
    glv.w.pushButton.clicked.connect(glv.w.ps_bt)
    glv.w.pushButton_2.clicked.connect(glv.w.ps_bt2)
    glv.w.pushButton_3.clicked.connect(glv.w.ps_bt3)
    glv.w.pushButton_4.clicked.connect(glv.w.ps_bt4)
    glv.w.pushButton_5.clicked.connect(glv.w.ps_bt5)
    glv.w.pushButton_6.clicked.connect(glv.w.ps_bt6)
    glv.w.pushButton_7.clicked.connect(glv.w.ps_bt7)
    glv.w.pushButton_8.clicked.connect(glv.w.ps_bt8)
    glv.w.pushButton_9.clicked.connect(glv.w.ps_bt9)
    glv.w.pushButton_10.clicked.connect(glv.w.cammotion_pitch)
    glv.w.pushButton_11.clicked.connect(glv.w.ps_bt11)
    glv.w.pushButton_12.clicked.connect(glv.w.cammotion_yaw)
    glv.w.pushButton_13.clicked.connect(glv.w.sendsercommand)
    glv.w.horizontalSlider.valueChanged[int].connect(glv.w.changevaluecampitch)
    glv.w.horizontalSlider_2.valueChanged[int].connect(glv.w.changevaluecamyaw)
    glv.w.show()
    sys.exit(app.exec_())