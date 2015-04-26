import unittest, math, os
from mumodo.xiofile import XIOFile, xiofile_quickcopy

class XioTest(unittest.TestCase):

    def setUp(self):
        #Test of an indexed file
        self.f = XIOFile('data/types.xio.gz', indexing=True)
        #Test of an indexed file with a preset number of lines
        self.j = XIOFile('data/types.xio.gz', 'r', 10, indexing=True)
        #Test of an an-unidexed file, now default
        self.g = XIOFile('data/types.xio.gz', indexing=False)
        #Test write mode (old legacy format)
        self.h = XIOFile('data/trywriting.xio.gz', 'w', fileformat='legacy')
        self.h.xio_writeline('<irio:sfint32 value="35" '
                             'sensorName="xioFileClass/desk3/skeletonCount" '
                             'timestamp="13765381"></irio:sfint32>\n')
        self.h.xio_writeline(self.h.xio_formatline('sfint32', 37, 'desk3',
                                                   'skeletonCount', 13765381))
        self.h.xiofile_close()
        #Test write mode (new default venice format)
        self.l = XIOFile('data/trywriting2.xio.gz', 'w')
        self.l.xio_writeline(self.l.xio_formatline('sfint32', 37, 'desk3',
                                                   'skeletonCount', 13765381))
        self.l.xiofile_close()
        #Test write mode, by opening the file previously written to
        self.i = XIOFile('data/trywriting.xio.gz', 'r', indexing=True)
        self.m = XIOFile('data/trywriting2.xio.gz', 'r', indexing=True)
        #Test copy utility, copy part of the file to a new file
        xiofile_quickcopy('data/types.xio.gz', 'data/newtypes.xio.gz', 0, 5)
        #Test result of copy, by loading the copy
        self.k = XIOFile('data/newtypes.xio.gz', 'r', indexing=True)
        #Test of an un-compressed file
        self.n = XIOFile('data/types.xio', indexing=True)
        #File to specifically test line ranges
        self.o = XIOFile('data/linestest.xio.gz', indexing=True)
        #Similar for unindexed mode
        self.p = XIOFile('data/linestest.xio.gz')
        self.n = XIOFile('data/types.xio', indexing=True)
        self.q = XIOFile('data/parsing5.xio.gz', indexing=True)
        self.nr = XIOFile('data/unreadable.xio.gz')

    def test_xiofile_indexed(self):
        self.failUnlessEqual(str(type(self.f)),
                             '<class \'mumodo.xiofile.XIOFile\'>')
        self.failUnlessEqual(self.f.mode, 'r')
        self.failUnlessEqual(self.f.indexed, True)
        self.failUnlessEqual(self.f.max_lines, 15)
        self.failUnlessEqual(self.f.min_time, 1376571532081L)
        self.failUnlessEqual(self.f.max_time, 1376571532082L)
        self.failUnlessEqual(self.f.xio_getline(2), '<irio:sfint32 xmlns="'
             '" xmlns:ns3="http://www.techfak.uni-bielefeld.de/ags/wbski/'
             'instantloggerprotocol" value="2" timestamp="1376571532081" '
             'sensorName="dsglab-desk-3/skeletonCount" '
             'type="Sample"></irio:sfint32>\n')
        self.failUnlessEqual(self.f.xio_getline_attime(1376571532081,
                                                       relative=False),
                              '<irio:sfint32 xmlns="" xmlns:ns3="http://'
                              'www.techfak.uni-bielefeld.de/ags/wbski/'
                              'instantloggerprotocol" value="90310" '
                              'timestamp="1376571532081" sensorName="dsglab'
                              '-desk-3/framenumber" type="Sample">'
                              '</irio:sfint32>\n')
        self.failUnlessEqual(self.f.xio_getline_attime(1), '<irio:mfvec3f xmln'
             's="" xmlns:ns3="http://www.techfak.uni-bielefeld.de/ags/wbski/in'
             'stantloggerprotocol" value="[0.2124978 -0.1224827 1.858883, 0.30'
             '30231 -0.1534625 1.925013, 0.01070284 -0.04043572 1.811359, 0.51'
             '68817 0.04873443 1.994409, 0.209666 -0.148198 1.78842, 0.299611 '
             '-0.1756292 1.85338, -0.01972085 -0.3181056 1.753447, 0.5168398 -'
             '0.1499471 1.939156, 0.2531285 0.3707453 1.670671, 0.2336805 0.03'
             '969637 1.820125, 0.1654053 -0.02932697 1.817514, 0.3024898 -0.02'
             '393005 1.848226, 0.4543798 0.03429135 1.977719, 0.5566682 -0.032'
             '79109 2.062352, 0.234128 0.2108699 1.780103, 0.1076903 0.1457002'
             ' 1.790787, 0.3986858 0.1662227 1.876898, 0.2335398 0.06816141 1.'
             '811909, -0.01211493 -0.2486881 1.766024, 0.5297669 -0.1118848 1.'
             '973672]" timestamp="1376571532082" sensorName="dsglab-desk-3/joi'
             'ntPositions3D1" type="Sample"></irio:mfvec3f>\n')
        self.failUnlessEqual(self.f.xio_parseline_lineno(5),
                             {'valuetype': 'sffloat',
                              'fieldname': 'soundAngle',
                              'sensorname': 'dsglab-desk-3',
                              'value': -24.015615,
                              'time': 1376571532081L})
        self.failUnlessEqual(self.f.xio_parseline_attime(),
                             {'valuetype': 'sfint32',
                              'fieldname': 'framenumber',
                              'sensorname': 'dsglab-desk-3',
                              'value': 90310, 'time': 1376571532081L})
        self.failUnlessEqual([l for l in self.f.xio_linegen(0, 5)][2],
                             {'valuetype': 'sfint32',
                              'fieldname': 'skeletonCount',
                              'sensorname': 'dsglab-desk-3',
                              'value': 2, 'time': 1376571532081L})
        self.failUnlessEqual(list(self.f.xio_linegen_timerange(0, 10))[3],
                             {'valuetype': 'sffloat',
                              'fieldname': 'interactionSpace',
                              'sensorname': 'dsglab-desk-3',
                              'value': 0.083201334,
                              'time': 1376571532081L})
        self.failUnlessEqual(len(list(self.q.xio_linegen_timerange(0, 4,
                                                        on_errors='stop'))), 4)
        self.failUnlessEqual(list(self.q.xio_linegen_timerange(1, 4,
             on_errors='stop'))[0]['value'], 2)


    def test_xiofile_lesslines(self):
        self.failUnlessEqual(self.j.mode, 'r')
        self.failUnlessEqual(self.j.indexed, True)
        self.failUnlessEqual(self.j.max_lines, 9)
        self.failUnlessEqual(self.j.max_time, 1376571532081L)
        self.failUnlessEqual(self.j.xio_getline(8), '<irio:mfvec3f xmlns="" '
             'xmlns:ns3="http://www.techfak.uni-bielefeld.de/ags/wbski/instan'
             'tloggerprotocol" value="[0.0 0.0 0.0, 0.0 0.0 0.0, 0.0 0.0 0.0, '
             '0.1671641 -0.3231136 1.178103, 0.2154177 0.04740157 1.772092, '
             '0.0 0.0 0.0]" timestamp="1376571532081" sensorName="dsglab-desk'
             '-3/positions3D" type="Sample"></irio:mfvec3f>\n')
        self.failUnlessEqual(self.j.xio_getline_attime(1376571532081,
                                                       relative=False),
                             '<irio:sfint32 xmlns="" xmlns:ns3="http://www.'
                             'techfak.uni-bielefeld.de/ags/wbski/instantlog'
                             'gerprotocol" value="90310" timestamp="1376571'
                             '532081" sensorName="dsglab-desk-3/framenumber" '
                             'type="Sample"></irio:sfint32>\n')
        self.failUnlessEqual(self.j.xio_parseline_lineno(5),
                             {'valuetype': 'sffloat',
                              'fieldname': 'soundAngle',
                              'sensorname': 'dsglab-desk-3',
                              'value': -24.015615,
                              'time': 1376571532081L})
        self.failUnlessEqual(self.j.xio_parseline_attime(),
                             {'valuetype': 'sfint32',
                              'fieldname': 'framenumber',
                              'sensorname': 'dsglab-desk-3',
                              'value': 90310,
                              'time': 1376571532081L})
        self.failUnlessEqual([l for l in self.j.xio_linegen(0, 5)][2],
                             {'valuetype': 'sfint32',
                              'fieldname': 'skeletonCount',
                              'sensorname': 'dsglab-desk-3',
                              'value': 2,
                              'time': 1376571532081L})
        self.failUnlessEqual([x for x in self.j.xio_linegen_timerange(0, 6)][3],
                             {'valuetype': 'sffloat',
                              'fieldname': 'interactionSpace',
                              'sensorname': 'dsglab-desk-3',
                              'value': 0.083201334,
                              'time': 1376571532081L})

    def test_xiofile_unindexed(self):
        self.failUnlessEqual(self.g.mode, 'r')
        self.failUnlessEqual(self.g.indexed, False)
        self.failUnlessEqual(self.g.min_time, 1376571532081L)
        self.failUnlessEqual([ln for ln in self.g.xio_quicklinegen(0, 13)][6],
                             {'valuetype': 'sffloat',
                              'fieldname': 'soundAmplitude',
                              'sensorname': 'dsglab-desk-3',
                              'value': -1.0,
                              'time': 1376571532081L})
        self.failUnlessEqual(len([z for z in self.q.xio_quicklinegen(0, 6,
                                                         on_errors='stop')]), 4)

        self.failUnlessEqual(self.g.xio_quicksearch(15),
                             (False, 1376571532081L))
        self.failUnlessEqual(self.g.xio_quicksearch(1376571532082),
                             (True, 1376571532082L))
        #Test that unindexed is now the default mode
        self.failUnlessEqual(XIOFile('data/types.xio.gz').indexed, False)
        self.failUnlessEqual(type(self.nr), XIOFile)

    def test_writing_in_xiofile(self):
        #Read from previously written to file
        self.failUnlessEqual(self.i.xio_getline(0), '<irio:sfint32 value="35" '
             'sensorName="xioFileClass/desk3/skeletonCount" timestamp='
             '"13765381"></irio:sfint32>\n')
        #Read from previously formatted XIO line (legacy mode)
        self.failUnlessEqual(self.i.xio_getline(1), '<irio:sfint32 value="37" '
             'sensorName="xioFileClass/desk3/skeletonCount" timestamp='
             '"13765381"></irio:sfint32>\n')
        #Read from previously formatted XIO line (venice mode)
        self.failUnlessEqual(self.m.xio_getline(0), '<sfint32 value="37" '
             'timestamp="13765381" sensorName="desk3/skeletonCount"/>\n')
        #Test the mode of writing to a file
        self.failUnlessEqual(XIOFile('data/trywriting.xio.gz', 'w').mode, 'w')

    def test_copying_an_iofile(self):
        self.failUnlessEqual(self.k.xio_getline(2), '<irio:sfint32 xmlns="" '
             'xmlns:ns3="http://www.techfak.uni-bielefeld.de/ags/wbski/insta'
             'ntloggerprotocol" value="2" timestamp="1376571532081" sensor'
             'Name="dsglab-desk-3/skeletonCount" type="Sample"></irio:sfin'
             't32>\n')

    def test_parsing_of_types(self):
        self.failUnlessEqual(self.f.xio_parsetypes("0.1671641 -0.31289",
                                                   'sfvec2f')[1], -0.31289)
        self.failUnlessEqual(self.f.xio_parsetypes("0.1671641 -0.3 0.3",
                             'sfvec3f')[0], 0.1671641)
        self.failUnlessEqual(self.f.xio_parsetypes("0.9260816 -0.1602955 "
                                  "0.0856332 -0.3306738", 'sfrotation')[0],
                             0.9260816)
        self.failUnlessEqual(self.f.xio_parsetypes("90310", 'sfint32'), 90310)
        self.failUnlessEqual(self.f.xio_parsetypes("0.083201334", 'sffloat'),
                             0.083201334)
        self.failUnlessEqual(self.f.xio_parsetypes("Some string",
                             'sfstring'), 'Some string')
        self.failUnlessEqual(self.f.xio_parsetypes("[309.0 -0.5838974, "
                                   "336.0 -0.5788992, 317.0 -0.4093522]",
                             'mfvec2f')[1][0], 336.0)
        self.failUnlessEqual(self.f.xio_parsetypes("[0.9260816 -0.1602955 "
                                  "0.0856332 -0.3306738, 0.9676204 0.07145812 "
                                  "0.1676264 -0.1746593, 0.8931494 -0.2351457 "
                                  "-0.1472739 -0.3539787]",
                             'mfrotation')[1][0], 0.9676204)
        self.failUnlessEqual(self.j.xio_parsetypes("[0.2154177 0.04740157"
                                  " 1.772092, 0.0 0.0 0.0]", 'mfvec3f')[0][1],
                             0.04740157)
        self.failUnlessEqual(self.j.xio_parsetypes("[a, 0.04740157, b, c, E]",
                                                   'mffloat')[1],
                             0.04740157)
        self.assertTrue(math.isnan(self.j.xio_parsetypes("[a, 0.04740157]",
                                                         'mffloat')[0]))
        self.failUnlessEqual(self.j.xio_parsetypes("[a, 0.04740157]",
                                                   'mfstring')[1],
                             '0.04740157')
        self.failUnlessEqual(self.j.xio_parsetypes("True", 'sfbool'), True)
        self.failUnlessEqual(self.j.xio_parsetypes("true", 'boolean'), True)
        self.failUnlessEqual(self.j.xio_parsetypes("", 'sfbool'), False)
        self.failUnlessEqual(self.j.xio_parsetypes("yes", 'boolean'), False)

    def test_parsing_of_names(self):
        self.failUnlessEqual(self.f.xio_parsename("dsglab-desk-3/"
                                                  "jointOrientations0"),
                            ('dsglab-desk-3', 'jointOrientations0'))
        self.failUnlessEqual(self.j.xio_parsename("dsglab-desk-3/positions3D"),
                             ('dsglab-desk-3', 'positions3D'))

    def test_parsing_of_lines(self):
        self.failUnlessEqual(str(self.j.xio_parseline('<irio:mfvec3f xmlns="'
             '" xmlns:ns3="http://www.techfak.uni-bielefeld.de/ags/wbski/insta'
             'ntloggerprotocol" value="[0.0 0.0 0.0, 0.0 0.0 0.0, 0.0 0.0 0.0,'
             ' 0.1671641 -0.3231136 1.178103, 0.2154177 0.04740157 1.772092,'
             ' 0.0 0.0 0.0]" timestamp="1376571532081" sensorName="dsglab-'
             'desk-3/positions3D" type="Sample"></irio:mfvec3f>\n')['value']),
                             '[0.0 0.0 0.0, 0.0 0.0 0.0, 0.0 0.0 0.0, '
                             '0.1671641 -0.3231136 1.178103, 0.2154177 '
                             '0.04740157 1.772092, 0.0 0.0 0.0]')
        self.failUnlessEqual(self.f.xio_parseline('<irio:sfint32 xmlns="'
             '" xmlns:ns3="http://www.techfak.uni-bielefeld.de/ags/wbski/'
             'instantloggerprotocol" value="2" timestamp="1376571532081" '
             'sensorName="dsglab-desk-3/skeletonCount" type="Sample">'
             '</irio:sfint32>\n'),
                             {'valuetype': 'sfint32',
                              'fieldname': 'skeletonCount',
                              'sensorname': 'dsglab-desk-3',
                              'value': 2,
                              'time': 1376571532081L})
        self.failUnlessEqual(self.m.xio_parseline('<sfint32 value="37" '
             'timestamp="13765381" sensorName="desk3/skeletonCount"/>\n'),
                             {'valuetype': 'sfint32',
                              'fieldname': 'skeletonCount',
                              'sensorname': 'desk3',
                              'value': 37,
                              'time': 13765381})

    def test_xiofile_uncompressed(self):
        self.failUnlessEqual(self.n.mode, 'r')
        self.failUnlessEqual(self.n.indexed, True)
        self.failUnlessEqual(self.n.max_lines, 15)
        self.failUnlessEqual(self.n.max_time, 1376571532082L)
        self.failUnlessEqual(self.n.xio_getline(2), '<irio:sfint32 xmlns="'
             '" xmlns:ns3="http://www.techfak.uni-bielefeld.de/ags/wbski/'
             'instantloggerprotocol" value="2" timestamp="1376571532081" '
             'sensorName="dsglab-desk-3/skeletonCount" '
             'type="Sample"></irio:sfint32>\n')
        self.failUnlessEqual(self.n.xio_getline_attime(1376571532081,
                                                       relative=False),
                              '<irio:sfint32 xmlns="" xmlns:ns3="http://'
                              'www.techfak.uni-bielefeld.de/ags/wbski/'
                              'instantloggerprotocol" value="90310" '
                              'timestamp="1376571532081" sensorName="dsglab'
                              '-desk-3/framenumber" type="Sample">'
                              '</irio:sfint32>\n')
        self.failUnlessEqual(self.n.xio_getline_attime(1), '<irio:mfvec3f xmln'
             's="" xmlns:ns3="http://www.techfak.uni-bielefeld.de/ags/wbski/in'
             'stantloggerprotocol" value="[0.2124978 -0.1224827 1.858883, 0.30'
             '30231 -0.1534625 1.925013, 0.01070284 -0.04043572 1.811359, 0.51'
             '68817 0.04873443 1.994409, 0.209666 -0.148198 1.78842, 0.299611 '
             '-0.1756292 1.85338, -0.01972085 -0.3181056 1.753447, 0.5168398 -'
             '0.1499471 1.939156, 0.2531285 0.3707453 1.670671, 0.2336805 0.03'
             '969637 1.820125, 0.1654053 -0.02932697 1.817514, 0.3024898 -0.02'
             '393005 1.848226, 0.4543798 0.03429135 1.977719, 0.5566682 -0.032'
             '79109 2.062352, 0.234128 0.2108699 1.780103, 0.1076903 0.1457002'
             ' 1.790787, 0.3986858 0.1662227 1.876898, 0.2335398 0.06816141 1.'
             '811909, -0.01211493 -0.2486881 1.766024, 0.5297669 -0.1118848 1.'
             '973672]" timestamp="1376571532082" sensorName="dsglab-desk-3/joi'
             'ntPositions3D1" type="Sample"></irio:mfvec3f>\n')

        self.failUnlessEqual(self.n.xio_parseline_lineno(5),
                             {'valuetype': 'sffloat',
                              'fieldname': 'soundAngle',
                              'sensorname': 'dsglab-desk-3',
                              'value': -24.015615,
                              'time': 1376571532081L})
        self.failUnlessEqual(self.n.xio_parseline_attime(),
                             {'valuetype': 'sfint32',
                              'fieldname': 'framenumber',
                              'sensorname': 'dsglab-desk-3',
                              'value': 90310, 'time': 1376571532081L})
        self.failUnlessEqual([l for l in self.n.xio_linegen(0, 5)][2],
                             {'valuetype': 'sfint32',
                              'fieldname': 'skeletonCount',
                              'sensorname': 'dsglab-desk-3',
                              'value': 2, 'time': 1376571532081L})

        self.failUnlessEqual([y for y in self.q.xio_linegen(0, 6,
                                                        on_errors='stop')][-1],
                             {'fieldname': 'gazeQualityLevelLeft',
                              'sensorname': 'lab-labtop/FaceLabNode 3',
                              'time': 1341393414828L,
                              'value': 2,
                              'valuetype': 'sfint32'})

        self.failUnlessEqual(list(self.n.xio_linegen_timerange(0, 10))[3],
                             {'valuetype': 'sffloat',
                              'fieldname': 'interactionSpace',
                              'sensorname': 'dsglab-desk-3',
                              'value': 0.083201334,
                              'time': 1376571532081L})
        self.failUnlessEqual(list(self.q.xio_linegen_timerange(0, 6))[0],
                             {'fieldname': 'percentageInteractionSpace',
                              'sensorname': 'lab-labtop/irioKinect 2',
                              'time': 1341393414826L,
                              'value': 0.0,
                              'valuetype': 'sffloat'})

    def test_line_ranges_indexed(self):
        self.failUnlessEqual(self.o.xio_getline(899), '<sfint32 value="899" ti'
             'mestamp="8991" sensorName="linetest/linenumber"/>\n')
        self.failUnlessEqual(len(list(self.o.xio_linegen(0,
                                                         self.o.max_lines))),
                             1000)
        self.failUnlessEqual(self.o.xio_getline_attime(31, relative=False),
                             '<sfint32 value="3" timestamp="31" sensorName="li'
                             'netest/linenumber"/>\n')
        self.failUnlessEqual(list(self.o.xio_linegen_timerange(9990,
                                                               10000,
                                                               relative=False)),
                             [{'fieldname': 'linenumber',
                               'sensorname': 'linetest',
                               'time': 9991,
                               'value': 999,
                               'valuetype': 'sfint32'}])

        self.failUnlessEqual(self.o.xio_getline_attime(), '<sfint32 value="0"'
             ' timestamp="1" sensorName="linetest/linenumber"/>\n')

        self.failUnlessEqual(self.o.line_offset, [116, 72895])
        self.failUnlessEqual(self.o.time_offset, [7195, 14495, 21795, 29095,
                                                  36395, 43695, 50995, 58295,
                                                  65595])

    def test_line_ranges_unindexed(self):
        self.failUnlessEqual(list(self.p.xio_quicklinegen(5000, 5010,
                                                    relative=False)),
                                 [{'fieldname': 'linenumber',
                                   'sensorname': 'linetest',
                                   'time': 5001,
                                   'value': 500,
                                   'valuetype': 'sfint32'}])


        self.failUnlessEqual(self.p.xio_quicksearch(6001), (True, 6001))

    def tearDown(self):
        os.system('rm data/newtypes.xio.gz')
        os.system('rm data/trywriting.xio.gz')
        os.system('rm data/trywriting2.xio.gz')

if __name__ == "__main__":
    unittest.main()
