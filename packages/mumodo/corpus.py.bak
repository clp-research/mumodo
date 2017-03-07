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

"""corpus.py -- corpus and resource management

Functions and classes to create mumodos (multimodal documents) with
resource objects that abstract away from the actual data files.

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

import yaml, os, codecs, pickle
from moviepy.editor import VideoFileClip, AudioFileClip
from mumodo.mumodoIO import open_streamframe_from_xiofile,\
                            open_intervalframe_from_textgrid
from mumodo.analysis import slice_intervalframe_by_time, get_tier_type, \
                            slice_pointframe_by_time
from PIL import Image
import pandas as pd

__all__ = [
    # Classes
    'Resource', 'CSVResource', 'ImageResource', 'TextResource',
    'BinaryResource', 'BaseAVResource', 'BaseStreamResource',
    'BaseTierResource', 'AudioResource', 'VideoResource',
    'XIOStreamResource', 'CSVStreamResource', 'PickledStreamResource',
    'TextGridTierResource', 'CSVTierResource', 'PickledTierResource',
    'Mumodo',
    # Functions
    'serialize_mumodo', 'build_mumodo', 'read_mumodo_from_file',
    'write_mumodo_to_file'
    ]

class Resource(object):
    """ A mumodo resource abstract class

    Resources can be any form of data (e.g. video, audio, motion capture)

    The object describes the resource, how it can be retrieved from a file,
    and a sensible way to display the data, or cut a slice of the data. This
    is is a base class used to derive children for specific resource types.

    However, this class is useful for naming resources that are not covered
    by the children classes (yet) but should neverthelees  be part of a
    mumodo.

    """
    def __init__(self, **kwargs):
        """ Default constructor that is always called by all resources

        possible kwargs:

        name -- The name of the resource. It is preferably short and
                concise

        description -- A description of the resource (text)

        filename -- The name of the file this resource can be retrieved from.

        units -- The units used for the time axis of this resource. It is useful
                 to define this in order to perform slicing

        """
        if 'name' in kwargs:
            self.__name__ = kwargs['name']
        else:
            self.__name__ = None
        if 'description' in kwargs:
            self.__description__ = kwargs['description']
        else:
            self.__description__ = None
        if 'filename' in kwargs:
            self.__filename__ = kwargs['filename']
        else:
            self.__filename__ = None
        if 'units' in kwargs:
            self.__units__ = kwargs['units']
        else:
            self.__units__ = None

        self.__cached_object__ = None
        self.__rtype__ = 'GenericResource'
        self.__path_prefix__ = None

    def __repr__(self):
        return "{}\nname: {}\ndescription: {}\nfilename: {}\nunits: {}\n".\
               format(self.__class__.__name__,
                      self.__name__,
                      self.__description__,
                      self.__filename__,
                      self.__units__)

    def __toyaml__(self):
        return {'name': self.__name__, 'description': self.__description__,
                'filename': self.__filename__, 'units': self.__units__}

    def __load__(self):
        if self.__filename__ is None:
            print "No filename has been linked to this resource."
            return -1

        if not os.path.isfile(self.get_filepath()):
            print "The specified file does not exist"
            return -1
        return 0

    def get_name(self):
        """ Get the name of the resource

        """
        return self.__name__

    def get_type(self):
        """ Get the type of the resource

        """
        return self.__rtype__

    def get_units(self):
        """ Get the units of the resource

        """
        return self.__units__

    def set_units(self, units):
        """ Set the units of the resource

        """
        self.__units__ = units

    def set_path_prefix(self, prefix):
        """ Set the path prefix of the resource

        In general, resource filenames are looked for in a path set
        for the mumodo they belong to. This function allows to override
        that setting and instead set another path to the resource's
        data.

        """
        self.__path_prefix__ = prefix

    def get_path_prefix(self):
        """ Get the path prefix of the resource

        """
        return self.__path_prefix__

    def get_filepath(self):
        if self.__path_prefix__ is None or not isinstance(self.__path_prefix__,
                                                          basestring):
            filepath = self.__filename__
        else:
            filepath = os.path.join(self.__path_prefix__, self.__filename__)
        return filepath

class CSVResource(Resource):
    """ A CSV resource coming from a CSV file

    The CSV resource represents data stored in CSV files, that are not
    StreamFrames or Tiers. For those you can use CSVStreamResource and
    CSVTierResource, respectively.

    Mumodo uses the Pandas library to handle CSV files, and will load
    any CSV file into a Pandas DataFrame. Check the documentation of
    pandas for more details.

    In addition to the base Resource class constructor, this constructor
    accepts the following additional kwargs:

    kwargs - a dictionary of kwargs that are passed to the Pandas
             DataFrame.from_csv constructor

    The CSV resource cannot be sliced by time

    """
    def __init__(self, **kwargs):
        super(CSVResource, self).__init__(**kwargs)
        self.__rtype__ = 'CSVResource'

        if 'kwargs' in kwargs:
            self.__kwargs__ = kwargs['kwargs']
        else:
            self.__kwargs__ = dict()

    def __repr__(self):
        return super(CSVResource, self).__repr__() + \
           "kwargs: {}\n".format(self.__kwargs__)

    def __toyaml__(self):
        return dict(super(CSVResource, self).__toyaml__().items() + \
           {'kwargs': self.__kwargs__}.items())

    def __load__(self):
        if super(CSVResource, self).__load__() < 0:
            return -1
        if self.__cached_object__ is None:
            self.__cached_object__ = pd.DataFrame.from_csv(\
                                            self.get_filepath(),
                                            **self.__kwargs__)
        return 0

    def show(self):
        """ Display the table

        This method simply prints the DataFrame with CSV data

        """
        if self.__load__() < 0:
            return -1
        print self.__cached_object__

    def get_table(self):
        """ Get the DataFrame object

        This method returns a Pandas DataFrame with the contents of the CSV

        """
        if self.__load__() < 0:
            return -1
        return self.__cached_object__


class BaseAVResource(Resource):
    """ A base AudioVisual Data Resource Class

    AV data are handled using the moviepy python package. This base class is
    used to derive children that handle specific AV resources, namely audio and
    video. As such, it should never be instantiated.

    """

    def __init__(self, **kwargs):
        super(BaseAVResource, self).__init__(**kwargs)
        self.__rtype__ = 'AVResource'

        if 'player' in kwargs:
            self.__player__ = kwargs['player']
        else:
            self.__player__ = None
        if 'channel' in kwargs:
            self.__channel__ = kwargs['channel']
        else:
            self.__channel__ = None

    def show(self):
        """Display the AV resource

        Dis(play) the AV using an external player. The player MUST have
        been set either during construction, or using the specified method

        """
        if self.__player__ is None:
            print "no player has been set - cannot show video"
            return -1

        if self.__load__() < 0:
            return -1

        if os.system("{} {}".format(self.__player__, self.get_filepath())) != 0:
            return "I couldn't play"

    def get_slice(self, t1, t2):
        """ Get a slice of the audio/video

        Gets a slice from the audio/video using moviepy's subclip method.
        See that method's documentation for formatting the times.

        """
        if self.__load__() < 0:
            print "No slice can be returned."
            return
        return self.__cached_object__.subclip(t1, t2)

    def set_player(self, player):
        """ Set the external Video player

        Set the external video player to a different one than the one that
        was defined during construction

        """
        self.__player__ = player

    def get_player(self):
        """ Get the external Video player

        Returns the external Video player that has been set

        """
        return self.__player__

    def set_channel(self, channel):
        """ Set the channel of the resource

        Set the channel of the resource for multichannel video files.

        """
        self.__channel__ = channel

    def get_channel(self):
        """ Get the channel of the resource

        Returns the channel of the resource for multichannel video files.

        """
        return self.__channel__


class VideoResource(BaseAVResource):
    """ A mumodo Video resource object

    A VideoResource is a type of resource based on Video files. This module
    uses moviepy.editor to handle video files and is thus limited to the
    formats supported by that package. This is a rich set of formats, as
    moviepy is based on ffmpeg.

    """
    def __init__(self, **kwargs):
        """ VideoResource Constructor

        In addition to the kwargs defined in the base Resource class
        constructor, the following kwargs can also be defined:

        player -- an external player (e.g. VLC, mplayer) that can play
                  the video files. The value must be the FULL path to
                  the executable, or the executable has to be in the
                  PATH

        channel -- In case of multi-channel videos, an identifier
                   (usually a number) of the channel

        """
        super(VideoResource, self).__init__(**kwargs)
        self.__rtype__ = 'VideoResource'

    def __repr__(self):
        return super(VideoResource, self).__repr__() + \
           "player: {}\nchannel: {}\n".format(self.__player__, self.__channel__)

    def __toyaml__(self):
        return dict(super(VideoResource, self).__toyaml__().items() + \
           {'player': self.__player__, 'channel': self.__channel__}.items())

    def __load__(self):
        if super(VideoResource, self).__load__() < 0:
            return -1
        if self.__cached_object__ is None:
            self.__cached_object__ = VideoFileClip(self.get_filepath())
        return 0

    def get_video(self):
        """ Get the video object of this resource

        Returns the data object itself (a moviepy VideoClip instance)

        """
        if self.__load__() < 0:
            print "No video can be returned."
            return
        return self.__cached_object__

class AudioResource(BaseAVResource):
    """ A mumodo Audio resource object

    An AudioResource is a type of resource based on Audio files. This module
    uses moviepy.editor to handle audio files and is thus limited to the
    formats supported by that package. This is a rich set of formats, as
    moviepy is based on ffmpeg.
    """
    def __init__(self, **kwargs):
        """ AudioResource Constructor

        In addition to the kwargs defined in the base Resource class
        constructor, the following kwargs can also be defined:

        player -- an external player (e.g. VLC, mplayer) that can play
                  the audio files. The value must be the FULL path to
                  the executable, or the executable has to be in the
                  PATH

        channel -- In case of multi-channel audios, an identifier
                   (usually a number) of the channel

        """
        super(AudioResource, self).__init__(**kwargs)
        self.__rtype__ = 'AudioResource'


    def __repr__(self):
        return super(AudioResource, self).__repr__() + \
           "player: {}\nchannel: {}\n".format(self.__player__, self.__channel__)

    def __toyaml__(self):
        return dict(super(AudioResource, self).__toyaml__().items() + \
           {'player': self.__player__, 'channel': self.__channel__}.items())

    def __load__(self):
        if super(AudioResource, self).__load__() < 0:
            return -1
        if self.__cached_object__ is None:
            self.__cached_object__ = AudioFileClip(self.get_filepath())
        return 0

    def get_audio(self):
        """ Get the audio object of this resource

        Returns the data object itself (a moviepy AudioClip instance)

        """
        if self.__load__() < 0:
            print "No audio can be returned."
            return
        return self.__cached_object__

class BaseStreamResource(Resource):
    """ An abstract StreamResource class

    This base StreamResource class serves as the parent for
    children with different methods of loading the StreamFrame

    """

    def __init__(self, **kwargs):
        super(BaseStreamResource, self).__init__(**kwargs)
        self.__rtype__ = 'StreamResource'

    def get_slice(self, t1, t2):
        if self.__load__() < 0:
            return
        return self.__cached_object__.ix[t1:t2]

    def show(self):
        if self.__load__() < 0:
            return
        print self.__cached_object__

    def get_streamframe(self):
        if self.__load__() < 0:
            print "No StreamFrame  can be returned."
            return
        return self.__cached_object__

class XIOStreamResource(BaseStreamResource):
    """ StreamFrame from XIO file

    This class implements a StreamFrame resource that is
    loaded from an XIO file.

    In addition to the base Resource kwargs, the constructor
    accepts additional kwargs:

    sensorname -- the XIO sensorname, which is the only mandatory
                  argument in order to open a streamframe from
                  an XIO file

    kwargs  -- a dictonary of kwargs to be passed to the function
               that parses the XIO file and returns the StreamFrame.
               Notably, an offset can be one of these. See the
               documentation of mumodo.mumodoIO for more information

    """
    def __init__(self, **kwargs):
        super(XIOStreamResource, self).__init__(**kwargs)

        if 'sensorname' in kwargs:
            self.__sensorname__ = kwargs['sensorname']
        else:
            self.__sensorname__ = None
        if 'kwargs' in kwargs:
            self.__kwargs__ = kwargs['kwargs']
        else:
            self.__kwargs__ = {}

    def __repr__(self):
        return super(XIOStreamResource, self).__repr__() + \
           "sensorname: {}\nkwargs: {}\n".format(self.__sensorname__,
                                                 self.__kwargs__)

    def __toyaml__(self):
        return dict(super(XIOStreamResource, self).__toyaml__().items() + \
           {'sensorname': self.__sensorname__,
            'kwargs': self.__kwargs__}.items())

    def __load__(self):
        if super(XIOStreamResource, self).__load__() < 0:
            return -1
        if self.__sensorname__ is None:
            print "No sensorname has been set."
            print "No StreamFrame can be created."
            return -1
        if self.__cached_object__ is None:
            print "Parsing XIO file (will be done only once)."
            print "Please wait ..."
            self.__cached_object__ = open_streamframe_from_xiofile\
                                     (self.get_filepath(),
                                      self.__sensorname__,
                                      **self.__kwargs__)
        return 0

class CSVStreamResource(BaseStreamResource):
    """ StreamFrame from CSV file

    This class implements a StreamFrame resource that is
    loaded from a CSV file.

    In addition to the base Resource kwargs, the constructor
    accepts additional kwargs:

    kwargs  -- a dictonary of kwargs to be passed to the pandas
               function that parses the CSV file and returns the
               StreamFrame. See Pandas documentation for more
               information (DataFrame.from_csv())

    """
    def __init__(self, **kwargs):
        super(CSVStreamResource, self).__init__(**kwargs)

        if 'kwargs' in kwargs:
            self.__kwargs__ = kwargs['kwargs']
        else:
            self.__kwargs__ = dict()

    def __repr__(self):
        return super(CSVStreamResource, self).__repr__() + \
           "kwargs: {}\n".format(self.__kwargs__)

    def __toyaml__(self):
        return dict(super(CSVStreamResource, self).__toyaml__().items() + \
           {'kwargs': self.__kwargs__}.items())

    def __load__(self):
        if super(CSVStreamResource, self).__load__() < 0:
            return -1
        if self.__cached_object__ is None:
            self.__cached_object__ = pd.DataFrame.from_csv(\
                                            self.get_filepath(),
                                            **self.__kwargs__)
        return 0

class PickledStreamResource(BaseStreamResource):
    """ Pickled StreamFrame Resource

    This class implements a previously pickled StreamFrame
    resource that is unpickled from a binary file.

    In addition to the base Resource kwargs, the constructor
    accepts no additional kwargs

    """
    def __load__(self):
        if super(PickledStreamResource, self).__load__() < 0:
            return -1
        if self.__cached_object__ is None:
            self.__cached_object__ = pickle.load(open(self.get_filepath(),
                                                      "rb"))
        return 0

class BaseTierResource(Resource):
    """ Base Tier Resource

    The BaseTierResource represents Interval or Point Tier resources,
    and serves as a parent for children that load tiers from different
    file types. IntervalTiers and PointTiers are Pandas DataFrames with
    specific column names and structure. See the documentation of mumodoIO
    for more information.

    """
    def __init__(self, **kwargs):
        super(BaseTierResource, self).__init__(**kwargs)
        self.__rtype__ = 'TierResource'

    def get_slice(self, t1, t2):
        if self.__load__() < 0:
            return
        tiertype = get_tier_type(self.__cached_object__)
        if tiertype == 'interval':
            return slice_intervalframe_by_time(self.__cached_object__, t1, t2)
        elif tiertype == 'point':
            return slice_pointframe_by_time(self.__cached_object__, t1, t2)

    def show(self):
        if self.__load__() < 0:
            return
        print self.__cached_object__

    def get_tier(self):
        if self.__load__() < 0:
            return
        return self.__cached_object__

class TextGridTierResource(BaseTierResource):
    """ Intervalframe or Pointframe from TextGrid

    The TextGridTierResource imports intervalframes or pointframes
    from Praat TextGrids. Additionally to the kwargs defined in the
    base Resource class, the following kwargs are additionaly defined:

    tiername -- the name of the tier for this resource

    """
    def __init__(self, **kwargs):
        super(TextGridTierResource, self).__init__(**kwargs)

        if 'tiername' in kwargs:
            self.__tiername__ = kwargs['tiername']
        else:
            self.__tiername__ = None

    def __repr__(self):
        return super(TextGridTierResource, self).__repr__() + \
           "tiername: {}\n".format(self.__tiername__)

    def __toyaml__(self):
        return dict(super(TextGridTierResource, self).__toyaml__().items() + \
           {'tiername': self.__tiername__}.items())

    def __load__(self):
        if super(TextGridTierResource, self).__load__() < 0:
            return -1
        if self.__tiername__ is None:
            print "No tiername has been set."
            print "No TierFrame can be created."
            return -1
        if self.__cached_object__ is None:
            self.__cached_object__ = open_intervalframe_from_textgrid\
                               (self.get_filepath())[self.__tiername__]
        return 0

    def set_tiername(self, tiername):
        """ Set the tiername for this tier resource

        Arguments:

        tiername -- the name of the tier to be read from the TextGrid

        """
        self.__tiername__ = tiername

    def get_tiername(self):
        """ Return  the tiername for this tier resource

        """
        return self.__tiername__

class CSVTierResource(BaseTierResource):
    """ Intervalframe or Pointframe from TextGrid

    The TextGridTierResource imports intervalframes or pointframes
    from CSV files. Additionally to the kwargs defined in the
    base Resource class, the following kwargs are additionaly defined:

    kwargs -- a dict of kwargs to be passed to the Pandas function that
              imports dataframes from CSV. Check pandas documentation for
              more information.

    """
    def __init__(self, **kwargs):
        super(CSVTierResource, self).__init__(**kwargs)

        if 'kwargs' in kwargs:
            self.__kwargs__ = kwargs['kwargs']
        else:
            self.__kwargs__ = dict()

    def __repr__(self):
        return super(CSVTierResource, self).__repr__() + \
           "kwargs: {}\n".format(self.__kwargs__)

    def __toyaml__(self):
        return dict(super(CSVTierResource, self).__toyaml__().items() + \
           {'kwargs': self.__kwargs__}.items())

    def __load__(self):
        if super(CSVTierResource, self).__load__() < 0:
            return -1
        if self.__cached_object__ is None:
            self.__cached_object__ = pd.DataFrame.from_csv(\
                                            self.get_filepath(),
                                            **self.__kwargs__)
        return 0

class PickledTierResource(BaseTierResource):
    """ Intervalframe or Pointframe from Pickled data

    The PickledTierResource imports intervalframes or pointframes
    from pickled files. Additionally to the kwargs defined in the
    base Resource class, no additional kwargs are  defined:

    """
    def __load__(self):
        if super(PickledTierResource, self).__load__() < 0:
            return -1
        if self.__cached_object__ is None:
            self.__cached_object__ = pickle.load(open(self.get_filepath(),
                                                      "rb"))
        return 0

class ImageResource(Resource):
    """ An image resource coming from an image file

    The Image resource represents simply an image. Mumodo uses the Python
    Image Library to handle image files. Check the documentation of this
    module for more details

    In addition to the base Resource class constructor, this constructor
    requires no additional kwargs.

    The Image resource cannot be sliced by time

    """
    def __init__(self, **kwargs):
        super(ImageResource, self).__init__(**kwargs)
        self.__rtype__ = 'ImageResource'

    def __load__(self):
        if super(ImageResource, self).__load__() < 0:
            return -1
        if self.__cached_object__ is None:
            self.__cached_object__ = Image.open(self.get_filepath())
        return 0

    def show(self):
        """ Display the image

        This method simply displays the image using the show() method of the
        PIL library

        """
        if self.__load__() < 0:
            return -1
        self.__cached_object__.show()

    def get_image(self):
        """ Get the image object

        This method returns a PIL Image object that represents the image.

        """
        if self.__load__() < 0:
            return -1
        return self.__cached_object__


class TextResource(Resource):
    """ A text resource coming from a text file

    The Text resource represents simply a text.

    In addition to the base Resource class constructor, this constructor
    has  the following optional kwargs:

    encoding -- the encoding of the text file. If not given the
                default is utf-8

    The Text resource cannot be sliced by time

    """
    def __init__(self, **kwargs):
        super(TextResource, self).__init__(**kwargs)
        self.__rtype__ = 'TextResource'

        if 'encoding' in kwargs:
            self.__encoding__ = kwargs['encoding']
        else:
            self.__encoding__ = 'utf-8'

    def __load__(self):
        if super(TextResource, self).__load__() < 0:
            return -1
        if self.__cached_object__ is None or self.__cached_object__.closed:
            self.__cached_object__ = codecs.open(self.get_filepath(),
                                                 "r",
                                                 encoding=self.__encoding__)
        return 0

    def __repr__(self):
        return super(TextResource, self).__repr__() + \
           "encoding: {}\n".format(self.__encoding__)

    def __toyaml__(self):
        return dict(super(TextResource, self).__toyaml__().items() + \
           {'encoding': self.__encoding__}.items())

    def show(self):
        """ Show text

        Simply print out the entire text

        """
        if self.__load__() < 0:
            return -1
        self.__cached_object__.seek(0)
        for line in self.__cached_object__:
            print line

    def get_encoding(self):
        """ Get the encoding of this text resource

        Returns the encoding of the file that this text resource
        is stored in

        """

        return self.__encoding__

    def get_text(self):
        """ Get the entire text

        Returns the text that is represented by this resource

        """
        if self.__load__() < 0:
            return -1
        text = ''
        self.__cached_object__.seek(0)
        for line in self.__cached_object__:
            text += line
        return text

    def get_file_object(self):
        """ Get the file object

        Returns the file object instead of the entire text. This is
        useful for big text files.

        """
        if self.__load__() < 0:
            return -1
        return self.__cached_object__

class BinaryResource(Resource):
    """ A binary data resource coming from a binary file

    The Binary resource represents binary data

    In addition to the base Resource class constructor, this constructor
    has no additioanl kwargs:

    The binary resource cannot be sliced by time, and cannot be shown, but
    the file object is returned for further operations

    """
    def __init__(self, **kwargs):
        super(BinaryResource, self).__init__(**kwargs)
        self.__rtype__ = 'BinaryResource'

    def __load__(self):
        if super(BinaryResource, self).__load__() < 0:
            return -1
        if self.__cached_object__ is None or self.__cached_object__.closed:
            self.__cached_object__ = open(self.get_filepath(), "rb")
        return 0

    def get_file_object(self):
        """ Get the file object

        Returns the file object instead of the entire text. This is
        useful for big text files.

        """
        if self.__load__() < 0:
            return -1
        return self.__cached_object__

class Mumodo(object):
    """ The mumodo corpus object """
    def __init__(self, **kwargs):
        """ The constructor of a Mumodo object

        Possible kwargs

        name -- The corpus name

        description --- A brief description

        url -- A list of remote urls where the corpus can be found.

        localpath -- A local path where the corpus can be found. This will
                     be a path prefix to all the files of this mumodo on disk

        files  -- A list of the corpus files

        Other instance variables initialized

        ID -- an ID that is shorter then the name and can be used as a key more
              reliably (e.g. has no spaces or special characters)

        Other instance variables initialized

        resources -- A dictionary of available resources in this Mumodo

        """
        if 'name' in kwargs:
            self.__name__ = kwargs['name']
        else:
            self.__name__ = None
        if 'description' in kwargs:
            self.__description__ = kwargs['description']
        else:
            self.__description__ = None
        if 'url' in kwargs:
            self.__url__ = kwargs['url']
        else:
            self.__url__ = None
        if 'localpath' in kwargs:
            self.__localpath__ = kwargs['localpath']
        else:
            self.__localpath__ = None
        if 'files' in kwargs:
            self.__files__ = kwargs['files']
        else:
            self.__files__ = []
        if 'ID' in kwargs:
            self.__ID__ = kwargs['ID']
        else:
            self.__ID__ = None
        if 'resources' in kwargs:
            self.__resources__ = kwargs['resources']
        else:
            self.__resources__ = dict()

        self.__parent__ = None

    def __repr__(self):
        return "{}\nname: {}\ndescription: {}\nurl: {}\nlocalpath: \
                {}\nfiles: {}\nID: \
                {}\nresources: {})".format(self.__class__.__name__,
                                           self.__name__,
                                           self.__description__,
                                           self.__url__,
                                           self.__localpath__,
                                           self.__files__,
                                           self.__ID__,
                                           self.__resources__.keys())

    def __toyaml__(self):
        return {'name': self.__name__, 'description': self.__description__,
                'url': self.__url__, 'localpath': self.__localpath__,
                'files': self.__files__, 'parent': self.__parent__,
                'ID': self.__ID__}

    def __getitem__(self, item):
        """ Access a resource by its name

        For convenience, the following expression will store a
        reference of the resource named 'myresource'

        >>> r = mymodo['myresource']

        Numerical access to resources is not supported, as it is
        not really needed.

        """
        if len(self.__resources__) <= 0:
            print "No resources have been defined yet!"
            return
        if item in self.__resources__:
            return self.__resources__[item]

    def __iter__(self):
        """ iterate over the resources of this Mumodo

        Mumodos are also iterable, which is helpful for lookups of
        resources with specific names or types

        """
        return (r for r in self.__resources__.values())

    def add_resource(self, resource):
        """ Add a resource to this mumodo

        The resource has to be an object of type mumodo.corpus.Resource
        or a derived type. In addition the new resource cannot have the
        same name as an existing resource with the same name.

        """

        if isinstance(resource, Resource):
            rname = resource.get_name()
            if rname is None or rname in self.__resources__:
                print "Resource must have a unique name!"
                return -1
            self.__resources__[rname] = resource
            resource.set_path_prefix(self.__localpath__)
            if resource.__filename__ not in self.__files__:
                self.__files__.append(resource.__filename__)

    def get_resource_names(self):
        """ Return the names of the resources attached to this Mumodo

        The function returns the names of the resources in alphabetical
        order.
        """
        return sorted(self.__resources__.keys())

    def set_localpath(self, path):
        """ Set the local path for this Mumodo

        This function updates each resource with a local path in which
        to look up the file associated with that resource.
        """
        self.__localpath__ = path
        for r in self.__resources__.values():
            r.set_path_prefix(path)

    def get_name(self):
        """ Return the name of this mumodo

        """
        return self.__name__

def serialize_mumodo(mumodo, default_flow_style=False):
    """ Create a human-readable and editable yaml dump

    Arguments:

    mumodo  -- a mumodo object, populated with subcorpora and sessions

    """

    ser = ""
    if isinstance(mumodo, Mumodo):
        ser += "!Mumodo\n"
        ser += yaml.dump(mumodo.__toyaml__(),
                         default_flow_style=default_flow_style)
        ser += "\n"
        for key in sorted(mumodo.__resources__.keys()):
            ser += "!{}\n".format(mumodo[key].__class__.__name__)
            ser += yaml.dump(mumodo[key].__toyaml__(),
                             default_flow_style=default_flow_style)
            ser += "\n"
    return ser

def build_mumodo(stream):
    """ Build and populate Mumodo object(s) from a human-readable yaml dump

    Returns a list of populated mumodo objects

    Arguments

    stream -- a character stream

    """

    blockbuffer = ''
    mumodolist = []
    object_type = None
    keys = {'Mumodo': Mumodo,
            'VideoResource': VideoResource,
            'AudioResource': AudioResource,
            'XIOStreamResource': XIOStreamResource,
            'CSVStreamResource': CSVStreamResource,
            'PickledStreamResource': PickledStreamResource,
            'TextGridTierResource': TextGridTierResource,
            'CSVTierResource': CSVTierResource,
            'PickledTierResource': PickledTierResource,
            'ImageResource': ImageResource,
            'TextResource': TextResource,
            'Resource': Resource,
            'BinaryResource': BinaryResource,
            'CSVResource': CSVResource}
    for line in stream.split('\n'):
        #do we have a new block?
        if len(line) > 0 and line[0] == '!' or len(line) == 0:
            if len(blockbuffer) > 0:
                kwargs = yaml.load(blockbuffer)
                blockbuffer = ''
            #Create the object here
            if object_type in keys.keys():
                obj = keys[object_type](**kwargs)

                #build the object tree
                if isinstance(obj, Mumodo):
                    mumodolist.append(obj)
                elif isinstance(obj, Resource):
                    mumodolist[-1].add_resource(obj)

            object_type = line[1:]
            continue

        blockbuffer += line
        blockbuffer += '\n'
    return mumodolist

def read_mumodo_from_file(filepath, encoding='utf-8'):
    """ Read mumodos from a file on disk

    Reads the file and returns a list of mumodos found
    in the file

    Arguments:

    filepath -- a valid filepath

    Kwargs:

    encoding -- a valid encoding supported by the Python codecs
                package

    """
    if not os.path.isfile(filepath):
        print "file does not exist!"
        return

    inser = ""
    with codecs.open(filepath, "r", encoding=encoding) as f:
        for line in f:
            inser += line
    return build_mumodo(inser)

def write_mumodo_to_file(mumodos, filepath, encoding='utf-8'):
    """ Write mumodos to a file on disk

    Write a mumodo or a list of mumodos to the file

    Arguments:

    mumodos -- A list of mumodo objects (may contain a single object)

    filepath -- a valid filepath

    kwargs:

    encoding -- a valid encoding supported by the Python codecs
                package

    """

    ser = ''
    for mumodo in mumodos:
        ser += serialize_mumodo(mumodo)

    with codecs.open(filepath, "w", encoding=encoding) as f:
        f.write(ser)
