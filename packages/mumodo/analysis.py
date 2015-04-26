"""analyis.py -- analysis and plotting functions

Functions for analyis of streamframes, intervalframes and pointframes

"""

__author__ = ["Spyros Kousidis", "Katharina Jettka", "Gerdis Anderson",
              "Robert Rogalla", "Fabian Wohlgemuth", "Casey Kennington"]
__copyright__ = "Dialogue Systems Group Bielefeld - www.dsg-bielefeld.de"
__credits__ = ["Spyros Kousidis", "Katharina Jettka", "Gerdis Anderson",
               "Robert Rogalla", "Fabian Wohlgemuth", "Casey Kennington"]
__license__ = "GPL"
__version__ = "0.1.1"
__maintainer__ = "Spyros Kousidis"
__status__ = "Development" # Development/Production/Prototype

import pandas as pd

__all__ = ['intervalframe_overlaps', 'intervalframe_union',
           'invert_intervalframe', 'create_intervalframe_from_streamframe',
           'create_streamframe_from_intervalframe',
           'slice_streamframe_on_intervals', 'slice_intervalframe_by_time',
           'slice_pointframe_by_time',
           'convert_times_of_tier', 'convert_times_of_tiers',
           'shift_tier', 'shift_tiers', 'get_tier_type', 'get_tier_boundaries',
           'join_intervals_by_label', 'join_intervals_by_time']

def intervalframe_overlaps(frame1, frame2, concatdelimiter='/'):
    """Intersection of two interval frames

    Return an IntervalFrame with the intersection  of two intervalframes
    An intersection is defined as an AND function on the intervals of both
    sources (regardless of text). HINT: Input Intervalframes should
    be imported without empty intervals

    Arguments:
    frame1,frame2   -- IntervalFrames.

    Keyword arguments:

    concatdelimiter  --  Concatenate the labels of the overlapping intervals
                         to create labels of the new dataframe intervals.
                         If empty string is given, the intervals are simply
                         labeled with 'overlap' instead.

    """
    overlaps = []
    if len(frame2) < len(frame1):
        frame1, frame2 = frame2, frame1
    for intrv1 in frame1.index:
        st1 = frame1['start_time'].ix[intrv1]
        en1 = frame1['end_time'].ix[intrv1]
        fr2 = frame2[frame2['end_time'] > st1]
        fr2 = fr2[fr2['start_time'] < en1]
        for intrv2 in fr2.index:
            overlap = {}
            if type(concatdelimiter) == str and len(concatdelimiter) > 0:
                overlap['text'] = fr2.ix[intrv2]['text'] + concatdelimiter + \
                                  frame1.ix[intrv1]['text']

            else:
                overlap['text'] = 'overlap'
            st2 = fr2['start_time'].ix[intrv2]
            en2 = fr2['end_time'].ix[intrv2]
            if st2 > st1:
                overlap['start_time'] = st2
            else:
                overlap['start_time'] = st1
            if en2 > en1:
                overlap['end_time'] = en1
            else:
                overlap['end_time'] = en2
            overlaps.append(overlap)

    return pd.DataFrame(overlaps).ix[:, ['start_time', 'end_time', 'text']]

def intervalframe_union(frame1, frame2, concatdelimiter='/'):
    """Union of two interval frames

    Return an IntervalFrame with the union of two intervalframes
    A union is defined as an OR function on the intervals of both
    sources (regardless of text). Optionally, the labels of overlapping
    intervals can be concatenated to create the labels of the new
    dataframe intervals. HINT: Input Intervalframes should
    be imported without empty intervals

    Arguments:
    frame1,frame2   -- IntervalFrames.

    concatdelimiter  --  Concatenate the labels of the overlapping intervals
                         to create labels of the new dataframe intervals.
                         If empty string is given, the intervals are simply
                         labeled with 'overlap' instead.

    """
    unifications = []
    #join the two frames into one
    newframe = frame1.append(frame2)
    if len(newframe) == 0:
        return pd.DataFrame()
    newframe.sort(columns=['start_time', 'end_time'], inplace=True)
    newframe.reset_index(drop=True, inplace=True)
    #Read first interval
    start = newframe.irow(0)['start_time']
    end = newframe.irow(0)['end_time']
    text = newframe.irow(0)['text']
    #main loop
    for i in newframe[1:].index:
        #Read the new interval
        start2 = newframe.ix[i]['start_time']
        end2 = newframe.ix[i]['end_time']
        text2 = newframe.ix[i]['text']
        #Is the new interval disjoint from the running one?
        if start2 > end:
            if not (type(concatdelimiter) == str and len(concatdelimiter) > 0):
                text = 'union'
            unifications.append({'start_time': start, 'end_time': end,
                                 'text': text})
            start = start2
            end = end2
            text = text2
        else:
            if end2 > end:
                end = end2
            #Set the running label
            if type(concatdelimiter) == str:
                text += concatdelimiter + text2
    #add the last working interval
    if not (type(concatdelimiter) == str and len(concatdelimiter) > 0):
        text = 'union'
    unifications.append({'start_time': start, 'end_time': end,
                         'text': text})
    return pd.DataFrame(unifications, columns=['start_time',
                                               'end_time', 'text'])

