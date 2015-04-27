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

"""mumodoIO.py: Functions to for stream- and interval- frame I/O

  Streamframes and Intervalframes are the two types of objects that
  mumodo uses for analysis. Both are Pandas DataFrames. Instead of
  subclassing Pandas DataFrames, we simply format our dataframes in
  a specific way.

  Streamframes are like time series. They contain a series of timed,
  typed events. The events can be of different types in the same series.
  The index of the DataFrame is the timestamp of the event. Thus, slices
  of the DataFrame correspond to time intervals directly. Streamframes
  are created primarily from our own XIO files, but can also be saved in
  other formats (e.g. CSV, Praat point tiers).

  Intervalframes are tiers of annotation intervals, such as those found
  in Praat and ELAN. They have three columns (start_time, end_time, text)
  This module makes use of the tgt [textgrid tools]
  package in order to import Praat textgrids. Because each tier of a
  textgrid is an intervalframe itself, the respective function returns
  a dictionary of Intervalframes, with the names of the tiers as keys.

"""

__author__ = ["Spyros Kousidis", "Katharina Jettka", "Gerdis Anderson",
              "Robert Rogalla", "Fabian Wohlgemuth"]
__copyright__ = "Dialogue Systems Group Bielefeld - www.dsg-bielefeld.de"
__credits__ = ["Spyros Kousidis", "Katharina Jettka", "Gerdis Anderson",
               "Robert Rogalla", "Fabian Wohlgemuth"]
__license__ = "GPL"
__version__ = "0.1.1"
__maintainer__ = "Spyros Kousidis"
__status__ = "Development" # Development/Production/Prototype

from mumodo.xiofile import XIOFile
from mumodo.increco import IncReco
import tgt
import pandas as pd

__all__ = ['open_streamframe_from_xiofile',
           'save_streamframe_to_xiofile', 'open_intervalframe_from_textgrid',
           'save_intervalframe_to_textgrid',
           'quantize', 'open_intervalframe_from_increco',
           'convert_pointtier_to_streamframe',
           'convert_streamframe_to_pointtier']

def open_streamframe_from_xiofile(filepath, sensorname, window_size=5,
                                  with_fields=None, without_fields=None,
                                  discard_duplicates=True, start_time=0,
                                  end_time=0, relative=True,
                                  timestamp_offset=0):
    """Import data for one sensor out of a XIOFile and return a
       StreamFrame indexed with timestamps. By default, the timestamps
       are made relative. Optionally, and offset can be added to
       relative timestamps or the raw timestamps can be kept.

       Arguments:
       filepath             --  Path + filename of the XIOFile to be imported.
       sensorname           --  Name of the sensor to be imported.
       window_size,
       with_fields,
       without_fields,
       discard_duplicates   --  Parameters for quantizing (see Quantize
                                function)
       start_time,
       end_time,
       relative             -- Parameters for xio_quicklinegen.
       timestamp_offset     -- is zero by default and makes timestamps relative
                               Set to any non_integer value, timestamp_offset
                               will leave the timestamps raw. Any non-zero
                               integer value will be added as offset to the
                               relative timestamps

    """
    infile = XIOFile(filepath, 'r', indexing=False)
    stream = pd.DataFrame(quantize(infile.xio_quicklinegen(start_time, end_time,
                                                           True, relative),
                                   sensorname, window_size, with_fields,
                                   without_fields, discard_duplicates,
                                   enumerate_fields=True))
    stream.dropna(subset=['time'], inplace=True)
    stream = stream[:-1]
    if len(stream) < 1:
        return stream
    stream.index = stream['time'].map(lambda x: int(x))
    if type(timestamp_offset) == int:
        stream.index -= infile.min_time
        stream.index += timestamp_offset
    else:
        print "non-int offset in input: raw timestamps from the file will be" +\
               " used"
    infile.xiofile_close()
    stream.index.name = None
    return stream

def save_streamframe_to_xiofile(framedict, filepath):
    """Save many streamframes to a single XIOFile.

    Arguments:
    framedict   --  a dict of streamframes, keys are the
                    sensornames
    filepath    --  Path + filename of the file to be written.
    sensorname  --  Name of the sensor.

    """

    #create a joined streamframe
    frame = None
    for key in framedict.keys():
        if len(framedict[key]) < 1:
            continue
        sensorframe = framedict[key].copy(deep=True)
        sensorframe['sensorname'] = key
        if frame is None:
            frame = sensorframe
        else:
            frame = frame.append(sensorframe)

    if len(frame) < 1:
        print "invalid data!"
        return

    frame.sort_index(inplace=True)

    outfile = XIOFile(filepath, 'w')
    types = {'float': 'sffloat', 'SFVec3f': 'sfvec3f', 'SFVec2f': 'sfvec2f',
             'SFRotation': 'sfrotation', 'MFVec3f': 'mfvec3f',
             'MFVec2f': 'mfvec2f', 'MFRotation': 'mfrotation',
             'MFString': 'mfstring', 'MFFloat': 'mffloat',
             'bool':'sfbool', 'int':'sfint32', 'str':'sfstring'}

    for row in frame.iterrows(): #each row of the dataframe
        timestamp = int(row[0])
        fields = row[1]
        sensorname = fields['sensorname']

        for fieldname in row[1].index:  #fieldname becomes name of each column
            if fieldname in ['time', 'sensorname']:
                continue
            for key in types:
                if key in str(type(row[1][fieldname])):
                    otype = types[key]
                    value = row[1][fieldname]
                    if str(value).lower() != 'nan':
                        outfile.xio_writeline(outfile.xio_formatline(otype,
                                                                     value,
                                                                     sensorname,
                                                                     fieldname,
                                                                     timestamp))
    outfile.xiofile_close()
    return

