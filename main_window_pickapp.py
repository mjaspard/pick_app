
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QSlider, QCheckBox, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout
from Ui_main_window_pickapp import Ui_MainWindow
from PyQt5.QtCore import pyqtSlot, QSize, pyqtSignal
# from Loader import Loader
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
import numpy as np
from osgeo import gdal
import pandas as pd
import shutil, os
from fct_display import *
import importlib






# Decorator to bypass function if data not loaded
def data_loaded(fonction):
	print("start deco")
	def check_dataset(self):
		if self.dataset:
			return fonction(self)
		else:
			self.label_SAR.setText("Please open a csv file before playing")
	return check_dataset


#===============================================================================================================
#===========================     SECONDARY  CLASS      ===================================================
#===============================================================================================================



class PopupDialog(QDialog):
	""" Opening a dialog box to enter manually edifice shape"""


	value_saved = pyqtSignal(str, str, str)
	def __init__(self):
		super().__init__()

		self.input1 = QLineEdit()
		self.input2 = QLineEdit()
		self.input3 = QLineEdit()
		self.save_button = QPushButton('Save')
		

		dict_param = LooadParametersFile('input_shape.py')
		self.input1.setText(dict_param['Rbase'])
		self.input2.setText(dict_param['Zbase'])
		self.input3.setText(dict_param['Zvolc'])

		layout = QVBoxLayout()
		layout.addWidget(QLabel('Base size [m]:'))
		layout.addWidget(self.input1)
		layout.addWidget(QLabel('Base altitude [m]:'))
		layout.addWidget(self.input2)
		layout.addWidget(QLabel('Summit altitude [m]:'))
		layout.addWidget(self.input3)
		layout.addWidget(self.save_button)

		self.save_button.clicked.connect(self.save_values)

		self.setLayout(layout)

	def save_values(self):
		value1 = self.input1.text()
		value2 = self.input2.text()
		value3 = self.input3.text()
		self.value_saved.emit(value1, value2, value3)
		self.close()


#===============================================================================================================
#====================    MAIN CLASS DECLARATION + POPUP CLASS ===========================================================
#===============================================================================================================


