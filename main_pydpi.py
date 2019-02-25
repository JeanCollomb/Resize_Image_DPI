# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

###############################################################################
import sys
from multiprocessing import cpu_count
from threading import Thread
from PIL import Image
from os import makedirs, listdir
from os.path import exists, normpath, dirname, getsize
from PyQt5.QtWidgets import QApplication, QMainWindow, qApp, QFileDialog
from interface import Ui_MainWindow               #changer nom du fichier et de la class Ui
###############################################################################


###############################################################################
class MainWindow(QMainWindow, Ui_MainWindow):     #changer le nom de la class Ui
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        qApp.installEventFilter(self)
        self.setupUi(self)
        
        
        # Liens a faire ici
        self.pushButton_selection_photos.clicked.connect(self.fct_selection_images)
        self.pushButton_selection_dossier_export.clicked.connect(self.fct_selection_dossier_export)
        self.pushButton_lancement_conversion.clicked.connect(self.lancement_conversion)
        self.actionQuitter.triggered.connect(qApp.quit)
        
        
        self.show()
###############################################################################
        
###############################################################################   
        # Fonctions associees aux liens crees ci-dessus
        
    def lancement_conversion(self):
        '''
        '''
        self.label_info_conversion.setText('Conversion en cours ...')
        self.progressBar.setValue(0)
        self.dpi = None
        self.dim_max = None
        self.label.repaint()
        try:
            self.fct_recuperation_donnees()
            try:
                self.fct_conversion()
            except:
                self.label_info_conversion.setText('Sélectionner des images')
                self.label.repaint()
        except ValueError:
            self.label_info_conversion.setText('Le DPI et la dimension max. doivent être des chiffres')
        except TypeError:
            self.label_info_conversion.setText('Le DPI et la dimension max. doivent être des chiffres')
        
    
    def fct_conversion(self):
        """
        Fonction pour convertir les images
        """
        
        if not exists(self.chemin_export):
            makedirs(self.chemin_export)
        
        if self.checkBox_multi_process.isChecked():
            CPU_NUMBER = cpu_count()
            
            if len(self.liste_images) > CPU_NUMBER:
                processes = []
                
                for processus in range(CPU_NUMBER):
                    file_per_processus = round(len(self.liste_images)/CPU_NUMBER)
                    
                    if processus == CPU_NUMBER-1:
                        files_list = self.liste_images[(processus * file_per_processus):]
                    else :
                        files_list = self.liste_images[processus * file_per_processus:(processus + 1) * file_per_processus]
                    print('CPU ', str(processus+1), ': {} pictures'.format(len(files_list)))
                    t = Thread(target=self.fct_redimensionnement_image, args = (files_list,))
                    processes.append(t)
                
                for t in processes:
                    t.start()
                for t in processes:
                    t.join()
            else:
                self.fct_redimensionnement_image(self.liste_images)
        else :
            self.fct_redimensionnement_image(self.liste_images)
        
        size_before = round(self.size(self.liste_images),1)
        size_after  = round(self.size(listdir(self.chemin_export), self.chemin_export),1)
        size_diff   = size_after - size_before
        gain        = round((100-size_after*100/size_before),1)
        self.label_info_conversion.setText('Tâche terminée ! Taille ini. : {}Mo ; Taille fin. : {}Mo ; Gain : {}%'.format(size_before, size_after, gain))
    

    def fct_selection_dossier_export(self):
        '''
        Fonction pour selectionner le dossier d'exportation
        '''
        pathToWallpaperDir = normpath(
            QFileDialog.getExistingDirectory(self))
        self.chemin_export = pathToWallpaperDir + '\export'
        

    def fct_selection_images(self):
        '''
        Fonction pour selectionner les images a convertir
        '''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileNames(self,"Choisir les images", 
                                                  "",
                                                  "All Files (*);;Images (*.png *.jpg *.bmp *.tiff)", 
                                                  options=options)
        nombre_images = len(fileName)
        self.liste_images = fileName
        self.chemin_courant = dirname(fileName[0])
        self.chemin_export = dirname(fileName[0]) + '\export'
        self.label_info_init.setText('{} images sélectionnées'.format(nombre_images))
        

    def fct_redimensionnement_image(self, files_list):
        '''
        Fonction pour redimensionner une image
        '''
        for idx, file in enumerate(files_list):
            self.label.repaint()
            image = Image.open(file)
            image_name = file.split('/')[-1]
            image_wo_extension = image_name.split('.')[0]
            self.fct_calcul_nouvelles_dimensions(self.dpi, self.dim_max)
            ratio       = self.dim_max_new / max(image.size[0], image.size[1])
            WIDTH_new  = int(image.size[0] * ratio)
            HEIGHT_new  = int(image.size[1] * ratio)
            image_new   = image.resize((WIDTH_new, HEIGHT_new), Image.ANTIALIAS)
            
            if self.checkBox_jpg.isChecked():
                image_new = image_new.convert('RGB')
                new_name = str(self.chemin_export) + '\\' + str(image_wo_extension) + '.jpg'
                image_new.save(new_name)
            if self.checkBox_pdf.isChecked():
                image_new = image_new.convert('RGB')
                new_name = str(self.chemin_export) + '\\' + str(image_wo_extension) + '.pdf'
                image_new.save(new_name)
            if self.checkBox_jpg.isChecked() == False and self.checkBox_pdf.isChecked() == False:
                image_new = image_new.convert('RGB')
                new_name = str(self.chemin_export) + '\\' + str(image_wo_extension) + '.jpg'
                image_new.save(new_name)
            
            if self.checkBox_multi_process.isChecked() :
                pass
            else:
                self.label_info_conversion.setText(new_name)
                avancement = idx*100/len(self.liste_images)
                self.progressBar.setValue(avancement)
        self.progressBar.setValue(100)


    def fct_recuperation_donnees(self):
        '''
        Fonction pour recuperer les donnees entrees par l'utilisateur
        '''
        self.dpi = int(self.lineEdit_DPI.text())
        self.dim_max = int(self.lineEdit_largeur.text())
        
        
    def fct_calcul_nouvelles_dimensions(self, dpi, dim_max):
        '''
        Fonction pour le calcul de la nouvelle dim_max de l'image
        '''
        self.dim_max_new = int((dpi * dim_max)/2.54)
        
    
    def size(self,list_file, path=None):
        '''
        '''
        if path == None:
            size = [getsize(list_file[i]) for i in range(len(list_file))]
        else :
            size = [getsize(str(path) + '\\' + list_file[i]) for i in range(len(list_file))]
        return sum(size)/(1024**2)

###############################################################################
    
###############################################################################   

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
#    test = TestClass()
    sys.exit(app.exec_())

###############################################################################