def invert_intervalframe(inversion, st=None, en=None, label=None,
                         concat_delimiter='/', **kwargs):

    """Return the negative of an interval frame

    Return the inversion of an interval frame.
    An inversion is defined as a NOT function of the original
    interval frame. The labels of inverted intervals are by default
    a concatenation of the labels of surrounding intervals. Any other
    preferred label can be passed to the function.
    HINT: Input Intervalframes should be imported without empty intervals

    Arguments:
    frame            -- IntervalFrame.

    label            -- The labels of the intervals of the inverted frame
                        are concatenations of the labels of the surrounding
                        intervals in the original frame when the default
                        value None is not changed. Any string that is
                        given instead will become the label of the
                        inverted frame's intervals.

    st               -- The time at which the inverted frame shall start.
                        If st is None, the inverted frame will start at the
                        end_time of the first interval of the original frame.

    en               -- The time at which the inverted frame shall end. If en is
                        None, the inverted frame will end at the start_time of
                        the last interval of the original frame.

    concat_delimiter -- the character by which the labels of the surrounding
                        intervals of the original frame are to be concatenated.



    """

    if 'min_boundary_threshold' not in kwargs.keys():
        min_boundary_threshold = 0.000001
    else:
        min_boundary_threshold = kwargs['min_boundary_threshold']

    if len(inversion) == 0 or (inversion.columns != ['start_time', 'end_time',
                                                     'text']).all():
        print "empty intervalframe or wrong shape"
        return

    tf = inversion.copy()

    if st == None:
        st = tf['start_time'].iloc[0]
    if en == None:
        en = tf['end_time'].iloc[-1]

    tf['temp'] = tf['start_time']
    tf['start_time'] = tf['end_time']
    tf['end_time'] = tf['temp'].shift(-1)
    tf = tf.append(pd.DataFrame([{'start_time': tf['start_time'].iloc[-1],
                                  'end_time': en,
                                  'text': tf['text'].iloc[-1]}]))
    tf = tf.append(pd.DataFrame([{'start_time': st,
                                  'end_time': tf['temp'].iloc[0],
                                  'text': tf['text'].iloc[0]}]))

    tf.sort(columns=['start_time'], inplace=True)
    tf['dur'] = tf['end_time'] - tf['start_time']
    tf = tf[tf['dur'] > min_boundary_threshold]
    tf.reset_index(inplace=True)

    if label == None:
        for i in tf.index[1:-1]:
            tf.loc[i, 'text'] += (concat_delimiter + tf.loc[i+1, 'text'])
    else:
        tf['text'] = str(label)

    return tf.ix[:, ['start_time', 'end_time', 'text']]

def create_intervalframe_from_streamframe(streamframe, column, function,
                                          intervalwidth, text='True'):
    """Creates an Intervalframe from a streamframe based on a condition.

    Arguments:

    streamFrame   -- The Streamframe that contains the data.
    column        -- The column to evaluate (function evaluates each
                     item of this column).
    function      -- A lambda function that evaluates to true or false
                     depending on a condition
                     e.g. lambda x: True if x>0 else False.
    intervalWidth -- Minimum distance between intervals (setting higher
                     results in less, bigger intervals).

    Keyword arguments:
    text          -- Text for the Intervalframe labels (default True).

    """
    indices = streamframe[streamframe[column].map(function)].index
    if len(indices) < 1:
        return None
    start = None
    last = None

    interval_list = []

    #Little helper function
    def append_to_list(tt1, tt2, ttx):
        """add a dictionary to the list"""
        if tt2 != tt1:
            interval = {}
            interval['start_time'] = tt1
            interval['end_time'] = tt2
            interval['text'] = ttx
            interval_list.append(interval)

    for i in indices:
        if start == None:
            start = i
            last = i
        if i - last <= intervalwidth:
            last = i
        else:
            append_to_list(start, last, text)
            start = i
            last = i
    #Append the last interval if required
    append_to_list(start, last, text)

    if len(interval_list) > 0:
        return pd.DataFrame(data=interval_list, columns=['start_time',
                                                         'end_time', 'text'])
    else:
        return None

