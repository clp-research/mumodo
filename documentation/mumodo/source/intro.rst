Introduction
============

MUltiMOdal DOcument (mumodo) is a Python package developed by the Dialogue Systems Group (DSG), Bielefeld University. It has been designed to greatly simplify the task of importing, preprocessing and analysing multimodal data.

Mumodo addresses the following common issues in multimodal data analysis:

* Establishing a common format for all kinds of data
* Visualization of complex data
* Easily accessing, refering to, and getting views of such data
* Importing/exporting to and from other common tools
* Running the whole analysis using as few different pieces of software as
  possible
* Being able to reproduce the analysis
* Have a clear presentation of the analysis procedure and results

Download and install
==================

Get mumodo from github or install with pip. Please check the readme file for detailed installation instructions.

The Data Model
==============

Multimodal analysis in mumodo uses a data model in which information is stored (mostly) in two types of objects: 

1. The StreamFrame, which is a time-indexed pandas DataFrame of typed events or groups of events (frames)

2. The IntervalFrame, which is a DataFrame  of intervals with start time, end time and label properties. A similar object called the PointFrame is used to import point tiers from Praat.


Mumodo Parts
============

Mumodo consists of the following parts:

1. MumodoIO 

This part of mumodo handles input/output of data into StreamFrames and IntervalFrames. Widely used formats such as CSV and Praat textgrid are upported. In addition, mumdodo natively supports more specialized formats, such as XIO and inc_reco.

2. Analysis

This module contains basic operations between the main object types. For example, it offers functions for getting the union/intersection of IntervalFrames, or converting/shifting their times etc. However, the wealth of functions in Pandas/Scipy/Numpy provide a very complete analysis environment.

3. Plotting

Functions for plotting (multiple) scalar or vector series, based on matplotlib. When using mumodo in the IPython interpreter, you can have your plots inlined with your analysis.

4. Corpus

This module  provides an abstraction layer between resources (modalities) and the actual filesystem, so that a multimodal document can be imported as whole (rather than several files  one by one) in order to perform analysis.

Usage
=====

Mumodo can be used either as a regular Python package, e.g. it can be imported into scripts that perform batch analysis of large corpora, or interactively in an interpreter. In the latter case, we recommend using a distribution that includes IPython, Matplotlib, Numpy, Pandas, Scipy as well as Moviepy (for Audio and Video data), and PIL for images. There are many free distributions available that provide these and many more.

The Notebooks
=============

Mumodo documentation is split into two parts. If you are looking for a detailed documentation of all the functions and classes, you are in the right place. However, a more high-level, tutorial-like documentation of the usage can be found in the form of IPython notebooks. Please look in the readme for instructions on how to install the notebooks and their sample data into a workspace folder (can be done automatically). The following notebooks are available:

* Basic Data Types - learn about the basic data types of mumodo
* Basic IO - learn how to import/export data from common and mumodo-specific file formats into your notebook as basic data types 
* Doing Analysis with mumodo - basic walkthrough some of the analysis functions
* Plotting functions - some examples of plotting functions
* RealTrackingData - an example analyis using real motion capture data
* Computing Offset - synchronize diverse data streams
* Managing Corpora and Resources with mumodo - an introduction to the corpus management part of mumodo
* Working with mumodo Slices - more advanced mumodo corpus tricks


