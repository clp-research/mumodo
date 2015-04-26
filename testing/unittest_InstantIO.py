####################################################################
#                                                  __              #
#             ____ ___  __  ______ ___  ____  ____/ /___           #
#            / __ `__ \/ / / / __ `__ \/ __ \/ __  / __ \          #
#           / / / / / / /_/ / / / / / / /_/ / /_/ / /_/ /          #
#          /_/ /_/ /_/\__,_/_/ /_/ /_/\____/\__,_/\____/           #
#                                  www.dsg-bielefeld.de            #
####################################################################

__author__ = "Gerdis Anderson"
__copyright__ = "Dialogue Systems Group Bielefeld - www.dsg-bielefeld.de"
__credits__ = ["Gerdis Anderson"]
__license__ = "GPL"
__version__ = "0.1.1"
__maintainer__ = "Spyros Kousidis"
__status__ = "Development" # Development/Production/Prototype

####################################################################

import unittest
from mumodo.InstantIO import sfbool, SFVec3f, SFVec2f, SFRotation, MFVec2f, \
                             MFVec3f, MFRotation, MFString, MFFloat

class instant_testing(unittest.TestCase):

    def test_SFVec3f(self):
        self.failUnlessEqual(SFVec3f('1 3 4').v, [1.0, 3.0, 4.0])
        self.failUnlessEqual(SFVec3f('2 8 3').x, 2.0)
        self.failUnlessEqual(SFVec3f('2 8 3').y, 8.0)
        self.failUnlessEqual(SFVec3f('2 8 3').z, 3.0)
        self.failUnlessEqual(SFVec3f(2.5, 'a').v, [-1.0, -1.0, -1.0])
        self.failUnlessEqual(SFVec3f('1 4 3')[1], 4.0)
        self.failUnlessEqual(str(SFVec3f(3.4, 5.6, 2.3)), '3.4 5.6 2.3')
        self.failUnlessEqual(list(SFVec3f('1 3 4')), [1.0, 3.0, 4.0])

    def test_SFVec2f(self):
        self.failUnlessEqual(SFVec2f('1 2').v, [1.0, 2.0])
        self.failUnlessEqual(SFVec2f(1.2, 3.4).v, [1.2, 3.4])
        self.failUnlessEqual(SFVec2f(1.2, 3.4).x, 1.2)
        self.failUnlessEqual(SFVec2f(1.2, 3.4).y, 3.4)
        self.failUnlessEqual(SFVec2f(3.2, 'c').v, [-1.0, -1.0])
        self.failUnlessEqual(SFVec2f('5 6')[1], 6.0)
        self.failUnlessEqual(str(SFVec2f(6.3, 9.8)), '6.3 9.8')
        self.failUnlessEqual(list(SFVec2f(1.2, 3.4)), [1.2, 3.4])

    def test_SFRotation(self):
        self.failUnlessEqual(SFRotation('1 2 3 4').v, [1.0, 2.0, 3.0, 4.0])
        self.failUnlessEqual(SFRotation(1.2, 3.4, 2.4, 7.6).v,
                             [1.2, 3.4, 2.4, 7.6])
        self.failUnlessEqual(SFRotation(1.2, 3.4, 5.4, 2.4).qx, 1.2)
        self.failUnlessEqual(SFRotation(1.2, 3.4, 3.6, 1.4).qy, 3.4)
        self.failUnlessEqual(SFRotation(1.2, 3.4, 3.6, 1.4).qz, 3.6)
        self.failUnlessEqual(SFRotation(1.2, 3.4, 3.6, 1.4).qw, 1.4)
        self.failUnlessEqual(SFRotation(1.2, 3.4, 3.6).v,
                             [-1.0, -1.0, -1.0, -1.0])
        self.failUnlessEqual(SFRotation(1.2, 3.4, 3.6, 5.7, 2.5).v,
                             [-1.0, -1.0, -1.0, -1.0])
        self.failUnlessEqual(SFRotation(1.2).qx, -1.0)
        self.failUnlessEqual(SFRotation('1 4 3 6')[1], 4.0)
        self.failUnlessEqual(str(SFRotation(3.4, 5.6, 2.3, 8.9)),
                             '3.4 5.6 2.3 8.9')
        self.failUnlessEqual(list(SFRotation(1, 4, 3, 6)),
                             [1.0, 4.0, 3.0, 6.0])

    def test_MFVec3f(self):
        self.failUnlessEqual(str(type(MFVec3f("[2.0 4.0 6.0,"
                  " 3.0 5.0 7.0]")[1])), "<class 'mumodo.InstantIO.SFVec3f'>")
        self.failUnlessEqual(str(MFVec3f([SFVec3f(x, x, x) \
                 for x in range(10)])[2]), '2.0 2.0 2.0')
        self.failUnlessEqual(str(MFVec3f(['1 0 0', '2 0 0', '-1 0 0'])[2]),
                             '-1.0 0.0 0.0')
        self.failUnlessEqual(str(MFVec3f("[a 4.0 6.0, 3.0 b 5.0]")[0]),
                             '-1.0 -1.0 -1.0')
        self.failUnlessEqual(MFVec3f("[2.0 4.0 6.0, 3.0 5.0 7.0]")[0].z, 6.0)
        self.failUnlessEqual(str(MFVec3f("[2.0 4.0 6.0, 3.0 5.0 7.0]")),
                             '[2.0 4.0 6.0, 3.0 5.0 7.0]')
        self.failUnlessEqual(str(MFVec3f("[2.0 4.0 6.0, 3.0 5.0 7.0]")[1]),
                             '3.0 5.0 7.0')
        self.failUnlessEqual([str(x) for x in MFVec3f("[2.0 4.0 6.0, "
               "3.0 5.0 7.0]")], ['2.0 4.0 6.0', '3.0 5.0 7.0'])
        self.failUnlessEqual(list(MFVec3f("[2.0 4.0 6.0, "
               "3.0 5.0 7.0]"))[1].x, 3.0)
        self.failUnlessEqual(len(MFVec3f("[2.0 4.0 6.0, 3.0 5.0 7.0]")), 2)
        self.failUnlessEqual(len(MFVec3f([])), 0)


    def test_MFVec2f(self):
        self.failUnlessEqual(str(type(MFVec2f("[2.0 4.0, 3.0 5.0]")[1])),
                             "<class 'mumodo.InstantIO.SFVec2f'>")
        self.failUnlessEqual(str(MFVec2f([SFVec2f(x, x) \
                               for x in range(10)])[2]), '2.0 2.0')
        self.failUnlessEqual(str(MFVec2f(['1 0', '-1 0'])[1]),
                             '-1.0 0.0')
        self.failUnlessEqual(str(MFVec2f("[a 4.0, 3.0 b]")[0]),
                             '-1.0 -1.0')
        self.failUnlessEqual(MFVec2f("[2.0 4.0, 3.0 5.0]")[0].y, 4.0)
        self.failUnlessEqual(str(MFVec2f("[2.0 4.0, 3.0 5.0]")),
                             '[2.0 4.0, 3.0 5.0]')
        self.failUnlessEqual(str(MFVec2f("[2.0 4.0, 3.0 5.0]")[1]),
                             '3.0 5.0')
        self.failUnlessEqual([str(x) for x in MFVec2f("[2.0 4.0, 3.0 5.0]")],
                             ['2.0 4.0', '3.0 5.0'])
        self.failUnlessEqual(list(MFVec2f("[2.0 4.0, 3.0 5.0]"))[1].x, 3.0)
        self.failUnlessEqual(len(MFVec2f("[2.0 4.0, 3.0 5.0]")), 2)
        self.failUnlessEqual(len(MFVec2f([])), 0)


    def test_MFRotation(self):
        self.failUnlessEqual(str(type(MFRotation("[1.0 2.0 3.0 4.0,"
                  " 5.0 6.0 7.0 8.0]")[1])),
                  "<class 'mumodo.InstantIO.SFRotation'>")
        self.failUnlessEqual(str(MFRotation([SFRotation(x, x, x, x) \
                 for x in range(10)])[2]), '2.0 2.0 2.0 2.0')
        self.failUnlessEqual(str(MFRotation(['1 0 0 1',
                                             '2 0 0 1',
                                             '-1 0 0 1'])[2]),
                             '-1.0 0.0 0.0 1.0')
        self.failUnlessEqual(str(MFRotation("[a 2.0 4.0 6.0, 1.0 3.0 b]")[0]),
                             '-1.0 -1.0 -1.0 -1.0')
        self.failUnlessEqual(MFRotation("[1.0 2.0 3.0 4.0, "
                                        "5.0 6.0 7.0 8.0]")[0].qy, 2.0)
        self.failUnlessEqual(str(MFRotation("[1.0 2.0 3.0 4.0, "
                                             "5.0 6.0 7.0 8.0]")),
                             '[1.0 2.0 3.0 4.0, 5.0 6.0 7.0 8.0]')
        self.failUnlessEqual(str(MFRotation("[1.0 2.0 3.0 4.0, "
                                             "5.0 6.0 7.0 8.0]")[1]),
                             '5.0 6.0 7.0 8.0')
        self.failUnlessEqual([str(x) for x in MFRotation("[1.0 2.0 3.0 4.0, "
                                                          "5.0 6.0 7.0 8.0")],
                              ['1.0 2.0 3.0 4.0', '5.0 6.0 7.0 8.0'])
        self.failUnlessEqual(list(MFRotation("[1.0 2.0 3.0 4.0, "
               "5.0 6.0 7.0 8.0]"))[1].qw, 8.0)
        self.failUnlessEqual(len(MFRotation("[1.0 2.0 3.0 4.0, "
                                             "5.0 6.0 7.0 8.0]")), 2)

        self.failUnlessEqual(len(MFRotation([])), 0)

    def test_MFString(self):
        self.failUnlessEqual(str(type(MFString("[a, b, c]")[1])),
                             "<type 'str'>")
        self.failUnlessEqual(MFString([str(x) for x in range(10)])[2], '2')
        self.failUnlessEqual(MFString(['a', 'b'])[1], 'b')
        self.failUnlessEqual(str(MFString("[a, b, c]")), '[a, b, c]')
        self.failUnlessEqual(list(MFString("[a, b, c]")), ['a', 'b', 'c'])
        self.failUnlessEqual(len(MFString("[a, b, c]")), 3)
        self.failUnlessEqual(len(MFString([])), 0)

    def test_MFFloat(self):
        self.failUnlessEqual(str(type(MFFloat("[0.1, 0.2, 0.3]")[1])),
                             "<type 'float'>")
        self.failUnlessEqual(MFFloat(range(10))[2], 2.0)
        self.failUnlessEqual(MFFloat([0.1, 0.2])[1], 0.2)
        self.failUnlessEqual(str(MFFloat("[0.1, 0.2, 0.3]")), '[0.1, 0.2, 0.3]')
        self.failUnlessEqual(list(MFFloat("[0.1, 0.2, 0.3]")), [0.1, 0.2, 0.3])
        self.failUnlessEqual(len(MFFloat("[0.1, 0.2, 0.3]")), 3)
        self.failUnlessEqual(len(MFFloat([])), 0)

    def test_sfbool(self):
        self.assertTrue(sfbool("True"))
        self.assertTrue(sfbool("TRUE"))
        self.assertTrue(sfbool("truE"))
        self.assertFalse(sfbool("yes"))

if __name__ == "__main__":
    unittest.main()