class MainWindowPickApp(QMainWindow,Ui_MainWindow):
	def __init__(self,parent=None): 
		super(MainWindowPickApp,self).__init__(parent) 
		self.setupUi(self)
		self.dataset = {}
		self.rm_canvas = False
		self.rm_canvas_view3d = False
		self.rm_canvas_profile = False
		self.rm_canvas_simampli = False
		self.rm_canvas_pickresults = False
		self.index_live = 0
		self.pick_SAR_index = 0
		self.pickSAR_activated = False
		self.SAR_zoom = False
		self.mem_date_pickplt = False
		self.toolbar = False
		self.updateSARFlag = False
		self.SAR_change.valueChanged.connect(lambda:  self.updateSAR_info())	# use a lambda to consume the unwanted argument
		self.SAR_change.sliderReleased.connect(lambda:  self.loadSAR())			# It is to manage decorator inside a class
		self.SAR_greyscale.sliderReleased.connect(lambda:  self.updateSAR())
		self.SAR_clip_max.sliderReleased.connect(lambda:  self.updateSAR())
		self.SAR_clip_min.sliderReleased.connect(lambda:  self.updateSAR())
		self.pushButton_SAR_left.clicked.connect(lambda:  self.decrementSAR())
		self.pushButton_SAR_right.clicked.connect(lambda:  self.incrementSAR())
		self.pushButton_ellipse.clicked.connect(lambda:  self.updateSAR())
		self.pushButton_filtered_SAR.clicked.connect(lambda:  self.updateSAR())
		self.pushButton_pick_SAR.clicked.connect(lambda:  self.pickSAR())
		self.frame_pickSAR.hide()
		self.pushButton_pickSAR_next.clicked.connect(lambda: self.pickSARNext())
		self.pushButton_pickSAR_previous.clicked.connect(lambda: self.pickSARPrev())
		self.pushButton_pickSAR_save.clicked.connect(lambda: self.pickSARSave())
		self.pushButton_update_simamp.clicked.connect(lambda:	self.initiateSimAmpliPlot())
		self.pushButton_ellipse_simamp.clicked.connect(lambda:	self.initiateSimAmpliPlot(init=False))
		self.pushButton_update_view3D.clicked.connect(lambda: self.initiateView3DPlot())
		self.pushButton_update_plotpicks.clicked.connect(lambda:  self.pickingResultsPlot())
		self.dateEdit_plotpicks_start.dateChanged.connect(lambda:  self.pickingResultsPlot(date_only=True))
		self.dateEdit_plotpicks_end.dateChanged.connect(lambda:  self.pickingResultsPlot(date_only=True))



		# manage menubar
		self.actionProfile.toggled.connect(self.dockWidget_profile.setVisible)
		self.action3d_view.toggled.connect(self.dockWidget_view3D.setVisible)
		self.actionSAR_image.toggled.connect(self.dockWidget_SARImage.setVisible)
		self.actionSimulated_amplitude.toggled.connect(self.dockWidget_SimAmp.setVisible)
		self.actionPlot_picking_results.toggled.connect(self.dockWidget_PlotPicks.setVisible)
		self.actionEdificeInput.toggled.connect(self.showInputData)
		
		# self.actionSimulated_amplitude.toggled.connect(lambda:  self.dockWidget_SimAmp.show())
		# self.actionSimulated_amplitude.toggled.connect(lambda:  self.dockWidget_SimAmp.raise_())
		# self.actionPlot_picking_results.toggled.connect(lambda:  self.dockWidget_PlotPicks.raise_())

		# manage active views
		self.dockWidget_SimAmp.setVisible(False)
		self.dockWidget_PlotPicks.setVisible(False)
		# Resize main window
		self.resize(1500, 500)

	# Decorator to bypass function if data not loaded
	def data_loaded(fonction):

		def check_dataset(self):
			if self.dataset:
				return fonction(self)
			else:
				self.label_SAR.setText("Please open a csv file before playing")
		return check_dataset

	
	def showInputData(self):
		""" This function will show a dialog box to enter manually the edifice input value.
		base_size = diameter size of the base of the edifice 
		base_alt = altitude of the base
		top_alt = altitude of the summit
		"""
		popup = PopupDialog()
		print(os.getcwd())
		popup.value_saved.connect(lambda v1, v2, v3: self.storeInputData(v1, v2, v3))
		# popup.value_saved.connect(self.storeInputData(v1, v2, v3))
		popup.exec_()

	def storeInputData(self, v1, v2, v3):
		"""This function will save the input data from popup when validated with save button into variable"""
		updateParametersFile('input_shape.py', 'Rbase', v1)
		updateParametersFile('input_shape.py', 'Zbase', v2)
		updateParametersFile('input_shape.py', 'Zvolc', v3)

		# reload new value
		input_shape = importlib.import_module('input_shape')
		input_shape = importlib.reload(input_shape)
		Zbase = input_shape.Zbase
		# Update graphics
		if self.dataset:
			self.updateSARPlot()



	@pyqtSlot()
	def on_action_Open_csv_triggered(self):
		""" Function that open csv file and write data into a dictionary
			Then, display the first image of the file
			"""
		(self.csv_file,filtre) = QFileDialog.getOpenFileName(self,"Open CSV File", filter="(*.csv)")

		# if csv_file:
		# 	QMessageBox.information(self,"TRACE", "Fichier à ouvrir:\n\n%s"%csv_file)

		# Load data into a dict
		# self.dataset = Loader(self.csv_file).images_data
		self.dataset = csv_to_dict(self.csv_file)
		self.image_number = len(self.dataset['folder'])
		# Manage horizontal slider directly dependant of number of datas
		self.SAR_change.setMaximum(self.image_number - 1)
		self.SAR_change.setTickPosition(QSlider.TicksBelow)
		self.SAR_change.setTickInterval(1)
		# Activate pushButton Ellipse
		self.pushButton_ellipse.setEnabled(True)
		self.pushButton_ellipse_simamp.setEnabled(True)
		self.pushButton_filtered_SAR.setEnabled(True)
		self.pushButton_pick_SAR.setEnabled(True)

		self.initiateSARPlot()


	# def closeEvent(self,event):
	# 	messageConfirmation = "Êtes-vous sûr de vouloir quitter Pick App ?"
	# 	reponse = QMessageBox.question(self,"Confirmation",messageConfirmation,QMessageBox.Yes,QMessageBox.No) 
	# 	if reponse == QMessageBox.Yes:
	# 		event.accept() 
	# 	else:
	# 		event.ignore()


