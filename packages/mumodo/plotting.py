# The MIT License (MIT)
#
# Copyright (c) 2015 Dialogue Systems Group, University of Bielefeld
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""plotting.py -- plotting functions

Plotting functions. To be used in an interpreter with inline plottig
capabilities, such as IPython notebook

"""

__author__ = ["Spyros Kousidis", "Katharina Jettka", "Gerdis Anderson",
              "Robert Rogalla", "Fabian Wohlgemuth", "Casey Kennington"]
__copyright__ = "Dialogue Systems Group Bielefeld - www.dsg-bielefeld.de"
__credits__ = ["Spyros Kousidis", "Katharina Jettka", "Gerdis Anderson",
               "Robert Rogalla", "Fabian Wohlgemuth", "Casey Kennington"]
__license__ = "MIT"
__version__ = "2.0"
__maintainer__ = "Spyros Kousidis"
__status__ = "Development" # Development/Production/Prototype

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mumodo.analysis import get_tier_boundaries, get_tier_type, \
                            slice_intervalframe_by_time

__all__ = ['plot_annotations', 'plot_scalar', 'plot_vector', 'plot_reco']

def __point_tier_to_intervals__(tier, width):
    """ Convert a point tier into intervals for drawing

    The function takes a point_tier as input and returns an
    interval tier, with the intervals centered around the points.
    The width parameter controls the width of the intervals.

    This funciton is used strictly for drawing

    """
    newtier = tier.copy(deep=True)
    newtier['start_time'] = newtier['time'] - float(width)/2
    newtier['end_time'] = newtier['time'] + float(width)/2
    newtier['text'] = newtier['mark']

    return newtier.ix[:, ['start_time', 'end_time', 'text']]

def __truncate_text__(ax, text, renderer, st, en, textkwargs):
    """Truncate the text to fit nicely in the plot

    Recursively cuts 10 % of the text until the text fits
    (horizontally) in an area defined in plotted units

    ax -- the matplotlib Axes object of a subplot
    text -- the text to fit in the area
    renderer -- the figure.canvas.renderer object
    st, en -- the left-to-right limits of the area (in
              plotted units)

    textkwargs -- the fontdict of the text

    """
    mytext = ax.text(st, 0.5, text, alpha=0, **textkwargs)
    width = mytext.get_window_extent(renderer).width
    start = ax.transData.transform([st, 0])[0]
    end = ax.transData.transform([en, 0])[0]
    while width > (end - start):
        mytext = ax.text(st, 0.5, text, alpha=0, **textkwargs)
        width = mytext.get_window_extent(renderer).width
        start = ax.transData.transform([st, 0])[0]
        end = ax.transData.transform([en, 0])[0]
        text = text[:int(0.9 * len(text))]
    return text

def __draw_tier__(ax, renderer, tier, **kwargs):
    """ Subplot of an interval or point tier

    Not to be called by itself but as part a plot function

    Arguments:

    ax -- A Matplotlib.pylab subplot object

    renderer -- A Figure.canvas renderer object

    tier -- the tier to be drawn

    The following kwargs HAVE to be passed:

    xmin, xmax -- limits of the x axis

    ymin, ymax -- define the base and top (in units between 0 and 1)
                  of the boxes depicting the intervals

    xticks: the x axis tick marks

    xlabels: the x axis tick labels

    tierkey: this key will be shown to identify this tier

    tiercolor -- set the color of the subplot items (boxes or lines)
                 if this is a color code, then all intervals/lines of the
                 tier are drawn in that colour (by default blue)

                 if it is a dictionary of labels and colors, then those
                 colors are used for those labels, with black for labels
                 not found in the dict.

    edgecolor --set the color of the edges of boxes

    textkwargs -- if not None, uses these kwargs to print the labels

    """

    ax.set_ylabel(kwargs['tierkey'], rotation='90')
    ax.set_yticks([])
    ax.set_xticks(kwargs['xticks'])
    ax.set_xticklabels(kwargs['xlabels'])
    ax.set_xlim(kwargs['xmin'], kwargs['xmax'])
    y0, y1 = kwargs['ymin'], kwargs['ymax']

    if isinstance(kwargs['edgecolor'], basestring):
        ecolor = kwargs['edgecolor']
    else:
        ecolor = 'w'

    for i in tier.index:
        if isinstance(kwargs['tiercolor'], basestring):
            fcolor = kwargs['tiercolor']
        elif isinstance(kwargs['tiercolor'], dict):
            if tier['text'][i] not in kwargs['tiercolor'].keys():
                fcolor = 'black'
            else:
                fcolor = kwargs['tiercolor'][tier['text'][i]]
        else:
            fcolor = 'b'

        ax.axhspan(y0, y1,
                   (tier['start_time'][i] - kwargs['xmin']) / \
                   (kwargs['xmax'] - kwargs['xmin']),
                   (tier['end_time'][i]  - kwargs['xmin']) / \
                   (kwargs['xmax'] - kwargs['xmin']),
                   facecolor=fcolor, edgecolor=ecolor)
        if kwargs['textkwargs'] is not None:
            txt = __truncate_text__(ax, tier['text'][i], renderer,
                                    tier['start_time'][i],
                                    tier['end_time'][i],
                                    kwargs['textkwargs'])
            ax.text(tier['start_time'][i], 0.5, txt,
                    **kwargs['textkwargs'])

def plot_reco(**kwargs):
    """Plot an inc_reco file

    The function accepts only kwargs, so as to be used with IPython
    widgets. These kwargs have to be passed

    iframe -- an intervalframe dict that represents the imported reco,
              with each update on a separate tier

    latest_tiers -- the number of updates to display as separate tier
                    subplots. If there are yet more updates than subplots
                    available, they appear as grey diamonds on the tier subplot
                    representing the earliest visible update (yellow diamond)

    current_time -- the current time. Only updates up to this time will be
                    plotted on any tier

    optional kwargs:

    max_history -- set the earliest time in the past (relative to current time)
                   that will be shown on any tier

    printing -- if True, the latest update is also printed as text

    filepath -- a valid file path and name for saving the plot as
                a figure on disk (no figure will be saved if filename is
                None)

    hscale, vscale -- enlarge the resulting plot horizontally or vertically,
                      (must be positive integers)

    textfontsize -- fontsize for the interval (IU) labels

    tickfontsize -- fontsize for the ticks

    labelfontsize -- fontsize for the Y (updates) labels

    tickspacing -- spacing for the x axis ticks (positive int)

    """
    intervalframe = kwargs['iframe']
    latest_tiers = kwargs['latest_tiers']
    current_time = kwargs['current_time']

    #dict of optional kwargs and default values:

    optional = {'printing': False,
                'filepath': False,
                'max_history': 0,
                'hscale': 1,
                'vscale': 1,
                'textfontsize': 16,
                'tickfontsize': 14,
                'labelfontsize': 14,
                'tickspacing': 1}

    for opt in optional:
        if opt not in kwargs or kwargs[opt] <= 0:
            kwargs[opt] = optional[opt]


    if kwargs['max_history'] > 0:
        min_time = max(current_time - kwargs['max_history'], 0)
        max_time = max(kwargs['max_history'], current_time)
    else:
        min_time = 0
        max_time = max([float(k) for k in intervalframe.keys()])

    min_time = int(min_time)
    max_time = int(max_time + 1)

    updates = []
    for key in intervalframe.keys():
        if float(key) <= current_time:
            updates.append(float(key))

    fig = plt.figure(figsize=(16 * kwargs['hscale'],
                              2 * latest_tiers * kwargs['vscale']))
    ax = fig.add_subplot(latest_tiers, 1, 1)
    splots = min(latest_tiers, len(updates))
    if len(updates) > 0:
        for i, u in enumerate(sorted(updates)):
            tier = slice_intervalframe_by_time(intervalframe[str(u)],
                                               min_time, max_time)
            last_time = intervalframe[str(u)]['end_time'].iloc[-1]
            if i >= len(updates) - latest_tiers:
                ax = fig.add_subplot(latest_tiers, 1, splots)
                __draw_tier__(ax, fig.canvas.get_renderer(),
                              tier,
                              xmin=min_time,
                              xmax=max_time,
                              xticks=range(min_time, max_time + 1,
                                           kwargs['tickspacing']),
                              xlabels=range(min_time,
                                            max_time + 1,
                                            kwargs['tickspacing']),
                              tierkey='',
                              tiercolor='w', edgecolor='b', ymin=0.3, ymax=0.7,
                              textkwargs={'color': 'k',
                                          'fontsize': kwargs['textfontsize']})
                splots -= 1
                ax.plot([last_time], [0.9], 'yD', markersize=10)
                if i < len(updates) - 1:
                    ax.vlines(last_time, 0, 1, linewidth=2, color='r')
                    ax.set_ylabel(str(u))
                else:
                    ax.vlines(current_time, 0, 1, linewidth=2, color='r')
                    ax.set_ylabel(current_time)
            else:
                ax = fig.add_subplot(latest_tiers, 1, latest_tiers)
                ax.plot([last_time], [0.9], 'D', color='grey', markersize=10)

        if kwargs['printing']:
            print "update at:", u
            print intervalframe[str(u)]
    else:
        ax.set_yticks([])
        ax.set_xlim(0, max_time)
    if kwargs['filepath']:
        fig.savefig(filepath)

def plot_scalar(streamframe, scalars, first_index=0, last_index=0, filepath=''):
    """Plot scalar(s) vs time

    Plot one or more column(s) with a scalar type against time (index of the
    streamframe)

    Arguments:
    streamframe -- a streamframe with time as index, naturally
    scalars -- a list of column names (strings)

    Keyword arguments:
    first_index, last_index -- define a time region (index is time).
                               A value of zero is interpreted as the
                               beginning and end of the streamframe,
                               respectively
    filepath    -- Filepath to save the plot.

    """
    fig = plt.figure(figsize=(14, 2))
    ax1 = fig.add_subplot(111)
    if first_index == 0:
        first_index = streamframe.index[0]
    if last_index == 0:
        last_index = streamframe.index[-1]
    for scalar in scalars:
        ax1.plot(streamframe.ix[first_index:last_index].index,
                 streamframe.ix[first_index:last_index][scalar],
                 label=scalar)
    ax1.set_xlabel(streamframe.index.name)
    ax1.legend()
    if len(filepath) > 0:
        fig.savefig(filepath, format=filepath.split('.')[1])

def plot_annotations(tierdict, time_begin=None, time_end=None, tierorder=None,
                     colorindex=None, hscale=1, vscale=1, linespan=20,
                     pointwidth=0.05, tickspacing=1,
                     text_kwargs=None, filepath=None):

    """Plot ELAN annotations, imported from textgrids

    arguments:
    tierdict    a dictionary of intervalframes

    keyword arguments:

    time_begin     -- minimum time (in seconds) of plot. If set to None, the
                       minimum time is found from the data
    time_end       -- maximum time (in seconds) of plot. If set to None, the
                       maximum time is found from the data
    tierorder      -- list of tierKey names to set the order of plotting.
                      Specifying less names than in the tierdict itself
                      results in only those tiers being drawn

    colorindex     -- list of colors to cycle through for each tier, or

                dictionary with labels as keys and colorcodes as values,
                for plotting annotation tiers with finite label sets

    hscale, vscale -- horizontal/vertical scaling of the plot

    linespan       -- time displayed per line of the plot (default 20 seconds)

    pointwidth     -- width of lines for point tiers (in seconds)

    tickspacing    -- number of seconds between ticks on x axis (default 1)

    text_kwargs    -- a fontdict for plt.text() in order to print the
                      text labels. Set to None to avoid printing any text

    filepath       -- path to filename to save the figure, e.g:
                      '~/Desktop/myfile.pdf'

                      The file must have one of the matplolib-supported
                      extensions, e.g. 'pdf', 'png', 'jpg'

    """
    if colorindex == None:
        colorindex = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
    #determine tiers to draw and the order
    thekeys = []
    if tierorder == None:
        thekeys = tierdict.keys()
    else:
        thekeys = tierorder

    if len(thekeys) == 0:
        return "No tiers to plot!"

    #find boundaries
    tiermin = min([get_tier_boundaries(tierdict[tierkey])[0] for tierkey \
                   in thekeys])
    tiermax = max([get_tier_boundaries(tierdict[tierkey])[1] for tierkey \
                   in thekeys])
    if time_begin == None:
        time_begin = tiermin
    else:
        time_begin = max(time_begin, tiermin)
    if time_end == None:
        time_end = tiermax
    else:
        time_end = min(time_end, tiermax)

    #Check time limits
    duration = time_end - time_begin
    if duration <= 0:
        return "Wrong time limits!"
    elif duration < linespan:
        linespan = duration
        number_of_lines = 1
    else:
        number_of_lines = int((float(duration) / linespan)) + 1

    fig = plt.figure(figsize=(hscale * linespan,
                              vscale * number_of_lines * len(thekeys)))

    for line in range(number_of_lines):
        #Drawing loop of tiers
        for tiernumber, tierkey in enumerate(thekeys):
            #Trim tier at time limits
            t1 = time_begin + line * linespan
            t2 = min(t1 + linespan, time_end)


            if get_tier_type(tierdict[tierkey]) == 'point':
                tier = slice_intervalframe_by_time(\
                       __point_tier_to_intervals__(tierdict[tierkey],
                                                   pointwidth), t1, t2)
            elif get_tier_type(tierdict[tierkey]) == 'interval':
                tier = slice_intervalframe_by_time(tierdict[tierkey], t1, t2)
            else:
                continue
            #Add subplots
            ax = fig.add_subplot(number_of_lines * len(thekeys), 1,
                                 line * len(thekeys) + tiernumber + 1)
            xticks = range(int(t1), int(t2) + 1, tickspacing)
            if tiernumber == len(thekeys)-1:
                xlabels = xticks
            else:
                xlabels = []

            #Set the color
            if isinstance(colorindex, list):
                tiercolor = colorindex[tiernumber % len(colorindex)]
            elif isinstance(colorindex, dict):
                tiercolor = colorindex

            __draw_tier__(ax, fig.canvas.get_renderer(), tier, xmin=t1,
                          xmax=(t1 + linespan), ymin=0, ymax=1,
                          xticks=xticks, xlabels=xlabels, tierkey=tierkey,
                          tiercolor=tiercolor, edgecolor='w',
                          textkwargs=text_kwargs)
    fig.subplots_adjust(hspace=0.5)
    if filepath is not None:
        fig.savefig(filepath, format=filepath.split('.')[1])

def plot_vector(streamframe, vector, first_index=0, last_index=0,
                pointsize=40, colormap=plt.cm.jet, filepath=''):
    """Plot vector vs time

    Plot one column with a 3D-vector type against time (index of the
    streamframe). Creates a 3D scatter plot with points color-coded for
    time (the streamframe index)

    Arguments:
    streamframe -- a streamframe with time as index, naturally
    vector -- column name (string)

    Keyword arguments:
    first_index, last_index -- define a time region (index is time).
                               A value of zero is interpreted as the
                               beginning and end of the streamframe,
                               respectively
    pointsize -- radius of 3D points
    colormap -- a matplotlib cmap collection
    filepath    -- Filepath to save the plot.

    """
    if first_index == 0:
        first_index = streamframe.index[0]
    if last_index == 0:
        last_index = streamframe.index[-1]
    fig = plt.figure(figsize=(10, 8))
    ax1 = fig.add_subplot(111, projection='3d')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    xst, yst, zst, cst = [], [], [], []
    for frame_time in streamframe.ix[first_index:last_index].index:
        try:
            xst.append(streamframe[vector].ix[frame_time].x)
            yst.append(streamframe[vector].ix[frame_time].y)
            zst.append(streamframe[vector].ix[frame_time].z)
            cst.append(frame_time)
        except AttributeError:
            pass
    cax = ax1.scatter(xst, yst, zst, zdir='z', s=pointsize, c=cst,
                      cmap=colormap)
    fig.colorbar(cax)
    if len(filepath) > 0:
        fig.savefig(filepath, format=filepath.split('.')[1])