def create_streamframe_from_intervalframe(frame, relative=False,
                                          start_label_appendix='',
                                          end_label_appendix='',
                                          fillstep=0):
    """ Creates a streamframe from an intervalframe

    Arguments:
    frame                 -- The IntervalFrame that contains the data
    relative              -- If set to True, relative will make the
                             timestampfs that serve as index values relative
                             to the frist timestamp
    start_label_appendix  -- Appends a suffix to the first event of the
                             respective type.
    end_label_appendix    -- Appends a suffix to the last event of the
                             respective type
    fillstep              -- If greater than the default value 0, then in the
                             streamframe
                             there will be inserted events of the respective
                             type of each
                             interval at regular steps between the start and
                             the end of
                             that interval. The stepwidth is the value of
                             fillstep.

    """

    if len(frame) == 0 or (frame.columns != ['start_time', 'end_time',
                                             'text']).all():
        print "empty intervalframe or wrong shape"
        return

    sframe = frame.copy()
    sframe['time'] = sframe['start_time']
    sframe['value'] = sframe['text'].map(lambda x: x + "_" + \
                      start_label_appendix if isinstance(x, basestring) else x)
    sframe.index = sframe['time']
    sframe = sframe.ix[:, ['value']]

    eframe = frame.copy()
    eframe['time'] = eframe['end_time']
    eframe['value'] = eframe['text'].map(lambda x: x + "_" + \
                         end_label_appendix if isinstance(x, basestring) else x)
    eframe.index = eframe['time']
    eframe = eframe.ix[:, ['value']]

    streamframe = sframe.append(eframe)

    if fillstep > 0:
        for i in frame.index:
            if fillstep < frame['end_time'].ix[i] - frame['start_time'].ix[i]:
                fframes = []
                fillpoint = frame['start_time'].ix[i] + fillstep
                while fillpoint < frame['end_time'].ix[i]:
                    fframes.append({'time': fillpoint,
                                    'value': frame['text'].ix[i]})
                    fillpoint += fillstep
                fframe = pd.DataFrame(fframes)
                fframe.index = fframe['time']
                streamframe = streamframe.append(fframe.ix[:, ['value']])

    streamframe.sort_index(inplace=True)
    if relative:
        streamframe.index -= streamframe.index[0]
    return streamframe

def slice_streamframe_on_intervals(streamframe, intervalframe):
    """ Create a sliced streamFrame.

    Slice a streamframe's index on the intervals of the intervalframe,
    regardless of the text. HINT: Intervalframe should not have
    empty intervals.
    The intervalframe gives the needed intervals from the 'original'
    streamframe, to be included in the new, sliced streamframe.

    Arguments:
    streamFrame     --   The streamFrame that contains the data.
    intervalFrame   --   The intervalFrame that contains the intervals,
                         needed for the sliced streamFrame.

    """
    new_index = []
    for i in intervalframe.index:
        start = intervalframe['start_time'].ix[i]
        end = intervalframe['end_time'].ix[i]
        this_slice = streamframe.ix[start:end]
        this_index = [x for x in this_slice.index]
        new_index += this_index
    return streamframe.ix[new_index]

def slice_intervalframe_by_time(intervalframe, start_time, end_time,
                                method='truncate'):
    """ Create a temporal slice of an intervalframe

    Slice an intervalframe, so that only intervals within the
    limits defined will be kept, regardless of the text labels

    Arguments:
    intervalframe -- the input intervalframe to be sliced
    start_time, end_time -- define a time region

    Keyword arguments:
    method -- Defines how to deal with intervals that cross the
              temporal boundaries. Possible values:
        'truncate' (default): Cut the intervals at the boundaries
        'include': Include intervals crossing the boundaries
        'exclude': Exclude intervals crossing the boundaries

    """
    if method == 'include':
        newframe = intervalframe[intervalframe['end_time'] > start_time]
        newframe = newframe[newframe['start_time'] < end_time]
    elif method == 'exclude':
        newframe = intervalframe[intervalframe['start_time'] >= start_time]
        newframe = newframe[newframe['end_time'] <= end_time]
    elif method == 'truncate':
        newframe = intervalframe[intervalframe['end_time'] > start_time]
        newframe = newframe[newframe['start_time'] < end_time]
        if len(newframe) == 0:
            return newframe
        if newframe['start_time'].iat[0] < start_time:
            newframe['start_time'].iat[0] = start_time
        if newframe['end_time'].iat[-1] > end_time:
            newframe['end_time'].iat[-1] = end_time
    else:
        print "method must be one of 'include', 'exclude', 'truncate'"
        return

    return newframe

