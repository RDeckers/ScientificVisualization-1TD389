Installation
====================

Python
--------------------
Managing Python packages on windows can be a bit of a pain.
luckily the people at Continiuum maintain a python distribution called Anaconda prepackaged with a lot of goodies, go to http://continuum.io/downloads and download it.
Make sure to download the python 2.7 version, as the VTK package does not yet support Python 3, and have Python added to your PATH (the installer does this by default).

vtk
--------------------
By default, Continiuum does not include the VTK package, but you can install it by opening a CMD window and typing
"conda install --name vtk" as per http://conda.pydata.org/docs/using/pkgs.html#install-a-package.

Taking it for a spin
====================
You should be all set now, so let's give it a try: 
*  Download http://www.uppmax.uu.se/docs/w/images/c/c8/HelloWorld.py (the rest of the tutorials can be found at http://www.uppmax.uu.se/docs/w/index.php/VTK_Tutorial)
*  Open the file with anaconda, by either
*    Simply double click it in explorer and when prompted select the python executable in your Anaconda installation folder,
*    or open a CMD window and the same folder as the file and type "python HelloWorld.py" 

Common Problems
===================
1.  I get the error "ImportError: No module named vtk".
*  Make sure you have ran "conda install --name vtk" succesfully and are using the anaconda version of Python, when you start a python shell it should say something like "Python 2.7.10 |Anaconda 2.3.0 (64-bit)| (default, May 28 2015, 16:44:52) [MSC v.1500 64 bit (AMD64)] on win32".