#===============================================================================================================
#====================     SAR AMPLITUDE IMAGE  IMAGE ===========================================================
#===============================================================================================================


	def initiateSARPlot(self):
		""" Function that display the image from the dataset at the index
			1: Reterive the figure object from "getSARFig function"
			2: Add this to the layout "SARLayout" !!! Layout need to be added to the QWidget
			"""

		# Close current figure if it exists:
		print(" initiate sar plot")
		if self.rm_canvas:
			print("-- remove canvas")
			self.canvas.close()

			if self.toolbar:
				self.toolbar.close()


		# Get matplotlib figure objetct and min/max value of amplitude image
		# self.SAR_clip_min.setValue(int(self.SAR_clip_min.minimum()))
		# self.SAR_clip_max.setValue(int(self.SAR_clip_max.maximum()))
		self.canvas = getSARFig(self)
		self.SAR_greyscale.setValue(int((self.dataset['expo_greyscale'][self.index_live])*100))
		# Add figure to layout properties of SARImage Widget
		self.SARLayout.addWidget(self.canvas)
		# Draw the figure
		self.canvas.draw()
		# Create a tool bar
		if self.pickSAR_activated:
			self.toolbar = NavigationToolbar(self.canvas, self.SARImage, coordinates=True)
			self.SARLayout.addWidget(self.toolbar)

		# Display crater profile
		self.initiateProfilePlot()
		
		# Update 3d view if selected
		if self.checkBox_auto_update_view3D.isChecked():
		    self.initiateView3DPlot()
		else:
		    self.pushButton_update_view3D.setChecked(True)

		# Update simulted amplitude view if selected
		if self.checkBox_auto_update_simamp.isChecked():
		    self.initiateSimAmpliPlot()
		else:
		    self.pushButton_update_simamp.setChecked(True)

		# Update picking results plot is selected
		if self.checkBox_auto_update_plotpicks.isChecked():
		    self.pickingResultsPlot()
		else:
		    self.pushButton_update_plotpicks.setChecked(True)
		

		# Set variable tp allow removing canvas after first creation
		self.rm_canvas = True
		# Re-initialise picking ellipse counter
		self.pick_SAR_index = 0
		# Reinitialise zoom memorisation and memorise original one
		self.SAR_zoom = False
		self.lim_x_or = self.ax.get_xlim()
		self.lim_y_or = self.ax.get_ylim()
		# Display name of first point to pick
		self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))


	def updateSARPlot(self):
		""" Function that display the image from the dataset at the index
			1: Reterive the figure object from "getSARFig function"
			2: Add this to the layout "SARLayout" !!! Layout need to be added to the QWidget
			3: we do not set clip min/max  
			"""
		# print("update sar plot")
		self.canvas.close()
		if self.toolbar:
			self.toolbar.close()
		self.dataset['expo_greyscale'][self.index_live] = self.SAR_greyscale.value()/100
		self.canvas = getSARFig(self)
		
		# Add figure to layout properties of SARImage Widget
		self.SARLayout.addWidget(self.canvas)
		# Draw the figure
		self.canvas.draw()
		# Create a tool bar
		self.toolbar = NavigationToolbar(self.canvas, self.SARImage, coordinates=True)
		self.SARLayout.addWidget(self.toolbar)

		# Update Profile 
		self.updateProfilePlt()

		# Update 3d view if selected
		if self.checkBox_auto_update_view3D.isChecked():
		    self.initiateView3DPlot()
		else:
		    self.pushButton_update_view3D.setChecked(True)

		# Update simulted amplitude view if selected
		if self.checkBox_auto_update_simamp.isChecked():
		    self.initiateSimAmpliPlot()
		else:
		    self.pushButton_update_simamp.setChecked(True)

		# Update picking results plot is selected
		if self.checkBox_auto_update_plotpicks.isChecked():
		    self.pickingResultsPlot()
		else:
		    self.pushButton_update_plotpicks.setChecked(True)


	@data_loaded
	def loadSAR(self):
		print("on_SAR_change_changed")
		self.updateSARFlag = False
		self.index_live = self.SAR_change.value()
		self.SAR_greyscale.setValue(int((self.dataset['expo_greyscale'][self.index_live])*100))
		self.initiateSARPlot()

	@data_loaded
	def updateSAR(self):
		print("updateSAR request")
		self.updateSARFlag = True
		self.updateSARPlot()

	@data_loaded
	def updateSAR_info(self):
		""" Write SAR image info that will be displayed on the current slider position"""
		self.index_hold = self.SAR_change.value()
		img_dir = self.dataset['folder'][self.index_hold]
		satname = img_dir.split('/')[-2]
		img_date_string = self.dataset['day'][self.index_hold]
		text = "{} : {}".format(img_date_string, satname)
		self.label_SAR.setText(text)


	@data_loaded
	def decrementSAR(self):
		self.index_live += -1
		self.index_live = np.clip(self.index_live, 0 , (self.image_number -1))
		self.label_SAR_index.setText(str(self.index_live))
		self.SAR_change.setValue(int(self.index_live))
		self.initiateSARPlot()


	@data_loaded
	def incrementSAR(self):
		# print("on_pushButton_SAR_right_clicked")
		self.index_live += 1
		self.index_live = np.clip(self.index_live, 0 , (self.image_number - 1))
		self.label_SAR_index.setText(str(self.index_live))
		self.SAR_change.setValue(int(self.index_live))
		self.initiateSARPlot()

	@data_loaded
	def pickSAR(self):
		# print("pickSAR")
		if self.pushButton_pick_SAR.isChecked():
			self.frame_pickSAR.show()
			self.pushButton_ellipse.setChecked(True)
			self.updateSARPlot()
			# Activate variable to use in the pickingManagement function
			self.pickSAR_activated = True
			# Display the next points to pick in the label of picking frame panel
			self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))
		else:
			self.frame_pickSAR.hide()
			self.pickSAR_activated = False


	def pickSARNext(self):
		self.pick_SAR_index += 1
		self.pick_SAR_index = np.clip(self.pick_SAR_index, 0 , 9)
		self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))
		# pickSARManagement(self)

	def pickSARPrev(self):
		self.pick_SAR_index += -1
		self.pick_SAR_index = np.clip(self.pick_SAR_index, 0 , 9)
		self.label_pickSAR_PtsToPick.setText(getPointNameFromIndex(self.pick_SAR_index))
		# pickSARManagement(self)

	def pickSARSave(self):
		print("save to csv file last modification")
		df = pd.DataFrame.from_dict(self.dataset)
		df.to_csv(self.csv_file, index=False)
		print("--> New values has been saved to csv")
		csv_file_out_tmp = self.csv_file + '_pick_tmp.csv'
		csv_file_out = self.csv_file + '_pick_results.csv'
		shutil.copyfile(csv_file_out_tmp, csv_file_out)
		print("--> csv file for plotting picking results is updated ")

		self.pushButton_pickSAR_save.setChecked(False)
		self.pickSARNext()

     

