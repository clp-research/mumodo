# mumodo
MUltiMOdal DOcument - import, analyze, plot and manage multimodal data

```
####################################################################
#                                                  __              #
#             ____ ___  __  ______ ___  ____  ____/ /___           #
#            / __ `__ \/ / / / __ `__ \/ __ \/ __  / __ \          #
#           / / / / / / /_/ / / / / / / /_/ / /_/ / /_/ /          #
#          /_/ /_/ /_/\__,_/_/ /_/ /_/\____/\__,_/\____/           #
#                                 Dialogue Systems Group           #
#                                 University of Bielefeld          #
#                                 www.dsg-bielefeld.de             #
####################################################################
```

Welcome to MUltiMOdal DOcuments (MUMODO), the multimodal data management, 
post-processing and analysis Python package. Mumodo is a piece of software
actively developed by the DSG (Dialogue Systems Group) in order to meet
ALL of (y)our multimodal analysis needs.
Mumodo makes extensive use of the Pandas library (http://pandas.pydata.org/) 
and its indexed tables (Dataframes); the IPython interpreter, as well as 
its html-based version, notebook; and Matplotlib, which mumodo uses for 
plotting. Other weak dependencies include moviepy to handle audio and video
files, as well as PIL (Python Image Library) to handle image data.

We recommend installing latest stable versions of IPython, Pandas, and 
Matplotlib in order to take advantage of all the newest features. 

In addition, mumodo makes use of the textgrid tools (tgt) package 
(https://github.com/hbuschme/TextGridTools), in order to import/export Praat
textgrids.

Since the running enviroment of mumodo is the Python interpreter, 
mumodo users have access to the wealth of libraries available for scientific 
computing in Python, while enjoying the flexibility of the Python programming 
language in their analysis workflows. In addition, the IPython-Matplotlib 
combo allows for inline plots and markup text to be input around the actual 
commands and expressions that consitute the analysis, essentially documenting 
the analysis "in place". This helps tremendously in sharing research work
and making it reproducible.

------------------------------------------------------------------------------
Mumodo Notebooks

The notebooks provided need to be loaded into an active IPython notebook 
session which is executed from a shell (Terminal in Mac OS or command prompt 
in Windows) as follows: 

ipython notebook

Demo notebooks distributed with mumodo can then be loaded from the IPython 
dashboard. These demo notebooks showcase the basic funcionality of the basic
mumodo packages. Their titles are self-explanatory and they contain instructions
within themselves.

Sample data

Some sample data is distributed with mumodo. This data is required in order to
run the demo notebooks. We recommend to move this data away from the 
installation directory to a folder in your "workspace" (see below).

-------------------------------------------------------------------------------
INSTALLATION

There are threeinstallation methods. The standard way is to use pip. 
Alternatively you can clone mumodo directly using git and either run a 
setup script, or copy files manually.

A. INSTALLATION WITH PIP

TODO: Register mumodo on PIP

B. INSTALLATION from git

1. Get mumodo by cloning this repository to your local HDD, to a location of
   your choice. 

2. Run the following command (You may need admin(root) permissions)

python setup.py install --install-data={directory}

{directory} is where the sample data and notebooks will go (your workspace)

NOTE: If you do not define the install-data variable, the sample data and 
      notebooks will be copied to an OS-dependent, default place, under a 
      folder called "mumodo". As this is less than ideal, we recommend you 
      setup a workspace directory at this time. Obvious choices are your home 
      folder, Documents folder, or a subfolder thereof

C. MANUAL INSTALLATION

1. Same as B.1

2. Add the "packages/" directory to your PYTHONPATH, or copy the 
   "mumodo" subfolder therein to your "site-packages" folder. A third 
   option is to use IPython profiles to add mumodo to the path via the 
   startup profile functionality (check IPython documentation)
3. Create a "workspace" directory on your local HDD. You can have several
   sub-folders therein for individual projects. Copy the demo notebooks and
   sample data into this workspace. The notebooks will work if the sampledata
   folder is in their directory.

4. Install the tgt package. Get it from
   https://github.com/hbuschme/TextGridTools, or simply do

     pip install tgt

   mumodo has been tested with version 1.02 of tgt
   
-------------------------------------------------------------------------------
USING MUMODO IN IPYTHON

Open a terminal, console (command prompt in windows), and go (cd) to your 
workspace (sub) directory, where you copied the notebooks and data, and run:

ipython notebook

The ipython dashboard should appear in your default webbrowser. 
Click on one of the demo noteboos to open it. A new tab should appear in the 
browser, that contains the new notebook. Check IPython documentation in order 
to get the basics of using IPython notebooks.

NOTE: The demo notebooks are not python scripts. You should not attempt to 
      run all the cells at once. Rather, run one cell at a time and see what 
      results it produces. 

NOTE: You should no longer use the "-pylab" and "inline" arguments when 
      starting ipython notebook, but rather follow the new guideline of 
      beginning each notebook with: 

     %matplotlib inline
     import numpy as np
     import matplotilb.pylab as plt
