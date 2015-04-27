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

""" InstantIO.py - implementation of InstantIO types in Python

    This module implements some of the InstantIO types [more info
    on these can be found at www.instantreality.org]

    The types are defined in two flavors:

    Single field types (SF) are implemented as classes, with accessors
    for the individual attributes

    Multiple field types (MF) are implemented as functions that return
    lists of the respective SF objects

    Accessing individual objects requires nothing more then ordinary
    list item access, hence no need to define a new class

    The constructors of the classes (as well as the mf functions) take
    string input and pack the data as (in case of MF, lists of) objects.
    The opposite transformation is achieved by str for the objects. Lists
    need to be iterated over and printed if one doesn't want the brackets
    in the produced string  [ str(mylist)[1:-1]  ]
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

from math import atan2, asin, pi

__all__ = [
    # Classes
    'SFVec3f', 'SFVec2f', 'SFRotation', 'MFVec3f',
    'MFVec2f', 'MFRotation', 'MFString', 'MFFloat',
    # Functions
    'sfbool'
    ]

class SFVec3f(object):

    """Parse and return SFVec3f values from Instant Reality."""

    def getv(self):
        return [self.__x, self.__y, self.__z]
    def getx(self):
        return self.__x
    def setx(self, value):
        self.__x = value
    def gety(self):
        return self.__y
    def sety(self, value):
        self.__y = value
    def getz(self):
        return self.__z
    def setz(self, value):
        self.__z = value

    x = property(fget=getx, fset=setx, doc="x")
    y = property(fget=gety, fset=sety, doc="y")
    z = property(fget=getz, fset=setz, doc="z")
    v = property(fget=getv, doc="v")

    def __init__(self, *args):
        """Create a new SFVec3f object.

        Arguments:
        Can be called either with string inputs (space separated):

        >>> print SFVec3f('3 5 9')
        3.0 5.0 9.0

        or with three float arguments:

        >>> SFVec3f(1.2, 3.4, 1.3).v
        [1.2, 3.4, 1.3]

        if the input consists of a wrong number of arguments (neither 1
        nor 3), or any of the arguments is not a float,
        the 'error' object (-1 -1 -1) is constructed:

        >>> print(SFVec3f('a b'))
        -1.0 -1.0 -1.0

        the error object is also constructed if the number of arguments in
        the string does not equal 3:

        >>> SFVec3f('hallo').v
        [-1.0, -1.0, -1.0]

        the single positions of the constructed object can be indexed:

        >>> SFVec3f(1.2, 2.9, 2.4).x
        1.2

        >>> SFVec3f(1.2, 2.9, 2.4).y
        2.9

        >>> SFVec3f(1.2, 2.9, 2.4).z
        2.4

        """
        if len(args) == 1:
            if type(args[0]) is str:
                items = args[0].split(' ')
                args = items
        if len(args) == 3:
            try:
                args = [float(x) for x in args]

            except ValueError:
                args = [-1.0, -1.0, -1.0]
        else:
            args = [-1.0, -1.0, -1.0]

        self.__x = args[0]
        self.__y = args[1]
        self.__z = args[2]

    def __str__(self):
        return ' '.join([str(x) for x in self.v])

    def __getitem__(self, i):
        try:
            return self.v[i]
        except IndexError:
            return

    def __iter__(self):
        return (i for i in self.v)


class SFVec2f(object):

    """Parse and return SFVec2f values from Instant Reality."""

    def getv(self):
        return [self.__x, self.__y]
    def getx(self):
        return self.__x
    def setx(self, value):
        self.__x = value
    def gety(self):
        return self.__y
    def sety(self, value):
        self.__y = value

    x = property(fget=getx, fset=setx, doc="x")
    y = property(fget=gety, fset=sety, doc="y")
    v = property(fget=getv, doc="v")

    def __init__(self, *args):
        """Create a new SFVec2f object.

        Arguments:
        Can be called either with string inputs (space separated):

        >>> SFVec2f('1 2').v
        [1.0, 2.0]

        or with two floats:

        >>> print(SFVec2f(3.4, 5.6))
        3.4 5.6

        if the input consists of a wrong number of arguments (neither 1
        nor 2), or any of the arguments is not a float,
        the 'error' object (-1 -1) is constructed:

        >>> print(SFVec2f(1.3, 5.6, 1.5, 7.8))
        -1.0 -1.0

        >>> print(SFVec2f(1.3,'d', 2.4))
        -1.0 -1.0

        the single positions of the created object can be indexed:

        >>> SFVec2f(1.3,'d', 2.4).x
        -1.0

        >>> SFVec2f('3.5 4.2').y
        4.2

        """
        if len(args) == 1:
            if type(args[0]) is str:
                items = args[0].split(' ')
                args = items
        if len(args) == 2:
            try:
                args = [float(x) for x in args]
            except ValueError:
                args = [-1.0, -1.0]
        else:
            args = [-1.0, -1.0]

        self.__x = args[0]
        self.__y = args[1]

    def __str__(self):
        return ' '.join([str(x) for x in self.v])

    def __getitem__(self, i):
        try:
            return self.v[i]
        except IndexError:
            return

    def __iter__(self):
        return (i for i in self.v)


class SFRotation(object):
    """ parse and return SFRotation values from Instant Reality """

    def getv(self):
        return [self.__qx, self.__qy, self.__qz, self.__qw]
    def getbank(self):
        return self.__bank
    def getheading(self):
        return self.__heading
    def getattitude(self):
        return self.__attitude
    def getqx(self):
        return self.__qx
    def setqx(self, value):
        self.__qx = value
        self.__convert_to_euler__()
    def getqy(self):
        return self.__qy
    def setqy(self, value):
        self.__qy = value
        self.__convert_to_euler__()
    def getqz(self):
        return self.__qz
    def setqz(self, value):
        self.__qz = value
        self.__convert_to_euler__()
    def getqw(self):
        return self.__qw
    def setqw(self, value):
        self.__qw = value
        self.__convert_to_euler__()

    qx = property(fget=getqx, fset=setqx, doc="qx")
    qy = property(fget=getqy, fset=setqy, doc="qy")
    qz = property(fget=getqz, fset=setqz, doc="qz")
    qw = property(fget=getqw, fset=setqw, doc="qw")
    bank = property(fget=getbank, doc="bank")
    heading = property(fget=getheading, doc="heading")
    attitude = property(fget=getattitude, doc="attitude")
    v = property(fget=getv, doc="v")

    def __init__(self, *args):
        """ create a new SFRotation object in quaternion notation

        arguments:
        can be called with a space separated string (4 tokens)

        >>> print SFRotation('2.5 -3 0 5')
        2.5 -3.0 0.0 5.0

        or four float arguments

        >>> print SFRotation(2.5, -3, 0, 5)
        2.5 -3.0 0.0 5.0

        if the number of arguments is not 4 (in the string also) or
        any of the arguments is not a float, the 'error' object (-1 -1 -1 -1)
        is constructed

        >>> print SFRotation('a', -0, 'b')
        -1.0 -1.0 -1.0 -1.0

        You can get elements of the quaternion (qx, qy, qz, qw)

        >>> SFRotation('2.5 -3 0 5').qx
        2.5

        Or get Euler angles in radians (heading, bank, attitude)

        >>> SFRotation('0 0 0 1').bank
        0.0

        Or the entire quaternion in 'vector' form

        >>> SFRotation('0 0 0 1').v
        [0.0, 0.0, 0.0, 1.0]

        """

        if len(args) == 1:
            if type(args[0]) is str:
                items = args[0].split(' ')
                args = items
        if len(args) == 4:

            try:
                args = [float(x) for x in args]

            except ValueError:
                args = [-1.0, -1.0, -1.0, -1.0]
        else:
            args = [-1.0, -1.0, -1.0, -1.0]

        #Create the object
        self.__qx = args[0]
        self.__qy = args[1]
        self.__qz = args[2]
        self.__qw = args[3]
        self.__convert_to_euler__()

    def __convert_to_euler__(self):
        """ Convert Quaternion to Euler angles

        Performs a transformation of the quaternion into Euler angles,
        by means of the atan2 function. Checks for singularties
        in order to avoid division by zero errors.

        The function sets the attributtes __heading, __bank, and
        __attitude, without returning anything

        The computed angles are in radians
        """
        qx = self.__qx
        qy = self.__qy
        qz = self.__qz
        qw = self.__qw
        qx2 = qx * qx
        qy2 = qy * qy
        qz2 = qz * qz
        qw2 = qw * qw
        unit = qx2 + qy2 + qz2 + qw2
        if unit == 0:
            self.__heading = self.__bank = self.__attitude = 0.0
            return
        test = qx*qy+qz*qw
        if test > 0.499*unit:
            self.__heading = 2 * atan2(qx, qw)
            self.__attitude = pi / 2
            self.__bank = 0.0
            return
        elif test < -0.499*unit:
            self.__heading = -2 * atan2(qx, qw)
            self.__attitude = pi / -2
            self.__bank = 0.0
            return
        else:
            self.__heading = atan2(2 * qy * qw - 2 * qx * qz,
                                   qx2 - qy2 - qz2 + qw2)
            self.__bank = atan2(2 * qx * qw - 2 * qy * qz,
                                qy2 - qx2 + qw2 - qz2)
            self.__attitude = asin(2 * test / unit)
            return

    def __str__(self):
        return ' '.join([str(x) for x in self.v])

    def __getitem__(self, i):
        return self.v[i]

    def __iter__(self):
        return (i for i in self.v)


class  MFFloat(object):
    "Parse an InstantIO mfstring. """

    def __init__(self, args):
        """Create an MFFloat object

        arguments:
        A single string with items separated by comma-space, enclosed
        in square brackets, or

        A list of floats (or numbers that will be cast to floats)

        The object holds the floats internally as a list:

        >>> list(MFFloat("[0, 1.2, 2]"))
        [0, 1.2, 2]

        Items that cannot be cast to floats yield NaN:

        >>> list(MFFloat('[a, 5, f]'))
        [nan, 5.0, nan]

        Element access, slicing and iteration are supported:

        >>> MFFloat("[0, 1.2, 2]")[0]
        0

        >>> MFFloat("[0, 1.2, 2]")[:-1]
        [0, 1.2]

        >>> [x*x for x in MFFloat("[1, 2, 3]")]
        [1, 4, 9]

        The lenght of an MFFloat object can be queried:

        >>> len(MFFloat("[0, 1.2, 2]"))
        3

        The string representaion of the object is the InstantIO style:
        >>> print MFFloat("[0, 1.2, 2])
        '[0, 1.2, 2]'

        """
        self.__v = []
        #is input just a string repr of MFFloat?
        if type(args) is str:
            try:
                concat = args.split('[')[1].split(']')[0]
            except IndexError:
                concat = ''
            if len(concat) == 0:
                return
            for i in concat.split(', '):
                try:
                    self.__v.append(float(i))
                except ValueError:
                    self.__v.append(float('nan'))
        #is it a collection of objects?
        else:
            #is this object iterable?
            try:
                for obj in args:
                    #can this token be cast to a float?
                    try:
                        self.__v.append(float(obj))
                    except ValueError:
                        self.__v.append(float('nan'))
            except TypeError:
                self.__v.append(float('nan'))

    def __str__(self):
        return '[' + ', '.join([str(x) for x in self.__v]) + ']'

    def __getitem__(self, i):
        try:
            return self.__v[i]
        except IndexError:
            return

    def __setitem__(self, i, value):
        try:
            self.__v[i] = str(value)
        except IndexError:
            return

    def __iter__(self):
        return (i for i in self.__v)

    def __len__(self):
        return len(self.__v)