#===============================================================================================================
#====================     PROFILE OF CRATER          ===========================================================
#===============================================================================================================


	def initiateProfilePlot(self):
			""" Function that display the image from the dataset at the index
				1: Reterive the figure object from "getSARFig function"
				2: Add this to the layout "SARLayout" !!! Layout need to be added to the QWidget
				"""

			# Close current figure if it exists:
			print(" initiate sar plot")
			if self.rm_canvas:
				self.canvas_profile.close()
				self.toolbar_profile.close()
				print("-- remove canvas profile")
				# self.canvas_profile.close()



			# Get matplotlib figure objetct and min/max value of amplitude image
			self.canvas_profile = getProfileFig(self)

			# Create tool bar
			self.toolbar_profile = NavigationToolbar(self.canvas_profile, self.ProfilePlt, coordinates=True)

			# Add figure to layout properties of ProfilePlt Widget
			self.Profile_Layout.addWidget(self.canvas_profile)
			self.Profile_Layout.addWidget(self.toolbar_profile)
			# Draw the figure
			self.canvas_profile.draw()

			# Run script to convert ellipse data points to geo-data (Rayon, altitude...) 
			create_csv_tmp(self)


	def updateProfilePlt(self):
			""" Function that display the image from the dataset at the index
				1: Reterive the figure object from "getSARFig function"
				2: Add this to the layout "SARLayout" !!! Layout need to be added to the QWidget
				3: we do not set clip min/max  
				"""
			print("update sar plot")
			self.canvas_profile.close()
			self.toolbar_profile.close()
			# Get matplotlib figure objetct and min/max value of amplitude image
			self.canvas_profile = getProfileFig(self)

			# Create tool bar
			self.toolbar_profile = NavigationToolbar(self.canvas_profile, self.ProfilePlt, coordinates=True)

			# Add figure to layout properties of ProfilePlt Widget
			self.Profile_Layout.addWidget(self.canvas_profile)
			self.Profile_Layout.addWidget(self.toolbar_profile)
			# Draw the figure
			self.canvas_profile.draw()

			# Run script to convert ellipse data points to geo-data (Rayon, altitude...) 
			create_csv_tmp(self)

