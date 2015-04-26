#!/bin/bash

#runs the unittests for all mumodo packages in the terminal

python unittest_mumodoIO.py -v > /dev/null
python unittest_xio.py -v > /dev/null
python unittest_InstantIO.py -v > /dev/null
python unittest_analysis.py -v > /dev/null
python unittest_corpus.py -v > /dev/null
python unittest_increco.py -v > /dev/null