def slice_pointframe_by_time(pointframe, start_time, end_time):
    """ Create a temporal slice of a pointframe

    Slice a pointframe, so that only points within the
    limits defined will be kept, regardless of the text labels

    Arguments:
    pointframe -- the input pointframe to be sliced
    start_time, end_time -- define a time region

    """
    return pointframe[pointframe['time'].map(lambda x: x >= start_time \
                                                 and x <= end_time)]

def convert_times_of_tier(tier, function):
    """ Convert the times of a tier using a specified function

    tier --- a tier, either intervalframe or point tier

    An IntervalFrame is a Pandas DataFrame that represents a Praat interval
    tier. The columns must be ['start_time', 'end_time', text']. A PointTier
    is a Pandas DataFrame that represents a Praat point tier. The columns must
    be ['time', 'mark'].

    function -- all times will be replaced by the output of this function. A
                lamda function should be used, e.g. lambda x: int(1000 * x)
                converts from (float) seconds to (int) milliseconds.
                Conversely, lambda x: float(x)/1000 ( or x / 1000. ) converts
                back to (float) seconds.
                It is possible to do custom conversions such as shifts, etc.

    """
    for column in tier.columns:
        if 'time' in column:
            tier.loc[:, column] = tier[column].map(function)

def convert_times_of_tiers(tierdict, function):
    """ Convert the times of all tiers in a dictionary using a specified
        function

    tierdict  --- a dictionary of tiers, either intervalframes or point tiers

    An IntervalFrame is a Pandas DataFrame that represents a Praat interval
    tier. The columns must be ['start_time', 'end_time', text']. A PointTier
    is a Pandas DataFrame that represents a Praat point tier. The columns must
    be ['time', 'mark'].

    function -- all times will be replaced by the output of this function. A
                lamda function should be used, e.g. lambda x: int(1000 * x)
                converts from (float) seconds to (int) milliseconds.
                Conversely, lambda x: float(x)/1000 ( or x / 1000. ) converts
                back to (float) seconds.
                It is possible to do custom conversions such as shifts, etc.

    """
    for tier in tierdict:
        convert_times_of_tier(tierdict[tier], function)

def shift_tier(tier, offset):
    """ Shift a tier by a specified time offset

    tier  --- a tier, either an intervalframes or a point tier

    An IntervalFrame is a Pandas DataFrame that represents a Praat interval
    tier. The columns must be ['start_time', 'end_time', text']. A PointTier
    is a Pandas DataFrame that represents a Praat point tier. The columns must
    be ['time', 'mark'].

    offset -- amount of time to shift the textgrid by in seconds. Can also be
    negative

    """
    convert_times_of_tier(tier, lambda x: x + offset)

def shift_tiers(tierdict, offset):
    """ Shift all tiers in a dictionary by a specified time offset

    tierdict  --- a dictionary of tiers, either intervalframes or point tiers

    An IntervalFrame is a Pandas DataFrame that represents a Praat interval
    tier. The columns must be ['start_time', 'end_time', text']. A PointTier
    is a Pandas DataFrame that represents a Praat point tier. The columns must
    be ['time', 'mark']

    offset -- amount of time to shift the textgrid by in seconds. Can also be
    negative

    """
    convert_times_of_tiers(tierdict, lambda x: x + offset)

def get_tier_type(tier):
    """ Discover the type of a tier

    A tier can be one of IntevalTier or PointTier. Discovery is
    based on the presence of a particular column ordering and
    naming.

    For IntervalTiers (or IntervalFrames) the columns are
    ['start_time', 'end_time', 'text'] in that order. The times
    are in seconds (and should be floats, but this is not strictly
    enforced)

    For PointTiers (or PointFrames) the columns are ['time', 'mark'],
    with the time again in seconds.

    Both need to be instances of pandas.DataFrame

    The function returns the string 'interval' or 'point', depending
    on the type of tier, or None if no conditions are satified

    """
    if not isinstance(tier, pd.DataFrame):
        return None
    if tier.columns[0] == 'start_time' and tier.columns[1] == 'end_time' \
                           and tier.columns[2] == 'text':
        return 'interval'
    elif tier.columns[0] == 'time' and tier.columns[1] == 'mark':
        return 'point'
    else:
        return None