class  MFString(object):
    "Parse an InstantIO mfstring. """

    def __init__(self, args):
        """Create an MFString object

        arguments:
        A single string with items separated by comma-space, enclosed
        in square brackets, or

        A list of objects, which will be cast into strings

        The object holds the strings internally as a list

        >>> list(MFString("[a, b, c]"))
        ['a', 'b', 'c']

        The length of an MFString object can be queried:

        >>> len(MFString("[a, b, c]"))
        3

        The string representaion of the object is the InstantIO style:
        >>> print  MFString("[a, b, c]")
        '[a, b, c]'

        """
        self.__v = []
        #is input just a string repr of MFString?
        if type(args) is str:
            try:
                concat = args.split('[')[1].split(']')[0]
            except IndexError:
                concat = ''
            if len(concat) == 0:
                return
            for i in concat.split(', '):
                self.__v.append(i)
        #is it a collection of objects?
        else:
            try:
                for obj in args:
                    self.__v.append(str(obj))
            except TypeError:
                self.__v.append('')

    def __str__(self):
        return '[' + ', '.join([str(x) for x in self.__v]) + ']'

    def __getitem__(self, i):
        try:
            return self.__v[i]
        except IndexError:
            return

    def __setitem__(self, i, value):
        try:
            self.__v[i] = str(value)
        except IndexError:
            return

    def __iter__(self):
        return (i for i in self.__v)

    def __len__(self):
        return len(self.__v)


