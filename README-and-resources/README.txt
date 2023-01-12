Welcome to the README for AQUADA-GUI.

This program is a graphical user interface (GUI) for AQUADA (Automated quantification of damages in composite wind turbine blades). It allows for users to analyze their thermal images by croping, creating binary damages masks, and quantifying the damage growth. 

============
Installation
============

AQUADA GUI is combined with python and all the necessary packages into one application. This consists of the 'aquada-gui' folder, whiich contains many files. These are listed below, but the one to focus on is 'aquada-gui.exe'. To run the GUI, simply click on this file, and it will run. To find this file more easily, you can create a shortcut to it by right clicking on 'aquada-gui.exe'. This shortcut can then be kept in a convenient location. 

============
LICENSE
============
MIT License

Copyright © 2023 Technical University of Denmark, Department of Wind and Energy Systems
For full license text, see license.txt

============
Important Notes
============
This program will ONLY work with a Windows operating system. Video files must be in .wmv format, and images must be .png. 
Thermography video files should also be in a color pallette where lighter colors are hotter, in order to generate meaningful results.

============
Resources
============
files.txt: This is a list of the whole directory that should be present when running the AQUADA GUI
demo.mp4: Shows the full damage detection process using AQUADA GUI
test-video-one.wmv: A lab test thermographic video, which can be analyzed with AQUADA GUI
test-video-two.wmv: Annother test video which is ready to be analyzed with AQUADA GUI

============
Acknowledgements
============
AQUADA-GUI was developed at The Technical University of Denmark by Max Spencer, with funding provided by the Fulbright Program. 
Computer vision analysis code is based on the work of Shohreh Sheiati. Work was supervised by Xiao Chen.  

The TKVideo package is used and modified under the mit liscence https://mit-license.org/ https://pypi.org/project/tkVideo/

Additional packages used include:
PyInstaller https://pyinstaller.org/en/stable/
tkinter https://docs.python.org/3/library/tkinter.html
pillow https://python-pillow.org/
cv2 https://pypi.org/project/cv2module/
pandas https://pandas.pydata.org/
numpy https://numpy.org/
matplotlib https://matplotlib.org/
imutils https://pypi.org/project/imutils/
scipy https://scipy.org/