def open_intervalframe_from_textgrid(filepath, encoding='utf-8',
                                     asobjects=False,
                                     include_empty_intervals=False):
    """Import a textgrid and return a dict of IntervalFrames.

    Each tier in the textgrid becomes an IntervalFrame (Pandas DataFrame)
    The Intervals by default are tokenized into start_time, end_time and
    text columns.
    The points (for point tiers) are tokenized into time and mark columns.

    Arguments:
    filepath  -- Path + filename of the TextGrid file to be imported.

    Keyword Arguments:
    asobjects -- If True, then values are intervalobjects (as defined in
                 package tgt, instead of tokenizing into start_time etc.
                 IntervalFrame has only one column with these objects.
    include_empty_intervals -- If enabled, empty intervals between
                               annotations are also returned
    encoding -- character encoding to read the textgrid file

    """

    textgrid = tgt.read_textgrid(filepath, encoding, include_empty_intervals)
    result = {}
    for tier in textgrid.tiers:
        if len(tier) > 0:
            if isinstance(tier, tgt.IntervalTier):
                frame = pd.DataFrame(tier.intervals, columns=['intervals'])
                if asobjects == False:
                    frame['start_time'] = frame['intervals'].map(lambda x:\
                                                             x.start_time)
                    frame['end_time'] = frame['intervals'].map(lambda x:\
                                                               x.end_time)
                    frame['text'] = frame['intervals'].map(lambda x: x.text)
                    del frame['intervals']
            elif isinstance(tier, tgt.PointTier):
                frame = pd.DataFrame(tier.points, columns=['points'])
                if asobjects == False:
                    frame['time'] = frame['points'].map(lambda x: x.time)
                    frame['mark'] = frame['points'].map(lambda x: x.text)
                    del frame['points']
            result[tier.name] = frame
    return result

def save_intervalframe_to_textgrid(framedict, filepath, encoding='utf-8'):
    """Write a dict of IntervalFrames in a textgrid-File.

       Arguments:
       framedict    --  Dictionary of dataframes. The keys become tier
                        names in the textgrid file
       filepath     --  Path + filename of the file to be written.

       Keyword arguments:
       encoding: character encoding to save textgrid file

    """

    if len(framedict) < 1:
        print "invalid data!"
        return
    mytextgrid = tgt.TextGrid()
    for tier_name in framedict.keys():
        newtier = framedict[tier_name]
        if len(newtier.columns) == 3:
            mytier = tgt.IntervalTier(name=tier_name)
            for row in newtier.index:
                myinterval = tgt.Interval(newtier[newtier.columns[0]][row],
                                          newtier[newtier.columns[1]][row],
                                          newtier[newtier.columns[2]][row])
                mytier.add_interval(myinterval)
        elif len(newtier.columns) == 2:
            mytier = tgt.PointTier(name=tier_name)
            for row in newtier.index:
                mypoint = tgt.Point(newtier[newtier.columns[0]][row],
                                    newtier[newtier.columns[1]][row])
                mytier.add_point(mypoint)
        mytextgrid.add_tier(mytier)
    tgt.write_to_file(mytextgrid, filepath, encoding=encoding, format="long")

def open_intervalframe_from_increco(filepath, encoding='utf-8', lastonly=False):
    """ Create an interval frame from an inc_reco file

    Creates a dictionary with an intervalframe per chunk. The dictionary
    keys are the times of the chunks

    Arguments:

    filepath - the path to the inc_reco file

    Kwargs:

    encoding -- the encoding of the file

    lastonly -- Read only the last chunk in the inc_reco file
                rather than all chunks

    """

    reco = IncReco(filepath)
    start_chunk = -1 if lastonly else 0

    frame_dict = dict()
    for chunk in reco[start_chunk:]:
        cur_frame = None
        for line in chunk['Chunk']:
            reco_frame = pd.DataFrame([{"start_time": \
                                        float(line[0].decode(encoding)),
                                        "end_time": \
                                        float(line[1].decode(encoding)),
                                        "text": line[2].decode(encoding)}])
            if cur_frame is None:
                cur_frame = reco_frame
            else:
                cur_frame = cur_frame.append(reco_frame, ignore_index=True)

        #check for minor errors in the times
        #Sometimes the end of the previous word is 1 ms later than
        #the start of the next word
        for i in cur_frame.index[1:]:
            cur_frame.ix[i, 'start_time'] = max(cur_frame['start_time'].ix[i],
                                                cur_frame['end_time'].ix[i-1])

        frame_dict[str(chunk['Time'])] = cur_frame.ix[:, ['start_time',
                                                          'end_time',
                                                          'text']]
    return frame_dict

