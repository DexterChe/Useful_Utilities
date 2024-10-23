"""
Created on 2023-05-03
Author: @Dmitry_Chezganov

File history:
05/06/2023: V2. Added check if the file was already trimmed to skip it.
06/06/2023: V2.1. Added check if the log file exists with message box to overwrite it or not.
05/09/2023: v3. Added option to trim images in the folder without subfolders.

Script will read all images in the folder and trim out black area around the usefull information.
0. Make logger
1. Ask user to select folder with images
2. Iterate all images in the folder
3. Open the image
4. Get the size of the image
5. Find the top-left corner of the useful part of the image
6. Crop the image to the useful part
7. Save the trimmed image
"""

from PIL import Image
from tkinter.filedialog import askopenfilename, askdirectory
import logging
import os
import tkinter as tk
import argparse
import numpy as np
from tkinter import messagebox

def get_args():
    parser = argparse.ArgumentParser(description='The script creates folders according to predefined structure')
    parser.add_argument('-l', '--log', help='Log file', default=True)
    parser.add_argument('-v', '--verbose', help='Verbose mode', action='store_true', default=True)
    parser.add_argument('-d', '--debug', help='Debug mode', action='store_true')
    parser.add_argument('-f', '--force', help='Force mode', action='store_true')
    args = parser.parse_args()
    return args

def get_logger(log_file, verbose, debug):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    if verbose:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    if debug:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

# function to read image files and trim out black area around the usefull information
def trim_image(logger, file_name, image_file, path_to_save):
    # check if the file name contains the word 'trimmed'
    if 'trimmed' in file_name:
        # if the file name contains the word 'trimmed' and force mode is not activated, skip the file
        # if not args.force:
        logger.info('File {} already trimmed. Skipping.'.format(file_name))
        # return
        # if the file name contains the word 'trimmed' and force mode is activated, remove the word 'trimmed' from the file name
        # else:
        #     file_name = file_name.replace('_trimmed', '')
        #     logger.info('File {} already trimmed. Overwriting.'.format(file_name))
    else:

        # Open the image
        image = Image.open(image_file)
        im_arra = np.array(image)
        logger.info('Image {} opened'.format(image_file))
        logger.info('Shape of the image array is {}'.format(im_arra.shape))

        # Get the size of the image
        width, height = image.size
        logger.info('Image size is {}x{}'.format(width, height))

        # Find the top and bottom edges of the useful part of the image
        top, bottom = 0, height
        for y in range(height):
            if not all(image.getpixel((x, y)) == (0, 0, 0) for x in range(width)):
                top = y
                break
        for y in range(height - 1, -1, -1):
            if not all(image.getpixel((x, y)) == (0, 0, 0) for x in range(width)):
                bottom = y + 1
                break

        # Find the left and right edges of the useful part of the image
        left, right = 0, width
        for x in range(width):
            if not all(image.getpixel((x, y)) == (0, 0, 0) for y in range(top, bottom)):
                left = x
                break
        for x in range(width - 1, -1, -1):
            if not all(image.getpixel((x, y)) == (0, 0, 0) for y in range(top, bottom)):
                right = x + 1
                break

        # Crop the image to the useful part
        image = image.crop((left, top, right, bottom))
        logger.info('Size of cropped image is {}x{}'.format(right-left, bottom-top))
        logger.info('Image {} cropped'.format(image_file))
        
        # plot the image
        image.show()
        
        # Save the trimmed image
        path2save = os.path.join(path_to_save, file_name.split('.')[0]+'_trimmed_image.png')
        image.save(path2save, format='png')
        #close the image
        image.close()
        logger.info('Image {} saved'.format(path2save))

def main():
    # ask user interactively to indicate where the folder with the images is
    root = tk.Tk()
    # make the window open on top
    root.attributes('-topmost', True)
    root.withdraw()  # hide tkinter window
    directory_path = askdirectory(title='Select folder with images')
    if not directory_path:  # if user cancels directory selection, exit script
        print('Directory selection cancelled. Exiting script.')
        exit()
    # set the path to the log file
    log_file = os.path.join(directory_path, 'log.txt')

    # # check if log file exists
    # if os.path.exists(log_file):
    #     overwrite = askdirectory(title='File Exists', message='The log file already exists. Do you want to overwrite it?')
    #     if not overwrite:
    #         print('Log file selection cancelled. Exiting script.')
    #         exit()
    # check if log file exists
    if os.path.exists(log_file):
        overwrite = messagebox.askyesno(title='File Exists', message='The log file already exists. Do you want to overwrite it?')
        # overwrite = filedialog.askdirectory(title='File Exists', message='The log file already exists. Do you want to overwrite it?')
        if not overwrite:
            print('Log file selection cancelled. Exiting script.')
            exit()
    
            
    # create logger
    args = get_args()
    logger = get_logger(log_file, args.verbose, args.debug)
    
    logger.info('Script started')
    logger.info('Input folder: {}'.format(directory_path))
    logger.info('Output folder: {}'.format(directory_path))
    logger.info('Log file: {}'.format(log_file))
    logger.info('Verbose mode: {}'.format(args.verbose))
    logger.info('Debug mode: {}'.format(args.debug))
    logger.info('Force mode: {}'.format(args.force))

    # go through all folders in the directory and return the list of folder paths
    folders = [f.path for f in os.scandir(directory_path) if f.is_dir()]
    #sort folders
    folders.sort()
    logger.info('List of {} folders found in the directory:\n {}'.format(len(folders), folders))
    # interate over all folders in the directory
    # check of the folder list is not empty
    if folders:
        for folder in folders:

            #list all files in the directory that has image format
            image_files = [f for f in os.listdir(folder) if f.endswith('.png') or f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.bmp') or f.endswith('.gif') or f.endswith('.tiff') or f.endswith('.tif')]
            #sort the list of files
            image_files.sort()
            logger.info('List of {} images found in the folder:\n {}'.format(len(image_files), image_files))


            # # interate over all images in file folder
            for filename in image_files:
            #     # print(filename)
            #     # Open the image
                trim_image(logger,
                        file_name=filename,
                        image_file=os.path.join(folder, filename), 
                        path_to_save=folder
                        )
    else:
        image_files = [f for f in os.listdir(directory_path) if f.endswith('.png') or f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.bmp') or f.endswith('.gif') or f.endswith('.tiff') or f.endswith('.tif')]
        #sort the list of files
        image_files.sort()
        logger.info('List of {} images found in the folder:\n {}'.format(len(image_files), image_files))

        # # interate over all images in file folder
        for filename in image_files:
            trim_image(logger,
                    file_name=filename,
                    image_file=os.path.join(directory_path, filename), 
                    path_to_save=directory_path
                    )

    logger.info('Script finished')

if __name__ == '__main__':
    main()


