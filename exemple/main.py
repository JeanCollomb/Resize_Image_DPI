# -*- coding: utf-8 -*-
"""
Author: Jean COLLOMB
"""

from time import time
from PIL import Image
from os import getcwd, listdir, makedirs
from os.path import isfile, join, splitext, exists, getsize
from multiprocessing import freeze_support, cpu_count
from threading import Thread

# Allowed extensions
extensions      = ['JPG', 'PNG', 'BMP', 'TIFF']
CPU_NUMBER = cpu_count()

# Get informations
print('---------------------------------')
print('          --> Input <--          ')
while True:
    try:
        DPI = float(input('DPI target value (300 for print): '))
        break
    except ValueError:
        print('Wrong format! It should be a number.')

while True:
    try:
        WIDTH_document = float(input('Document width in cm (21 for A4): '))
        break
    except ValueError:
        print('Wrong format! It should be a number.')

while True:
    try:
        EXT_file = str(input('Which extension do you want? (jpg, pdf, both): '))
        if EXT_file == 'jpg' or EXT_file == 'pdf' or EXT_file == 'both':
            break
        else:
            print('Please, you should choose one of the three options.')
    except ValueError:
        print('Wrong format! It should be a string.')

print('# Info: ', CPU_NUMBER, 'CPU are available')

while True:
    try:
        MULTIPROCESS = str(input('Multi-processing (y/n): '))
        if MULTIPROCESS.lower() == 'y':
            break
        elif MULTIPROCESS.lower() == 'n' or MULTIPROCESS.lower() == 'no':
            break
        else:
            print('Please, you should choose one of the two options.')
    except ValueError:
        print('Wrong format! It should be a string.')

print('---------------------------------')
print('   --> Work in progress... <--   ')

# Calculate new properties
# DPI = 2.54 * nbpixel / size en cm
initial_time    = time()
WIDTH_new       = int((DPI * WIDTH_document)/2.54)

# list of files
folder          = getcwd()
files_all       = listdir(folder)
files = []
for file in files_all:
    f_text, f_ext= splitext(file)
    if f_ext[1:].upper() in extensions:
        files.append(file)

# export folder creation
EXPORT_FOLDER   = folder + '\light_pictures'
if not exists(EXPORT_FOLDER):
    makedirs(EXPORT_FOLDER)

# resizing function
def file_resizing(files_list):
    '''
    '''
    for idx, file in enumerate(files_list):
        if isfile(join(folder,file)):
            f_text, f_ext= splitext(file)          
            f_ext = f_ext[1:].upper()
            
            if f_ext in extensions:
                NEW_NAME_JPG = f_text + '.jpg'
                NEW_NAME_PDF = f_text + '.pdf'
                
                image = Image.open(join(folder,file))
                ratio           = WIDTH_new / image.size[0]
                HEIGHT_new      = int(image.size[1] * ratio)
                
                image_new       = image.resize((WIDTH_new, HEIGHT_new), Image.ANTIALIAS)
                if EXT_file.lower() == 'jpg':
                    if image_new.mode != 'RGB':
                        image_new = image_new.convert('RGB')
                    image_new.save(join(EXPORT_FOLDER,NEW_NAME_JPG))
                    print('File ', NEW_NAME_JPG, ': Done !')
                elif EXT_file.lower() == 'pdf':
                    image_new.save(join(EXPORT_FOLDER,NEW_NAME_PDF))
                    print('File ', NEW_NAME_PDF, ': Done !')
                elif EXT_file.lower() == 'both':
                    if image_new.mode != 'RGB':
                        image_new = image_new.convert('RGB')
                    image_new.save(join(EXPORT_FOLDER,NEW_NAME_PDF))
                    image_new.save(join(EXPORT_FOLDER,NEW_NAME_JPG))
                    print('File ', NEW_NAME_PDF, ': Done !')
                    print('File ', NEW_NAME_JPG, ': Done !') 
                else:
                    print('Wrong extension asked. Conversion in jpg.')
                    if image_new.mode != 'RGB':
                        image_new = image_new.convert('RGB')
                    image_new.save(join(EXPORT_FOLDER,NEW_NAME_JPG))
                    print('File ', NEW_NAME_JPG, ': Done !')
    return

def size(list_file, path=None):
    '''
    '''
    if path == None:
        size = [getsize(list_file[i]) for i in range(len(list_file))]
    else:
        size = [getsize(str(path) + list_file[i]) for i in range(len(list_file))]
    return sum(size)/(1024**2)

if __name__ == "__main__":
    freeze_support()
    # function execution
    if MULTIPROCESS.lower() == 'n' or MULTIPROCESS.lower() == 'no':
        file_resizing(files)
    elif MULTIPROCESS.lower() == 'y' or MULTIPROCESS.lower() == 'yes':
        if len(files) > CPU_NUMBER:
            processes = []
            for processus in range(CPU_NUMBER):
                file_per_processus = round(len(files)/CPU_NUMBER)
                if processus == CPU_NUMBER-1:
                    files_list = files[(processus * file_per_processus):]
                else :
                    files_list = files[processus * file_per_processus:(processus + 1) * file_per_processus]
                print('CPU ', str(processus+1), ': {} pictures'.format(len(files_list)))
                t = Thread(target=file_resizing, args = (files_list,))
                processes.append(t)
            for t in processes:
                t.start()
            for t in processes:
                t.join()
        else:
            file_resizing(files)
    else :
        print('Not a good answer. Quit...')
final_time    = time()

print('---------------------------------')
print('       --> Program end <--       ')
print('Conversion time (s): ', round(final_time - initial_time,1))
size_before = size(files)
size_after  = size(listdir(EXPORT_FOLDER), path="light_pictures\\")
print('Initial size (Mo): ', round(size_before,1))
print('final size (Mo): ', round(size_after,1))
print('Gain (Mo): ', round(size_before - size_after,1), '<-->', round((100-size_after*100/size_before),1),'% gain')