def quantize(rows, sensorname, window_size=5, with_fields=None,
             without_fields=None, discard_duplicates=True,
             enumerate_fields=False):
    """Quantize frames within a fixed time window

    Series of typed, timed events can often be grouped by sensorname
    (or namespace) to create complete frames of data. For example,
    skeleton/lefthand and skeleton/righthand may have been logged as
    different events (lines), but should belong together, as frames of
    the sensor 'skeleton'. This function performs this operation. This
    results in the quantization of the timestamps of the individual
    events into less timestamps for frames.

    The function is a Python generator that yields dictionaries.
    Each dictionary is a frame, with keys corresponding to individual
    fields in the frame and their values. The function can be directly
    input to a Pandas Dataframe constructor (as the data argument)

    Arguments:
    rows  -- iterable with dictionaries as items. They represent parsed
             I/O events. These dictionaries' keys should be:
            ['sensorname', 'fieldname', 'time', 'type','value']

    sensorname --  the name of the sensor by which to group

    Keyword arguments:
    window_size --  maximum time in ms to consider as one frame. Start a
                 new frame after this time has passed
    with_fields -- a list of fieldnames. Output frames contain only these
                 fields
    without_fields --  a list of fieldnames. Ouput frames will not contain
                       any of these fields. This overrides with_fields
                       for the same field if found in both lists
    discard_duplicates -- if True, additional values for the same field found
                          in the same window will be discarded.
                          If False, additional values for the same field found
                          in the same window will overwrite previous values
    enumerate_fields -- if True, enumerate all fields found in any frame. This
                        is required in order to prevent type coercion of columns
                        by Pandas, but is false by default. It will cause the
                        function to yield one final dict with value TRUE for all
                        keys that were enumerated. Thus, Pandas will not create
                        a FLOAT dtype for a column of INTs that has one NaN
                        value in it

    """
    if with_fields is None:
        with_fields = []
    if without_fields is None:
        without_fields = []

    doenumerate = enumerate_fields and not with_fields
    if doenumerate:
        enumerated_fields = set()

    window_end = 0
    cur_row = {}
    for row in rows:
        if row['sensorname'] != sensorname:
            continue
        if row['fieldname'] not in with_fields and with_fields:
            continue
        if row['fieldname'] in without_fields:
            continue
        if doenumerate:
            enumerated_fields.add(row['fieldname'])
        value = row['value']
        time = row['time']
        fieldname = row['fieldname']
        # If time falls in the current window, update row.
        if time <= window_end:
            # Do nothing if the same field already exists and
            # discard duplicates is true.
            if fieldname in cur_row and discard_duplicates:
                pass
            else:
                cur_row[fieldname] = value
        # Otherwise, create a new window.
        else:
            #yield the currentframe
            if cur_row:
                yield cur_row
            #initialize the new frame
            cur_row = {'time' : time, fieldname : value}
            window_end = time + window_size
    #After the loop, ensure the last frame is yielded
    yield cur_row

    #then add row with True for all keys, so that column-types aren't
    #converted automatically to float, due to a NaN value
    if enumerate_fields:
        #if with_fields are given, these are the enumerated_fields
        if with_fields:
            enumerated_fields = set(with_fields)
        cur_row = dict([(field, True) for field in enumerated_fields])
        cur_row['time'] = -1
        yield cur_row

def convert_pointtier_to_streamframe(pointtier):
    """Convert a Pointier into a StreamFrame

    Converts a PointTier imported from a textgrid into a Streamframe

    Arguments:
    pointtier -- The PoinTier to convert

    """
    streamframe = pointtier.copy()
    streamframe.index = streamframe[streamframe.columns[0]].values
    del streamframe[streamframe.columns[0]]
    return streamframe

def convert_streamframe_to_pointtier(streamframe, columns=None):
    """Convert a StreamFrame into a dictionary of PointTiers

    Converts a Streamframe into a dictionary of PointTiers.
    The column names of the stream frame becomes the dictionary keys
    The resulting dictionary can then be saved into a  Praat TextGrid
    with those Point Tiers.

    Arguments:
    streamframe -- the input streamframe

    Keyword Arguments:
    columns -- list of columns to convert. Each column must exist
               in the streamframe

    """
    pointdict = {}
    if columns is None:
        columns = streamframe.columns
    for col in columns:
        pointdict[col] = pd.DataFrame({col: streamframe[col],
                                       'time': streamframe.index.values},
                                      columns=['time', col])
        pointdict[col] = pointdict[col].reset_index(drop=True)
    return pointdict
