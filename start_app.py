#!/usr/bin/env python
# start_app.py
import sys
from PyQt5.QtWidgets import QApplication
from main_window_pickapp import MainWindowPickApp


app = QApplication(sys.argv)   
MainWindowPickApp = MainWindowPickApp() 
MainWindowPickApp.show()   
rc = app.exec_()   
sys.exit(rc)