class MFVec2f(object):

    """Parse and return MFVec2f values from Instant Reality."""

    def __init__(self, args):
        """Create a new MFVec2f object.

        An MFVec2f object is an array (list) of SFVec2f objects. The
        MFVec2f class encapsulates the list allowing accessing of the
        elements, while checking that each element is of the correct
        type (SFVec2f)

        arguments:
        Can be called with a string corresponding to the mfvec2f-type:
        Each comma separated sub-string has 3 space-separated floats,
        and becomes an SFVec2f object, which can be accessed by its
        index in the (MFVec2f) array:

        >>> print MFVec2f("[2.0 4.0, 3.0 5.0]")[1]
        3.0 5.0

        A list of SFVec2f objects can also be used to construct an
        instance of MFVec2f:

        >>> print MFVec2f([SFVec2f(x,x) for x in range(10)])[2]
        2.0 2.0

        A list of strings that represent SFVec2f objects can also
        be used:

        >>> print MFVec2f(['1 0', '2 0', '-1 0'])[2]
        -1.0 0.0

        If any of the tokens using any of the three input methods
        is not an instance of or cannot be parsed into an SFVec2f
        (incorrect number/type of arguments, wrong object type),
        that token is parsed into the SFVec2f error object
        SFVec2f('-1.0 -1.0'), e.g.:

        >>> print MFVec2f("[2.0 4.0 6.0 4.0, 3.0 5.0]")[0]
        -1.0 -1.0

        >>> print MFVec2f("[a 4.0, 3.0 5.0]")[0]
        -1.0 -1.0

        As each item is a SFVec2f object, you can access its own
        elements as usual:

        >>> print MFVec2f("[2.0 4.0, 3.0 5.0]")[0].y
        4.0

        The length of an MFVec2f object can be queried:

        >>> len(MFVec2f("[2.0 4.0, 3.0 5.0]"))
        2

        The str function of an MFVec2f object yields an MFVec2f
        formatted string, rather than a list of object refs, e.g:

        >>> print MFVec2f([SFVec2f(x, x) for x in range(3)])
        [0.0 0.0, 1.0 1.0, 2.0 2.0]

        """
        self.__v = []
        #is input just a string repr of MFVec2f?
        if type(args) is str:
            try:
                concat = args.split('[')[1].split(']')[0]
            except IndexError:
                concat = ''
            if len(concat) == 0:
                return
            for i in concat.split(', '):
                self.__v.append(SFVec2f(i))
        #is it a collection of objects?
        else:
            try:
                for obj in args:
                    self.__v.append(self.__parseintosfvec2f__(obj))
            except TypeError:
                self.__v.append(SFVec2f(-1, -1))

    def __parseintosfvec2f__(self, value):
        if isinstance(value, SFVec2f):
            return value
        else:
            return SFVec2f(value)

    def __str__(self):
        return '[' + ', '.join([str(x) for x in self.__v]) + ']'

    def __getitem__(self, i):
        try:
            return self.__v[i]
        except IndexError:
            return

    def __setitem__(self, i, value):
        try:
            self.__v[i] = self.__parseintosfvec2f__(value)
        except IndexError:
            return

    def __iter__(self):
        return (i for i in self.__v)

    def __len__(self):
        return len(self.__v)


