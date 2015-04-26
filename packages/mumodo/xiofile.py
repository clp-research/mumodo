"""xiofile.py: Classes and functions handling XIO files

   XIO files are shallow XML representations of typed, timed events.
   The format was originally created by the AI Group, University of
   Bielefeld. XIO files are typically compressed using the gzip
   library.

   This module contains the XIOFile class, which handles the file I/O
   and allows quering the XIO files and seeking fast within them using
   a pre-indexing mechanism.

   Functions that operate on XIOFile objects could also be found here,
   e.g. xiofile_quickcopy, a function that can copy a (region of) XIO
   file into a new file

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

import gzip
from mumodo.InstantIO import *

__all__ = [
    # Classes
    'XIOFile',
    # Functions
    'xiofile_quickcopy'
    ]

class XIOFile(object):

    """Load, index and query xio.gz files output by FAME logging tool."""

    def __init__(self, path, mode='r', maxlines=0, indexing=False,
                 headerlines=2, fileformat="venice"):
        """Handles compressed XIO file I/O.

        Opens a compressed xio.gz file. This file is produced by legacy
        fame logger as well as venice logger.
        The file contains line terminated events that consist of a value,
        type, timestamp, and value(sensor) name

        Available modes:
        'r'    --  Opens a compressed xio.gz file and creates a line
                   index and a time index for fast seeking.
        'w'    --  Creates a new xio.gz file and handles write to it.

        Keyword args:
        maxlines    --  The number of lines to index. Can be used to
                        index a subset of the lines in case of a very
                        long file
        indexing    --  Performs indexing of lines and creates lookup
                        tables for quick seeking.
        headerlines --  The number of lines taken by the file  header.
                        These lines are ignored
        fileformat  --  The XML format to use when writing. Possible
                        values:
                        "legacy" - The old TechFak format
                        "venice" - (default) the newer, shorter format

        """
        self.mode = mode
        self.indexed = indexing
        self.headerlines = headerlines
        if self.mode == 'r':
            #dictionary of fieldnames {sensorname: fieldnames}
            self.fieldnames = {}
            #open the file
            with open(path) as f:
                self.is_gzipped = (f.read(2) == '\x1f\x8b')
            if self.is_gzipped:
                print 'opening compressed file ...'
                self.f = gzip.open(path)
            else:
                print 'opening un-compressed file ...'
                self.f = open(path)
            if self.indexed == False:
                print 'opening file without indexing'
                # Skip the header lines
                for _ in range(self.headerlines):
                    self.f.readline()
                #the next line contains the 1st timestamp
                #self.min_time = self.xio_parseline(self.f.readline())['time']
                #self.f.seek(0)
                line = self.f.readline()
                while self.xio_parseline(line)['time'] < 0 and line != '':
                    line = self.f.readline()
                if self.xio_parseline(line)['time'] >= 0:
                    self.min_time = self.xio_parseline(line)['time']
                else:
                    print 'no valid lines found!'
                #exit the constructor here if not indexing
                return
            self.xio_index(maxlines)
        elif self.mode == "w":
            if fileformat in ['legacy', 'venice']:
                self.f = gzip.open(path, "w")
                self.xioformat = fileformat
                self.xio_writeheader()
            else:
                print "unsupported file format."
                print " Only 'legacy' and 'venice' allowed"
        else:
            print "unsupported mode. Only 'r' and 'w' allowed"




    def xio_index(self, maxlines):
        """Perform indexing of an input XIO file """
        #Set up structures for indexing
        #List of file offsets every 1000 lines
        self.line_offset = []
        #list of flie offsets every 1 sec (1000ms)
        self.time_offset = []
        #file indexing: populate line_offset every 1000 lines
        #time_offset every (approximately) one second
        #and fill fieldnames dictionary
        offset = 0 #cumulative byte offset
        toffset = 0 #last timestamp that was indexed
        tcurrent = 0 #current timestamp
        print 'indexing ...'
        for i, line in enumerate(self.f):
            #do not look at the header lines. indexing starts
            #from the first line after the headerlines
            #Break if specified number of lines is reached
            if maxlines > 0 and (i - self.headerlines) > maxlines:
                break
            #Create an index every 1000 lines
            if (i - self.headerlines) % 1000 == 0:
                self.line_offset.append(offset)
            #Create an index every (approximately 1000ms
            if i > (self.headerlines - 1):
                parsedline = self.xio_parseline(line)
                tcurrent = parsedline['time']
                if tcurrent == -1:
                    print 'unable to parse line ', i, ' ', line
                elif not hasattr(self, 'min_time'):
                    self.min_time = tcurrent
                if tcurrent - toffset >= 1000:
                    self.time_offset.append(offset)
                    toffset = tcurrent
                #populate fieldnames dictionary
                sname = parsedline['sensorname']
                fname = parsedline['fieldname']
                if sname not in self.fieldnames:
                    self.fieldnames[sname] = []
                if fname not in self.fieldnames[sname]:
                    self.fieldnames[sname].append(fname)
            #add to byte offset
            offset += len(line)
            #show progress
            if (i - self.headerlines) % 1000000 == 0:
                linecount = (i - self.headerlines) / 1000000
                if linecount > 0:
                    print linecount, 'million lines'
            #first two and last line do not contain data
            self.max_lines = i - self.headerlines - 1
        #self.min_time = self.xio_parseline_lineno(0)['time']
        self.max_time = self.xio_parseline_lineno(self.max_lines)['time']
        print 'done! (indexed ' + str(self.max_lines + 1) + ' lines)'


    def xio_quicklinegen(self, start_time, end_time, parsed=True,
                         relative=True, on_errors='ignore'):
        """Quickly generate a timestamp range for un-indexed files.

        Arguments:
        start_time, end_time    --  The desired time range.
        start_time = 0 means start reading from the first line of the file.
        end_time = 0 means read until the end of the file.

        Keyword argumetns:
        parsed      --  Flag to yield parsed or non-parsed output.
        relative    --  Flag to toggle between absolute and relative
                        timestamps. Relative timestamps have the zero
                        at min_time (the first timestamp in the file)
        on_errors   --  Flag to toggle between different ways of
                        handling unparseable lines. If on_errors is
                        'ignore' (default), unparseable lines will
                        be skipped without warning. If on_errors is
                        'report', a warning will be printed. If
                        on_errors is 'stop', the generator will stop
                        at the first unparseable line; an additional
                        warning will be printed.


        """

        errors = ['ignore', 'report', 'stop']
        if relative:
            start_time += self.min_time
            if end_time > 0:
                end_time += self.min_time
        #self.f.seek(0)
        #length = len([li for n, li in enumerate(self.f)]) - 1
        self.f.seek(0)
        for i, line in enumerate(self.f):
            #Ignore 8the header lines
            if i <= (self.headerlines - 1):
                continue

            parsedline = self.xio_parseline(line)
            tcurrent = parsedline["time"]

            if tcurrent < 0:
                if errors.index(on_errors) > 0:
                    print "line " + str(i - self.headerlines) + " not parseable"
                if errors.index(on_errors) > 1:
                    break
                continue  #for clarity

            if tcurrent < start_time:
                continue

            if end_time > 0 and tcurrent > end_time:
                break

            yield parsedline if parsed else line

    def xio_quicksearch(self, timestamp, restart=True):
        """Quick searching of a timestamp for un-indexed files.

        Search if a timestamp exists in the file. Useful function for
        finding offsets between XIO files and other formats, such as
        videos. Returns True,timestamp if timestap is found or
        False, timestamp (the next one) if not

        Arguments:
        timestamp    --  The timestamp sought after.
                     Use absolute times only (for now).


        Keyword argumetns:
        restart --  Flag to begin searching from the beginning of
                    the file (for consecutive searches)

        """
        if restart:
            self.f.seek(0)
        for i, line in enumerate(self.f):
            #Ignore the header lines
            if i > (self.headerlines - 1):
                parsedline = self.xio_parseline(line)
                tcurrent = parsedline["time"]
                if tcurrent == timestamp:
                    return (True, tcurrent)
                elif tcurrent > timestamp:
                    return (False, tcurrent)
        return (False, tcurrent, "end of file")

    def xio_seek(self, lineno=0):
        """Seek up to a line by looking up the line_offset list.

        Keyword arguments:
        lineno    --  The line number to seek to.

        """
        if self.indexed == False:
            return False

        #find the nearest line_offset index and offset from there
        offset_index = (lineno) / 1000
        self.f.seek(self.line_offset[offset_index])
        #readin x-1 lines where x is the offset from the last 1000_line_offset
        i = 0
        while i < (lineno%1000):
            self.f.readline()
            i += 1

    def xio_timeseek(self, timestamp=0, relative=True):
        """Seek to the first line with a specified timestamp
        by looking up the time_offset list.

        parameter:
        timestamp    --  The time to seek to (in ms)
        relative    --  Flag to toggle between absolute and relative
                        timestamps. Relative timestamps have the zero
                        at min_time (the first timestamp in the file)

        returns:
        False if timeseeking fails
        The first line found with the requested timestamp

        """
        if self.indexed == False:
            return False

        if relative:
            timestamp += self.min_time
        if timestamp < self.min_time or timestamp > self.max_time:
            return False
        #find the nearest time_offset index and offset from there
        offset_index = (timestamp - self.min_time) / 1000 - 1
        self.f.seek(self.time_offset[offset_index])
        #seek back if erroneoulsy sought too far
        while (self.xio_parseline(self.f.readline())['time'] > timestamp) and \
              (offset_index >= 0):
            offset_index -= 1
            self.f.seek(self.time_offset[offset_index])
        if offset_index == -1:
            self.f.seek(0)
        #readin lines until timestamp is found
        line = self.f.readline()
        while self.xio_parseline(line)['time'] < timestamp:
            line = self.f.readline()
        return line


    def xio_getline(self, lineno=0):
        """Retrieve a line from a previously opened and indexed XIO file.

        Returns the line identified by lineno

        Keyword arguments:
        lineno    --  A line number.

        """
        if lineno < 0 or lineno > self.max_lines:
            return "line number out of range"
        #seek to the line no
        self.xio_seek(lineno)
        #read the line
        return self.f.readline()

    def xio_getline_attime(self, timestamp=0, relative=True):
        """Retrieve a line from a previously opened and indexed XIO file.

        Returns the first line found at timestamp

        Keyword arguments:
        timestamp    --  A timestamp.
        relative     --  Toggle between relative and absolute timestamps
                         Relative timestamps have their zero at min_time
                         (the first timestamp in the file)

        """
        #seek to the first line with this timestamp
        line = self.xio_timeseek(timestamp, relative)
        if line:
            #read the line
            return line
        else:
            return "time out of range"

    def xio_parsename(self, line='//'):
        """Parse a '/' delimited sensorname.

        Parse the long sensor name into sensor name and
        field name. the field name is only the last token

        Keyword arguments:
        line    --  A '/' delimited string.

        """
        field = line.split('/')[-1]
        sensor = line[:-(len(field)+1)]
        return (sensor, field)

    def xio_parseline(self, line=' '):
        """Parse a raw xioline

        Parse a line from a previously opened XIO file.
        Return a dictionary describing the data.

        Returns error codes in the 'time' key of the dictionary:
        -2 means line was parsed but the data type could not parse
        -1 measn the line was not parsed (the line is passed as the
        value)

        Keyword arguments:

        line    --  A line.
        """
        try:
            #support legacy format from fame logger that had
            # an ":" character in the type
            if ':' not in line.split(" ")[0]:
                line = '<:' + line.split('<')[1]
            #get the sensor_name, value type, value and timestamp of event
            value_type = line.split(' ')[0].split(":")[1]
            sensor_name = line.split('sensorName="')[1].split('"')[0]
            value = line.split('value="')[1].split('"')[0]
            timestamp = line.split('timestamp="')[1].split('"')[0]

            #extract the field (slot) name from the sensor name
            sensor_name, field_name = self.xio_parsename(sensor_name)

            #pack everything into a dict
            values = {'valuetype': value_type,
                      'value': self.xio_parsetypes(value, value_type.lower()),
                      'sensorname': sensor_name, 'fieldname': field_name,
                      'time': int(timestamp)}

            #if the type is not supported return an error code of -2
            if str(values['value']).startswith('KeyError'):
                values['time'] = -2
        except IndexError:
            values = {'valuetype': '', 'value': line, 'sensorname': '',
                      'fieldname': '', 'time': -1}
        return values

    def xio_parsetypes(self, value, otype):
        """Convert string value_types into suitable object types.

           The type names are coded as strings. This function
           assigns an appropriate parsing function to the value,
           according to a lookup table.

           Arguments

           value -- The value
           otype -- The string that describes the type (must be all lowercase)

           If type is not found in the lookup table, the returned value is
           a string starting with 'KeyError', followed by the type

        """
        # Dict of functions for parsing sensor values
        # appropriate to each input type.
        parsing_fn = {'sffloat' : float,
                      'sfvec3f' : SFVec3f,
                      'sfvec2f' : SFVec2f,
                      'mfvec2f' : MFVec2f,
                      'mfvec3f' : MFVec3f,
                      'sfrotation' : SFRotation,
                      'mfrotation' : MFRotation,
                      'sfbool' : sfbool,
                      'boolean': sfbool,
                      'sfint32' : int,
                      'sfstring' : str,
                      'mfstring': MFString,
                      'mffloat': MFFloat}
        try:
            converted = parsing_fn[otype](value)
        except KeyError:
            converted = 'KeyError:' + str(otype)
        return converted

    def xio_parseline_lineno(self, lineno=0):
        """Parse a numbered line from a previously opened and
           indexed XIO file.

        Keyword arguments:
        lineno    --  A line number.

        """
        return self.xio_parseline(self.xio_getline(lineno))

    def xio_parseline_attime(self, timestamp=0, relative=True):
        """Parse a line at a specific timestamp from a previously
           opened and indexed XIO file.

        Keyword arguments:
        timestamp    --  the reuested time. If several lines have the
                         same timestamp, only the fisrt is parsed
        relative     --  Toggle between relative and absolute timestamps
                         Relative timestamps have their zero at min_time
                         (the first timestamp in the file)

        """
        return self.xio_parseline(self.xio_getline_attime(timestamp, relative))



    def xio_linegen(self, start=0, end=1, parsed=True, on_errors='ignore'):

        """Generate a (raw or parsed) line range from a previously
           opened and indexed XIO file.

        Keyword arguments:
        start,end    -- The line range.
        parsed       -- Toggle between raw or parsed output lines
        on_errors    -- Flag to toggle between different ways of
                        handling unparseable lines. If on_errors is
                        'ignore' (default), unparseable lines will
                        be skipped without warning. If on_errors is
                        'report', a warning will be printed. If
                        on_errors is 'stop', the generator will stop
                        at the first unparseable line; an additional
                        warning will be printed.


        """


        if start > end or self.xio_getline(start) == \
                          "line number out of range" \
                       or self.xio_getline(end) == "line number out of range":
            yield "bad limits or limits out of range"
        else:
            self.xio_seek(start)
            i = start
            errors = ['ignore', 'report', 'stop']
            while i <= end:
                line = self.f.readline()
                if not parsed:
                    yield line
                    continue
                #else:
                parsedline = self.xio_parseline(line)
                tcurrent = parsedline["time"]
                #errors = ['ignore', 'report', 'stop']
                if tcurrent < 0:
                    if errors.index(on_errors) > 0:
                        print "line " + str(i) + " not parseable"
                    if errors.index(on_errors) > 1:
                        break


                else:
                    yield parsedline

                i += 1




    def xio_linegen_timerange(self, start_time, end_time, relative=True,
                              parsed=True, on_errors='ignore'):
        """Generate a (parsed or raw) line range from a previously
           opened and indexed XIO file.

        Arguments:
        start_time, end_time -- timestamp range.

        Keyword arguments:
        relative     --  Toggle between relative and absolute timestamps
                         Relative timestamps have their zero at min_time
                         (the first timestamp in the file)
        parsed -- Toggle between raw or parsed output lines

        """
        errors = ['ignore', 'report', 'stop']
        line = self.xio_timeseek(start_time, relative)
        if start_time > end_time:
            yield "bad limits"
        elif not line:
            yield "time out of range" #exit if seeking was unsuccessful
        else:
            if relative:
                end_time += self.min_time
                start_time += self.min_time
            tcurrent = start_time
            parsedline = self.xio_parseline(line)
            while tcurrent <= end_time and line != '':
                if tcurrent > 0:
                    yield parsedline if parsed else line
                else:
                    if errors.index(on_errors) > 0:
                        print "unparseable line: " + line
                    if errors.index(on_errors) > 1:
                        break

                line = self.f.readline()
                parsedline = self.xio_parseline(line)
                tcurrent = parsedline["time"]

    def xio_formatline(self, value_type, value, sensorname, fieldname,
                       timestamp):
        """Format a raw XIO line for output from the given input

        Arguments:
        value_type  -- A string describing the object type
        value       -- The value of the object
        sensorname  -- possibly '/' delimited string describing the
                       sensor, or namespace of this field
        fieldname   -- The name of the field
        timestamp   -- The timestamp of this line

        """
        string = {}
        string['legacy'] = '<irio:' + str(value_type) + ' value="' + \
                           str(value) + '" sensorName="xioFileClass/' + \
                           str(sensorname) + '/' + str(fieldname) + \
                           '" timestamp="' + str(timestamp) + '"></irio:' + \
                           str(value_type) + '>' +'\n'
        string['venice'] = '<' + str(value_type) + ' value="' + \
                           str(value) + '" timestamp="' + str(timestamp) + \
                           '" sensorName="' + str(sensorname) + '/' + \
                           str(fieldname) + '"/>'  +'\n'
        return string[self.xioformat]

    def xio_writeheader(self):
        """Write the header to the output XIO file"""
        self.xio_writeline('<?xml version="1.0" encoding="utf-8"?>'+'\n')
        string = {}
        string['legacy'] = ('<instantioprotocol xmlns="http://www.techfak.uni'
                            '-bielefeld.de/ags/wbski/instantloggerprotocol"'
                            ' xmlns:irio="http://www.techfak.uni-bielefeld.de'
                            '/ags/wbski/instantloggerprotocol/interaction"'
                            ' version="1">')
        string['venice'] = ('<veniceprotocol info="venice file format '
                            'generated by mumodo" version="1.0">')
        self.xio_writeline(string[self.xioformat] + '\n')

    def xio_writeline(self, line):
        """Write a line to an XIO file previously opened for writing """

        self.f.write(line)

    def xiofile_close(self):
        """Close a previously opened xio File."""

        string = {}
        string['legacy'] = '</instantioprotocol>'
        string['venice'] = '</veniceprotocol>'

        if self.mode == 'w':
            self.xio_writeline(string[self.xioformat])
        self.f.close()



def xiofile_quickcopy(origin_file, new_file, start_time=0, end_time=0,
                      relative=True):
    """Copy a part of a XIOFile to a new file.

    Arguments:
    origin_file        --  Filename and path of the file to copy.
    new_file           --  Filename and path of the new file.

    Keyword arguments:
    start_time,end_time  --  Time range which should be copied. Default
                             values copy the entire file.
    relative     --  Toggle between relative and absolute timestamps
                     Relative timestamps have their zero at min_time
                     (the first timestamp in the file)

    """
    infile = XIOFile(origin_file, 'r', indexing=False)
    oufile = XIOFile(new_file, 'w')
    for line in infile.xio_quicklinegen(start_time, end_time, parsed=False,
                                        relative=relative):
        oufile.xio_writeline(line)
    infile.xiofile_close()
    oufile.xiofile_close()
