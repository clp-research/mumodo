#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MUltiMOdal DOcument - Dialogue Systems Group, University of Bielefeld

# The MIT License (MIT)
#
# Copyright (c) 2015

# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
# IN THE SOFTWARE.

from os import system
from distutils.core import setup

setup(
    name='mumodo',
    description='mumodo - MUltiMOdal DOcument. Import, analyse, plot and' + \
                ' manage multimodal data',
    version='2.0',
    package_dir={'':'packages'},
    packages=['mumodo'],
    data_files=[('mumodo_examples/notebooks', 
                 ['notebooks/BasicDataTypes.ipynb',
                  'notebooks/BasicIO.ipynb',
                  'notebooks/ComputingOffset.ipynb',
                  'notebooks/DoingAnalysisWithMumodo.ipynb',
                  'notebooks/ManagingCorporaAndResourcesWithMumodo.ipynb',
                  'notebooks/PlottingFunctions.ipynb',
                  'notebooks/RealTrackingData.ipynb',
                  'notebooks/RealTrackingData.ipynb',
                  'notebooks/WorkingWithMumodoSlices.ipynb']),
                 ('mumodo_examples/notebooks/sampledata',
                  ['sampledata/othersensor.xio.gz',
                   'sampledata/test.eaf',
                   'sampledata/test.inc_reco',
                   'sampledata/test.mp4',
                   'sampledata/test.mumodo',
                   'sampledata/test.TextGrid',
                   'sampledata/test.txt',
                   'sampledata/test.wav',
                   'sampledata/test.xio.gz',
                   'sampledata/black.jpg',
                   'sampledata/testimage.png'])],

    maintainer='Dialogue Systems Group, Bielfeld University',
    maintainer_email='spyros.kousidis@uni-bielefeld.de',
    license='MIT License (MIT)',
    download_url='https://github.com/dsg-bielefeld/mumodo.git',
    classifiers=[
    	'Development Status :: 5 - Production/Stable',
    	'Intended Audience :: Science/Research',
    	'License :: OSI Approved :: MIT License (MIT)',
    	'Programming Language :: Python',
    	'Programming Language :: Python :: 2.7',
    	'Topic :: Scientific/Engineering :: Information Analysis',
    ],
)

#Install dependencies
system("pip install -r requirements.txt")