class MFVec3f(object):

    """Parse and return MFVec3f values from Instant Reality."""

    def __init__(self, args):
        """Create a new MFVec3f object.

        An MFVec3f object is an array (list) of SFVec3f objects. The
        MFVec3f class encapsulates the list allowing accessing of the
        elements, while checking that each element is of the correct
        type (SFVec3f)

        arguments:
        Can be called with a string corresponding to the mfvec3f-type:
        Each comma separated sub-string has 3 space-separated floats,
        and becomes an SFVec3f object, which can be accessed by its
        index in the (MFVec3f) array:

        >>> print MFVec3f("[2.0 4.0 6.0, 3.0 5.0 7.0]")[1]
        3.0 5.0 7.0

        A list of SFVec3f objects can also be used to construct an
        instance of MFVec3f:

        >>> print MFVec3f([SFVec3f(x,x,x) for x in range(10)])[2]
        2.0 2.0 2.0

        A list of strings that represent SFVec3f objects can also
        be used:

        >>> print MFVec3f(['1 0 0', '2 0 0', '-1 0 0'])[2]
        -1.0 0.0 0.0

        If any of the tokens using any of the three input methods
        is not an instance of or cannot be parsed into an SFVec3f
        (incorrect number/type of arguments, wrong object type),
        that token is parsed into the SFVec3f error object
        SFVec3f('-1.0 -1.0 -1.0'), e.g.:

        >>> print MFVec3f("[2.0 4.0 6.0 4.0, 3.0 5.0]")[0]
        -1.0 -1.0 -1.0

        >>> print MFVec3f("[a 4.0 6.0, 3.0 b 5.0]")[0]
        -1.0 -1.0 -1.0

        As each item is a SFVec3f object, you can access its own
        elements as usual:

        >>> print MFVec3f("[2.0 4.0 6.0, 3.0 5.0 7.0]")[0].z
        6.0

        The length of an MFVec3f object can be queried:

        >>> len(MFVec3f("[2.0 4.0 6.0, 3.0 5.0 7.0]"))
        2

        The str function of an MFVec3f object yields an MFVec3f
        formatted string, rather than a list of object refs, e.g:

        >>> print MFVec3f("[2.0 4.0 6.0, 3.0 5.0 7.0]").__str__()
        '[2.0 4.0 6.0, 3.0 5.0 7.0]'

        >>> print MFVec3f([SFVec3f(x,x,x) for x in range(3)])
        [0.0 0.0 0.0, 1.0 1.0 1.0, 2.0 2.0 2.0]

        """
        self.__v = []
        #is input just a string repr of MFVec3f?
        if type(args) is str:
            try:
                concat = args.split('[')[1].split(']')[0]
            except IndexError:
                concat = ''
            if len(concat) == 0:
                return
            for i in concat.split(', '):
                self.__v.append(SFVec3f(i))
        #is it a collection of objects?
        else:
            try:
                for obj in args:
                    self.__v.append(self.__parseintosfvec3f__(obj))
            except TypeError:
                self.__v.append(SFVec3f(-1, -1, -1))

    def __parseintosfvec3f__(self, value):
        if isinstance(value, SFVec3f):
            return value
        else:
            return SFVec3f(value)

    def __str__(self):
        return '[' + ', '.join([str(x) for x in self.__v]) + ']'

    def __getitem__(self, i):
        try:
            return self.__v[i]
        except IndexError:
            return

    def __setitem__(self, i, value):
        try:
            self.__v[i] = self.__parseintosfvec3f__(value)
        except IndexError:
            return

    def __iter__(self):
        return (i for i in self.__v)

    def __len__(self):
        return len(self.__v)