#===============================================================================================================
#=================================   3D VIEW      ==============================================================
#===============================================================================================================


	def initiateView3DPlot(self):
			""" Function that display the image from the dataset at the index
				1: Reterive the figure object from "getSARFig function"
				2: Add this to the layout "SARLayout" !!! Layout need to be added to the QWidget
				"""

			# Close current figure if it exists:
			print(" initiate View 3D plot")
			if self.rm_canvas_view3d:
				self.canvas_view3d.close()
				self.toolbar_view3d.close()


			self.rm_canvas_view3d = True
			# Get matplotlib figure objetct and min/max value of amplitude image
			self.canvas_view3d = getView3dFig(self)
			# Create tool bar
			self.toolbar_view3d = NavigationToolbar(self.canvas_view3d, self.view3DPlt, coordinates=True)


			self.View3D_Layout.addWidget(self.canvas_view3d)
			self.View3D_Layout.addWidget(self.toolbar_view3d)
			# Draw the figure
			self.canvas_view3d.draw()


#===============================================================================================================
#===========================    SIMULATED AMPLITUDE IMAGE  ===================================================
#===============================================================================================================


	def initiateSimAmpliPlot(self, init=True):
		""" Function that display the simulated amplitude image
			1: Execute "Writecsv_picking_results.py" to get the necessary data
			2: Call 
			2: Add this to the layout "SARLayout" !!! Layout need to be added to the QWidget
			"""

		# Close current figure if it exists:
		print(" initiate amplitude simulation plot")
		if self.rm_canvas_simampli:
			self.canvas_sim_ampli.close()
			self.toolbar_sim_ampli.close()

		self.rm_canvas_simampli = True

		# Run script to convert ellipse data points to geo-data (Rayon, altitude...) 
		create_csv_tmp(self)


		# Get matplotlib figure objetct and min/max value of amplitude image
		self.canvas_sim_ampli = getSimAmpliFig(self, init)
		# Create tool bar
		self.toolbar_sim_ampli = NavigationToolbar(self.canvas_sim_ampli, self.SimAmpPlt, coordinates=True)

		# Add object to layout
		self.SimAmp_Layout.addWidget(self.canvas_sim_ampli)
		self.SimAmp_Layout.addWidget(self.toolbar_sim_ampli)
		# Draw the figure
		self.canvas_sim_ampli.draw()



#===============================================================================================================
#===========================    Plot Picking results  ===================================================
#===============================================================================================================


	def pickingResultsPlot(self, date_only=False):
		""" Function that display the picking results plot
			1: Execute "Writecsv_picking_results.py" to get the necessary data
			2: Call 
			2: Add this to the layout "PickResultsayout" !!! Layout need to be added to the QWidget
			"""

		# stop the function when the automatic modification of dateEdit object run the functuin
		if (date_only and not self.rm_canvas_pickresults):
			return

		# Close current figure if it exists:
		print("run pickingResultsPlot")
		print("self.rm_canvas_pickresults = ", self.rm_canvas_pickresults)
		if self.rm_canvas_pickresults:
			self.canvas_pickresults.close()
			self.toolbar_pickresults.close()



		# Run script to convert ellipse data points to geo-data (Rayon, altitude...) 
		create_csv_tmp(self)

		# Get matplotlib figure objetct and min/max value of amplitude image
		self.canvas_pickresults = getPickingResultsFig(self, date_only)
		# Create tool bar
		self.toolbar_pickresults = NavigationToolbar(self.canvas_pickresults, self.PickResultsPlt, coordinates=True)

		# Add object to layout
		self.PickResults_Layout.addWidget(self.canvas_pickresults)
		self.PickResults_Layout.addWidget(self.toolbar_pickresults)
		# Draw the figure
		self.canvas_pickresults.draw()

		# set flaf to true
		self.rm_canvas_pickresults = True