def get_tier_boundaries(tier):
    """ Get the minimum and maximum times of this tier

    Returns a tuple (min, max) with the minimum and maximum
    times of the tier.

    """

    if get_tier_type(tier) == 'interval' and len(tier) > 0:
        return tier['start_time'].iloc[0], tier['end_time'].iloc[-1]
    elif get_tier_type(tier) == 'point' and len(tier) > 0:
        return tier['time'].iloc[0], tier['time'].iloc[-1]
    else:
        return None

def join_intervals_by_label(intervalframe, maximum_gap=float("inf")):
    """ Join near-adjacent intervals with the same label

    When (near) adjacent intervals in an intervalframe have the same label,
    they are concatenated into a single interval, starting at the start time
    of the first interval and ending at the end time of the adjacent interval

    If more than two adjacent intervals have the same label, the function
    chains them all together (the end time of last interval in the chain
    will be the end time of the new, single interval)

    WARNING: By default, this function does not check if the intervals
    are adjacent temporally. It only checks the labels. You can use the
    maximum_gap kwarg to add temporal constraints to the joining

    Arguments:

    intervalframe  -- An IntervalFrame: Pandas Dataframe with a standard
                      index and columns 'start_time', 'end_time' (floats)
                      and 'text' (can be of any type but is normally
                      str or unicode)

    kwargs:

    maximum_gap -- Do not join intervals that are more apart than this gap
                   (in seconds). If None (default), the gap is ignored and
                   all interval are joined

    """
    new_intervals = []
    new_text = None
    new_start = 0
    new_end = 0
    for i in intervalframe.index:
        st = intervalframe['start_time'].iat[i]
        en = intervalframe['end_time'].iat[i]
        text = intervalframe['text'].iat[i]
        #make sure a new interval is always created at the start
        if new_text is None:
            new_start = st
            new_end = en
            new_text = text
            continue

        if text != new_text or (st - new_end) > maximum_gap:
            new_intervals.append({'start_time': new_start,
                                  'end_time': new_end,
                                  'text': new_text})
            new_start = st
            new_text = text

        new_end = en
    return pd.DataFrame(new_intervals).ix[:, ['start_time', 'end_time', 'text']]

def join_intervals_by_time(intervalframe, minimum_gap=0, concat_delimiter=" "):
    """ Join near-adjacent intervals by time

    When adjacent intervals in an intervalframe are close to each other,
    they are concatenated in to a single interval, starting at the start
    time of the first interval and ending at the end time of the
    adjacent interval.

    If more than two adjacent intervals are near each other, the function
    chains them all together (the end time of last interval in the chain
    will be the end time of the new, single interval)

    The closeness is defined by the minimum_gap kwarg. By default, only
    directly adjacent intervals (that share a boundary) are concatenated
    The labels of the concatenated intervals are also concatenated,
    separated by a configurable delimiter (by default a space).

    Arguments:

    intervalframe  -- An IntervalFrame: Pandas Dataframe with a standard
                      index and columns 'start_time', 'end_time' (floats)
                      and 'text' (can be of any type but is normally str
                      or unicode)

    kwargs:

    minimum_gap -- Do not join intervals that are more apart than this
                   gap (in seconds).

    concat_delimiter -- A string inserted between the concatenated interval
                        labels

    """
    new_intervals = []
    new_text = None
    new_start = 0
    new_end = 0
    for i in intervalframe.index:
        st = intervalframe['start_time'].iat[i]
        en = intervalframe['end_time'].iat[i]
        text = intervalframe['text'].iat[i]
        #make sure a new interval is always created at the start
        if new_text is None:
            new_start = st
            new_end = en
            new_text = text
            continue

        if  (st - new_end) > minimum_gap:
            new_intervals.append({'start_time': new_start,
                                  'end_time': new_end,
                                  'text': new_text})
            new_start = st
            new_text = text
        else:
            new_text = new_text + concat_delimiter + text

        new_end = en

    #finally, add the last interval
    if new_end > 0:
        new_intervals.append({'start_time': new_start,
                              'end_time': new_end,
                              'text': new_text})
    return pd.DataFrame(new_intervals).ix[:, ['start_time', 'end_time', 'text']]