class MFRotation(object):

    """Parse and return MFRotation values from Instant Reality."""

    def __init__(self, args):
        """Create a new MFRotation object.

        An MFRotation object is an array (list) of SFRotation objects. The
        MFRotation class encapsulates the list allowing accessing of the
        elements, while checking that each element is of the correct
        type (SFRotation)

        arguments:
        Can be called with a string corresponding to the mfrotation-type:
        Each comma separated sub-string has 3 space-separated floats,
        and becomes an SFRotation object, which can be accessed by its
        index in the (MFRotation) array:

        >>> print MFRotation("[1.0 2.0 3.0 4.0, 5.0 6.0 7.0 8.0]")[0]
        1.0 2.0 3.0 4.0

        A list of SFRotation objects can also be used to construct an
        instance of MFRotation:

        >>> print MFRotation([SFRotation(x, x, x, x) for x in range(10)])[2]
        2.0 2.0 2.0 2.0

        A list of strings that represent SFRotation objects can also
        be used:

        >>> print MFRotation(['1 0 0 1', '2 0 0 1', '-1 0 0 1'])[2]
        -1.0 0.0 0.0 1.0

        If any of the tokens using any of the three input methods
        is not an instance of or cannot be parsed into an SFRotation
        (incorrect number/type of arguments, wrong object type),
        that token is parsed into the SFRotation error object
        SFRotation('-1.0 -1.0 -1.0 -1.0'), e.g.:

        >>> print MFRotation("[2.0 4.0 6.0, 5.0 6.0 7.0 8.0]")[0]
        -1.0 -1.0 -1.0 -1.0

        >>> print MFRotation("[a 4.0,  5.0 6.0 7.0 8.0]")[0]
        -1.0 -1.0 -1.0 -1.0

        As each item is a SFRotation object, you can access its own
        elements as usual:

        >>> print MFRotation("[1.0 2.0 3.0 4.0, 5.0 6.0 7.0 8.0]")[0].qy
        2.0

        The length of an MFRotation object can be queried:

        >>> len(MFRotation("[1.0 2.0 3.0 4.0, 5.0 6.0 7.0 8.0]"))
        2

        The str function of an MFRotation object yields an MFRotation
        formatted string, rather than a list of object refs, e.g:

        >>> print MFRotation([SFRotation(x, x, x, x) for x in range(2)])
        [0.0 0.0 0.0 0.0, 1.0 1.0 1.0 1.0]

        """
        self.__v = []
        #is input just a string repr of MFRotation?
        if type(args) is str:
            try:
                concat = args.split('[')[1].split(']')[0]
            except IndexError:
                concat = ''
            if len(concat) == 0:
                return
            for i in concat.split(', '):
                self.__v.append(SFRotation(i))
        #is it a collection of objects?
        else:
            try:
                for obj in args:
                    self.__v.append(self.__parseintosfrotation__(obj))
            except TypeError:
                self.__v.append(SFRotation(-1, -1, -1, -1))

    def __parseintosfrotation__(self, value):
        if isinstance(value, SFRotation):
            return value
        else:
            return SFRotation(value)

    def __str__(self):
        return '[' + ', '.join([str(x) for x in self.__v]) + ']'

    def __getitem__(self, i):
        try:
            return self.__v[i]
        except IndexError:
            return

    def __setitem__(self, i, value):
        try:
            self.__v[i] = self.__parseintosfrotation__(value)
        except IndexError:
            return

    def __iter__(self):
        return (i for i in self.__v)

    def __len__(self):
        return len(self.__v)


def sfbool(string):
    """ Parse a string into a boolean value

    The string "true" regradless of case  parses to True.
    Everything else parses to False.

    If anything other than a string is passed, an
    exception (ValueError) is raised.

    """
    return string.lower() == 'true'
