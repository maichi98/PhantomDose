import os 
import sys
import subprocess
import json

from PySide6.QtWidgets import QApplication,QLabel,QTableWidgetItem, QTableWidget,QTabWidget, QWidget,QPushButton, QHeaderView, QVBoxLayout,QScrollBar, QHBoxLayout, QSizePolicy, QLineEdit, QTreeWidget,QGridLayout,QTreeView, QFileSystemModel, QApplication, QMenu, QAbstractItemView
from PySide6.QtCore import *
from PySide6.QtGui import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas

import pyqtgraph.opengl as gl
import pyqtgraph as pg

from PySide6 import QtGui
from ScatterPlotWindowPh import ScatterPlotWindow
import numpy as np
#import pptk
import win32gui
import sys
from TreePh import TreePh
from PhantomTreePh import PhantomTreePh
from Phasync.Loop import Loop
from PptkPH import PptkPh
import win32.lib.win32con as win32con
import generate_phantom as traitement_ph
from ErrorMessage import ErrorMessage
import src.create_dicom_from_OOF_numpy as ext_convert
import src.compute_DVH as dvh
import src.constant as ext_const





class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        try :
            os.chdir("../")
            path_phantom = os.environ["PHANTOMLIB_PATH"] = os.getcwd() + os.path.join("/Phandose_pyside/PhantomLib")
            os.environ["PATH_SUB_PYTHON"] = os.path.join(os.getcwd() + "/venv/Scripts/python")
            is_path = os.path.exists(path_phantom)
            if not is_path : raise ValueError
        except:
            path_error = ErrorMessage()
            message_wrong_path = f"path : '{path_phantom}' doesn't exist"
            path_error.raise_error_message(message_wrong_path)
            #-------TODO Set a properly ErrorMessage 
            return
        
        
        #Trigger False then script 6 load phantom 
        self.update_model = False
        
        self.path_phantom = os.environ.get("PHANTOMLIB_PATH")
        self.windowcontainer = ""

        """initialize window"""
        self.setWindowTitle("Phandose")
        # self.setWindowFlags(Qt.FramelessWindowHint) """this line is for remove the flag or the title bar"""

        self.setMinimumWidth(1920)
        self.setMinimumHeight(1080)
        # self.setWindowState(self.windowState() ^ Qt.WindowFullScreen)
        self.setStyleSheet("""QWidget{background-color : #1C2625;} 
                             
                           QPushButton:hover
                            {
                                background-color: #48DEDC;
                                color:#F9F4E3;
                            
                            }
                           QPushButton:pressed
                           {
                            background-color: #F9F4E3;
                            color:#1C2625;
                           
                           }
                           QPushButton
                           {
                            border-radius: 10px;
                                        background-color: #2ACFCD;
                                        font-family: inter;
                                        font-weight: bold;
                                        font-size : 20px;
                                        color:#F9F4E3;
                           }
                           QWindow
                           {
                           background : #253130;
                           }

                           
                           QScrollBar:vertical {
                                border: none;
                                background: rgb(46, 62, 60);
                                width: 30px;
                                border-radius: 0px;
                                margin-right:5px;
                                margin-bot:15px;
                           
                            }

                            /*  HANDLE BAR VERTICAL */
                            QScrollBar::handle:vertical {	
                                background-color: rgb(28, 38, 37);
                                min-height: 30px;
                                border-radius: 2px;
                           
                            }
                            QScrollBar::handle:vertical:hover{	
                                background-color: rgb(16, 12, 14);
                            }
                            

                            /* BTN TOP - SCROLLBAR */
                            QScrollBar::sub-line:vertical {
                                border: none;
                                background: rgb(46, 62, 60);
                                height: 0px;
                                subcontrol-position: top;
                                subcontrol-origin: margin;
                            }
                            

                            /* BTN BOTTOM - SCROLLBAR */
                            QScrollBar::add-line:vertical {
                                border: none;
                                background: rgb(46, 62, 60);
                                height: 0px;
                                subcontrol-position: bottom;
                                subcontrol-origin: margin;
                            }
                            /* RESET ARROW */
                            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                                background: none;
                            }
                            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                                background: none;
                            }



                            /* HORIZONTAL SCROLLBAR - */
                            QScrollBar:horizontal {
                                border: none;
                                background: rgb(46, 62, 60);
                                width : 15px;
                                height: 30px;
                                border-radius: 0px;
                                margin-bottom:5px;
                                margin-right:15px;
                            
                            }
                            QScrollBar::handle:horizontal {
                                background-color: rgb(28, 38, 37);
                                min-height: 30px;
                                border-radius: 2.3px;
                            }
                            QScrollBar::add-line:horizontal {
                                background: rgb(46, 62, 60);
                                height: 0px;
                                subcontrol-position: right;
                                subcontrol-origin: margin;
                            }
                            QScrollBar::sub-line:horizontal {
                                border: none;
                                background: rgb(46, 62, 60);
                                height: 0px;
                                
                                subcontrol-position: left;
                                subcontrol-origin: margin;
                            }
                            QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal
                            {
                                background: none;

                            }
                            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
                            {
                                background: none;
                            }
                           QTabWidget::pane { border: 0; }
                           
                           QTabWidget::tab-bar {
                           
                           }
                            /* Style the tab using the tab sub-control. Note that
                                it reads QTabBar _not_ QTabWidget */
                            QTabBar::tab {
                                background-color: #2E3E3C;
                           
                                width: 145px;
                                height: 40px;
                           
                                min-width: 8ex;
                                font-family: inter;
                                font-weight: bold;
                                font-size: 15px;
                                color:#F9F4E3;
                                background-color: #253130;

                            }

                            QTabBar::tab:selected, QTabBar::tab:hover {
                           
                                background-color: #2E3E3C;
                           
                                

                           
                            }

                            QTabBar::tab:selected {
                                background-color: #2E3E3C;
                            }

                            QTabBar::tab:!selected {
                               
                            }
                           
                           QHeaderView::section {
                                border:solid;
                                background: #283735;
                                color: #54726f;
                                padding: 2px;
                                font-size: 12pt;
                                border-style: none;
                                border-right: none;
                           
                            }
                           QTableCornerButton::section {
                                background-color: #1c2625;
                            }
                           
                           """)
          

        """
        -------- Search part ---------

        - search_box is a color rectangle to wrap the search widget
        - search_widget is a widget for research patient
            TODO : Make script for link name of patient to index patient into the list
        
        
        """
        search_box = QLabel(self)
        search_box.setGeometry(35,24,505,44)
        search_box.setStyleSheet("""
                                  border-radius:10px;
                                  background-color: #253130;
                                  """) 
        self.search_widget = QLineEdit(self)
        self.search_widget.setPlaceholderText("Chercher un patient...")
        self.search_widget.setGeometry(41,30,493,32)
        self.search_widget.setStyleSheet("""border-radius: 10px;
                                    background-color: #2E3E3C;
                                    padding-top:3px;
                                    padding-left:10px;
                                    font-family: inter;
                                    /*font-weight: bold;*/
                                    color:#F9F4E3;
                                 """)
        

        """
        -------- Selection part ---------

        - self._selection_box is a color rectangle to wrap the self._pre_visualization_box and
          patient/phantom tree widget
            
        - Phantom_tree_widget is a widget for research patient
        
        """
        self._selection_box = QLabel(self)
        self._selection_box.setGeometry(35,80,800,860)
        self._selection_box.setStyleSheet("""
                                  border-radius:10px;
                                  background-color: #253130;
                                  """) 
        self._pre_visualization_box = QLabel(self)
        self._pre_visualization_box.setGeometry(550,100,270,820)
        self._pre_visualization_box.setStyleSheet("""
                                  border-radius:10px;
                                  background-color: #2E3E3C;
                                  """) 
        self._visualization_box = QLabel(self)
        self._visualization_box.setGeometry(850,80,900,860)
        self._visualization_box.setStyleSheet("""
                                  border-radius:10px;
                                  background-color: #253130;
                                  """) 
        self._tab_visualization = QTabWidget(self)
        self._tab_visualization.setGeometry(870,100,860,820)
        self._tab_visualization.setStyleSheet("""
                                  border-radius:10px;
                                  border-top-left-radius : 0px;
                                  background-color: #2E3E3C;
                                  border-style: solid
                                  """) 

        
        # Premier onglet avec un tableau
        tab1 = QWidget()
        
        # Deuxième onglet avec une vue Open3D
        self.tab2 = QWidget()
        
        
        self._tab_visualization.addTab(tab1, "Open3D")
        self._tab_visualization.addTab(self.tab2, "Tableau")


        self._patient_text = QLabel("Patients",self)
        self._patient_text.setGeometry(65,110,200,20)
        self._patient_text.setStyleSheet("""
                                   background-color: #253130;
                                   font-family: inter;
                                   font-weight: bold;
                                   font-size: 18px;
                                   color:#F9F4E3;
                                  """) 
        self._phantom_text = QLabel("Phantom",self)
        self._phantom_text.setGeometry(300,110,200,20)
        self._phantom_text.setStyleSheet("""
                                   background-color: #253130;
                                   font-family: inter;
                                   font-weight: bold;
                                   font-size: 18px;
                                   color:#F9F4E3;
                                  """) 
        """
        -------- Selection part ---------
            
        - Phantom_tree_widget is a widget to display lirbrairie of phantom 
        - Patient_tree_widget is a widget to load patient with (DIcom, Nii, Dose)
            TODO : faire une class de vérification 
        
        """
        self.patient_tree_widget = TreePh(self)
        self.patient_tree_widget.setHeaderHidden(True)
        self.patient_tree_widget.setGeometry(55,140,230,720)
        self.phantom_tree_widget = PhantomTreePh(self)
        self.phantom_tree_widget.setHeaderHidden(True)
        self.phantom_tree_widget.setGeometry(290,140,230,720)

        self.patient_tree_widget.acceptDrops()
        style_patient_phantom =  """border-radius: 10px;
                                 display:flex;
                                 background-color: #2E3E3C;
                                 padding-top : 20px;
                                 padding-left : 20px;
                                 font-family: inter;
                                 /*font-weight: bold;*/
                                 font-size : 12px;
                                 color:#F9F4E3; 
                                 border-image: url(none.png); 
                                 
                                 """

        """
        -------- run part ---------

        
        """
        self._run_button = QPushButton('Run', self)
        self.tree_view = TreePh()
        # self.setStyleSheet("""
        #                    QPushButton:hover
        #                    {
        #                     background: yellow;
        #                    }
        #                    """)
        self._run_button.setGeometry(370,880,150,35)
        self._run_button.clicked.connect(self.tree_view.getChoice)
        self._run_button.clicked.connect(self.run_visualization)

        self.patient_tree_widget.setStyleSheet(style_patient_phantom)
        self.phantom_tree_widget.setStyleSheet(style_patient_phantom)
       
        self.model_phantom = QFileSystemModel()
        self.model_phantom.setRootPath(QDir.currentPath())

        self.phantom_tree_widget.setModel(self.model_phantom)
        self.phantom_tree_widget.setRootIndex(self.model_phantom.index(self.path_phantom))
        self.phantom_tree_widget.clicked.connect(lambda index: self.tree_view.item_clicked(index, "phantom"))
        self.patient_tree_widget.clicked.connect(lambda index: self.tree_view.item_clicked(index, "patient"))

        
        
        """
        ------------Hide contents of floder(date, weight...)------------------
        """
        self.patient_tree_widget.setIndentation(10)
        self.phantom_tree_widget.setIndentation(10)
        self.patient_tree_widget.setColumnHidden(1, True)  
        self.patient_tree_widget.setColumnHidden(2, True)  
        self.patient_tree_widget.setColumnHidden(3, True)  

        self.phantom_tree_widget.setColumnHidden(1, True)  
        self.phantom_tree_widget.setColumnHidden(2, True)  
        self.phantom_tree_widget.setColumnHidden(3, True)  
        
        self.phantom_tree_widget.setColumnWidth(0, 300) 
        self.patient_tree_widget.setColumnWidth(0, 300)

     

        """
        ---------------- TAB VIEW part -------------
        """
        
        self._tab_visualization

        self.model_phantom.setReadOnly(True)
        # self.phantom_preview = ScatterPlotWindow().broke()



       





        
        # TODO Mettre le prévisualisation -----------------------------------------------------------------------------------------
     
        # coord = PptkPh("D:/01-developpement/Pj - PHANDOSE/02-Ibrahima_code/FROM_IDIALLO_20232710/PATIENTS/RS_213_/AIDREAM_213_BRADEL_MARIA_FATIMA_201208550DW.txt")

        # # Créer des données de points aléatoires
        # pos = coord.get_extarnal_contour()[0] # -> XYZ Coordinate
        # color = coord.get_extarnal_contour()[1] # -> RGB color 
        # print(coord.get_extarnal_contour()[1])

        # # color = np.random.rand(len(pos), 4)
        
        # size = np.random.rand(len(pos)) * 0.0002

        # # Créer la fenêtre principale et le widget OpenGL
        
        
        # # self.view = QGraphicsView()
        # # layout.addWidget(self.view)
        # self.plot_widget = gl.GLViewWidget()

        # wid = QWidget(self)
        # self.search_layout = QHBoxLayout(wid)
        # self.search_layout.addWidget(self.plot_widget)
        # self.plot_widget.setFixedSize(60,150 )


        # # Créer le nuage de points
        # scatter = gl.GLScatterPlotItem(pos=np.asarray(pos), size=size, color=np.asarray(color), pxMode=False)
        # self.plot_widget.addItem(scatter)

        # TODO Mettre le prévisualisation ------------------------------------------------------------------------------------------------



        
        # self.testst = QWidget()
        # self.graphWidget = pg.PlotWidget(self)
        # self.graphWidget.setGeometry(570,120,230,150)

        # hour = [1,2,3,4,5,6,7,8,9,10]
        # temperature = [30,32,34,32,33,31,29,32,35,45]

        # # plot data: x, y values
        # self.graphWidget.plot(hour, temperature, temperature)



      

    #     self.canvas = FigureCanvas(Figure( facecolor=(0,0,0,0), frameon=False,))
        
    #     self.plt = self.canvas.figure.add_subplot(projection='3d')
    #     # self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    #     self.canvas.setParent(self)
    #     self.update_plot()
    #     self.canvas.setGeometry(570,120,230,550)
    #     self.canvas.setStyleSheet("""border-radius:10px;
    #                               background-color: #253130;
    #                               """)

    # def update_plot(self):
    #     self.plt.clear()
    #     self.plt.scatter(np.random.randn(3000), np.random.randn(3000), np.random.randn(3000),s=0.01, c='orange')
    #     self.plt.set_facecolor("#2E3E3C")
    #     self.plt.grid(False)
    #     self.plt.axis('off')
    #     self.canvas.draw()



    
        # tab_widget = QTabWidget(self)
        # tab_widget.setGeometry(870,100,860,820)
        # self.onglet_1 = QWidget()
        # self.onglet_2 = QWidget()
        # tab_widget.addTab(self.onglet_1, "Onglet 1")
        # tab_widget.addTab(self.onglet_2, "Onglet 2")

        
   
    def rebuild_phantom_tree(self):
        print("dedans")

        with open("list_phantom.json", "r") as f:
                phantom_list = json.load(f)
        for currenDir, dirnames, filenames_ph in os.walk(os.environ.get("PHANTOMLIB_PATH")):
            
            for filename in filenames_ph:
                print(filename)
                print(type(filename))

                if filename in phantom_list['phantom_list']:
                    print("gooooooo")
                    print(filename)
                else:
                    print("dedans")
                    filenamePath = os.path.join(os.environ.get("PHANTOMLIB_PATH") + f"/{filename}")
                    fileId = self.model_phantom.index(filenamePath)
                    self.phantom_tree_widget.setRowHidden(fileId.row(), fileId.parent(), True)         
                                         

    
    def find_pptk_window(self):
        hwnd = win32gui.FindWindowEx(0, 0, None, "viewer")
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

        
        self.window = QtGui.QWindow.fromWinId(hwnd)
        self.windowcontainer = self.createWindowContainer(self.window, self)
        # self.onglet_1(self.windowcontainer)
        
        self.windowcontainer.setGeometry(870,100,860,820)
        self.windowcontainer.frameSize()
        self.windowcontainer.show()
        print("--> Fenêtre récupéré")

    def run_visualization(self):
        
        # self.tree_view.get_patient_clqqked()
        # self.tree_view.get_phantom_clicked()
        # traitement_ph.run_pre_traitement(self)
        # self._path = traitement_ph.get_final_path()
        
        
        event_loop = Loop()
        
        # STEP 1 - resume script 6 for create phantom for all choice
        event_loop.schedule(self._resume_process())
        event_loop.run_until_empty()
        
        #STEP 2 - Script to calculate remote dose
        # event_loop.schedule(self._calculation_remote_dose(tuple(), tuple()))
        # event_loop.run_until_empty()

        # STEP 3 - Script to convert remote dose numpy output to dicom  
        # patient_path = os.environ.get('PATIENT_PATH')
        self.patient_path = "H:/05-pipeline/src/Test_data_pipeline/aidream_path"
        self.oof_path = "H:/05-pipeline/src/Test_data_pipeline/oof_path"
        self.patient_id = "AIDREAM_222"

        event_loop.schedule(self._numpy_to_dicom(self.patient_path, self.oof_path))
        event_loop.run_until_empty()

        # STEP 4 - script to extract dvh values  
    


        event_loop.schedule(self._load_tab())
        event_loop.run_until_empty()
        

        # event_loop.schedule(self._load_view())
        # event_loop.run_until_empty()

        # ppt = PptkPh(self._path)
        # event_loop.schedule(ppt.run_window())
        # event_loop.run_until_empty()
        # try:
        #     self.find_pptk_window()
        # except Exception as e:
        #     print(e)
        

        # event_loop.run_until_complete(ppt.run_window())

    def resizeEvent(self, event):
        """
        Whenever the window is resized, the windowcontainer is resized as well

        """
        size = self.size()  # Récupérer la taille actuelle du widget
        

        #mw = MainWindow
        mw_width = size.width()
        mw_height = size.height()
        # self.windowcontainer.resize()

        self._visualization_box.resize(mw_width - 1022, mw_height -220)

        
        if self.windowcontainer in globals():
            size_container = self.windowcontainer
            size_container.resize(mw_width - 1062, mw_height -260)
            print(mw_height)
            print(mw_width)
        size.height()
    


        # for filname in phantom_list['phantom_list']:
        #     filenamePath = os.path.join(os.environ.get("PHANTOMLIB_PATH") + f"/{filname}")
        #     print(os.environ.get("PHANTOMLIB_PATH"))
        #     print(filname)
        #     print(f"filename path : {filenamePath}")
        #     fileId = self.new_model_phantom.index(filenamePath)
            
        #     self.phantom_tree_widget.setRowHidden(fileId.row(), fileId.parent(), False)
           

            # self.phantom_tree_widget.model.index(filenamePath)

        # self.phantom_tree_widget.setModel(self.new_model_phantom)
        print("CHECK")
        print("CHECK")
        print("CHECK")
        print("CHECK")
        print("CHANGE MODEL OF TREE")
    
    def _resume_process(self):
        print("resume")
        print("resume")
        print("resume")
        print("resume")
        with open("pause_signal.txt", "w") as f:
            f.write("resume")

    def _calculation_remote_dose(self, whole_body:any, dose:any) -> list:
        pass

    def _numpy_to_dicom(self, path_patient:str, path_remote_dose:str, registration_method:str="ants_resampling", with_plot=False):
        print("numpy to dicom")
        
        try:
            ext_convert.main(path_patient, path_remote_dose, registration_method, with_plot)
        except Exception as e:
            path_error = ErrorMessage()
            path_error.raise_error_message(str(e))

    def _dvh_histogram(self, structure_names_list, patient_id, aidream_path, oof_path, tab=False):
        try:
            result_dvh = dvh.dvh_plot_one_patients_all_structure(structure_names_list, patient_id, aidream_path, oof_path, tab)
            return result_dvh
        except Exception as e:
            path_error = ErrorMessage()
            path_error.raise_error_message(str(e))
    
    def _refractor_dvh(self):
        
        dvh_by_structure = []
        structure_names_list = ext_const.STRUCTURE_NAMES_LIST

        dvh_output = self._dvh_histogram(structure_names_list, self.patient_id, self.patient_path, self.patient_path+"/"+self.patient_id, True)
        
        for structure in dvh_output:
            volume = structure.volume            
            name = structure.name
            max_dose = structure.max
            min_dose = structure.min
            mean_dose = structure.mean
            d100 = structure.D100
            d98 = structure.D98
            d95 = structure.D95
            d2cc = structure.D2cc

            dvh_json = {
                "name" : name,
                "volume": volume,
                "max_dose" : max_dose,
                "min_dose" : min_dose,
                "mean_dose" : mean_dose,
                "d100" : str(d100),
                "d98" : str(d98),
                "d95" : str(d95),
                "d2cc" : str(d2cc),
            }
            dvh_by_structure.append(dvh_json)

        return dvh_by_structure
        
    def _load_tab(self):
        dvh_json_result = self._refractor_dvh()
        self._create_table(self.tab2, dvh_json_result)
    
    def _create_table(self, tab, dvh_json: list):
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        table_w = QTableWidget()
        table_w.setStyleSheet(
                    "background-color: #253130;"
                    "border: solid ;"
                    "color: #4181C0;"
                    "selection-background-color: #4181C0;"
                    "selection-color: #FFF;"
                    "color:#F9F4E3;"
                    

                    )
        table_w.setColumnCount(9)
        table_w.setRowCount(len(dvh_json))
        table_w.setHorizontalHeaderLabels(["Name",
                                         "Volume",
                                         "Max_dose",
                                         "Min_dose",
                                         "Mean_dose",
                                         "D100",
                                         "D98",
                                         "D95",
                                         "D2cc"])
        



        for y in range(len(dvh_json)):
            # each_elem_json = [i for i in range(len(dvh_json))]
            
            print(f"name ---{dvh_json[y]['name']}")
            print(f"volume --{dvh_json[y]['volume']}")
            print(f"max -- {dvh_json[y]['max_dose']}")
            print(f"min -- {dvh_json[y]['min_dose']}")
            print(f"min -- {dvh_json[y]['mean_dose']}")
            print(f"d100 ---{dvh_json[y]['d100']}")
            print(f"d98  ---{dvh_json[y]['d98']}")
            print(f"d95   ----{dvh_json[y]['d95']}")
            print(f"d2cc  ---{dvh_json[y]['d2cc']}")

            name_j = QTableWidgetItem(dvh_json[y]['name'])
            volume_j = QTableWidgetItem(str(dvh_json[y]['volume']))
            max_j = QTableWidgetItem(str(dvh_json[y]['max_dose']))
            min_j = QTableWidgetItem(str(dvh_json[y]['min_dose']))
            mean_j = QTableWidgetItem(str(dvh_json[y]['mean_dose']))
            d100_j = QTableWidgetItem(dvh_json[y]['d100'])
            d98_j = QTableWidgetItem(dvh_json[y]['d98'])
            d95_j = QTableWidgetItem(dvh_json[y]['d95'])
            d2cc_j =QTableWidgetItem(dvh_json[y]['d2cc'])

            table_w.setItem(y, 0, name_j)
            table_w.setItem(y, 1, volume_j)
            table_w.setItem(y, 2, max_j)
            table_w.setItem(y, 3, min_j)
            table_w.setItem(y, 4, mean_j)
            table_w.setItem(y, 5, d100_j)
            table_w.setItem(y, 6, d98_j)
            table_w.setItem(y, 7, d95_j)
            table_w.setItem(y, 8, d2cc_j)





                # for value  in dvh_json[x].values():
                #     # print(f"keyyyyyyyyyyyyyyyy{key}")
                #     print(f"valuuuuuuuuuuuuuuuuue{value}")
                #     # 9 is the number of headers fields 
                # item = QTableWidgetItem(value)
                # table.setItem(y, x, item)

                    # dvh_json[number]["Name"],
                    # dvh_json[number]["Volume"],
                    # dvh_json[number]["Max_dose"],
                    # dvh_json[number]["Min_dose"],
                    # dvh_json[number]["Mean_dose"],
                    # dvh_json[number]["D100"],
                    # dvh_json[number]["D98"],
                    # dvh_json[number]["D95"],
                    # dvh_json[number]["D2cc"]
        
        layout.addWidget(table_w)



app = QApplication(sys.argv)
demo = MainWindow()
demo.show()
app.exec()