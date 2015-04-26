import unittest
import tgt, os
from mumodo.mumodoIO import quantize, open_streamframe_from_xiofile, \
                            save_streamframe_to_xiofile, quantize, \
                            open_intervalframe_from_textgrid, \
                            save_intervalframe_to_textgrid, \
                            convert_pointtier_to_streamframe, \
                            convert_streamframe_to_pointtier, \
                            open_intervalframe_from_increco

from mumodo.xiofile import XIOFile

class MumodoTest(unittest.TestCase):

    def setUp(self):
        self.f = open_streamframe_from_xiofile('data/fseeksmaller.xio.gz',
                                               "lab-labtop/irioKinect 2",
                                               window_size=5, with_fields=[],
                                               without_fields=[],
                                               discard_duplicates=True,
                                               start_time=0, end_time=13,
                                               relative=True,
                                               timestamp_offset=10)

        self.f2 = open_streamframe_from_xiofile('data/fseeksmaller.xio.gz',
                                                "lab-labtop/irioKinect",
                                                window_size=5, with_fields=[],
                                                without_fields=[],
                                                discard_duplicates=True,
                                                start_time=0, end_time=13,
                                                relative=True,
                                                timestamp_offset=10)
        #self.outtake_from_stream = self.f.ix[1341393414826]['framenumber']
        self.fraw = open_streamframe_from_xiofile('data/fseeksmaller.xio.gz',
                                                  "lab-labtop/irioKinect 2",
                                                  window_size=5, with_fields=[],
                                                  without_fields=[],
                                                  discard_duplicates=True,
                                                  start_time=0, end_time=13,
                                                  relative=True,
                                                  timestamp_offset='raw')
        self.ff = open_streamframe_from_xiofile('data/fseeksmaller.xio.gz',
                                                "lab-labtop/irioKinect 2",
                                                window_size=5, with_fields=[],
                                                without_fields=[],
                                                discard_duplicates=True,
                                                start_time=0, end_time=13,
                                                relative=True)

        save_streamframe_to_xiofile({"lab-labtop/irioKinect 2": self.f},
                                    'data/sf_to_xio.xio.gz')

        save_streamframe_to_xiofile({"lab-labtop/irioKinect 2": self.f,
                                     "lab-labtop/irioKinect": self.f2},
                                    'data/sf_to_xio2.xio.gz')

        self.rsn = open_streamframe_from_xiofile('data/fseeksmaller.xio.gz',
                                                "wrong/sensor/name")

        self.outtake_from_xio = XIOFile('data/sf_to_xio.xio.gz',
                                        indexing=True)

        self.outtake_from_xio_2 = XIOFile('data/sf_to_xio2.xio.gz',
                                          indexing=True)

        self.q = [ex for ex in quantize(self.outtake_from_xio.xio_quicklinegen\
                                                  (0, 13, True, True),
                                  "lab-labtop/irioKinect 2")][0]['soundAngle']

        self.ivf = open_intervalframe_from_textgrid('data/r1_12_15with'
                                                    'Point.TextGrid',
                                                    encoding='utf-8',
                                                    asobjects = False,
                                         include_empty_intervals = False)['P']
        self.cv = convert_pointtier_to_streamframe(self.ivf)
        self.pf = convert_streamframe_to_pointtier(self.f)
        self.outtake_from_pf = \
          convert_streamframe_to_pointtier(self.f)['soundAngle'].ix[0]['time']

        self.if_from_tg = open_intervalframe_from_textgrid('data/r1-20120704-'
                          'cam1-head-zm.TextGrid',
                          encoding='utf-8',
                          asobjects = False,
                          include_empty_intervals = False)

        self.if_from_tg_tier =  self.if_from_tg.values()[0]

        save_intervalframe_to_textgrid(self.if_from_tg,
                                       'data/testif.TextGrid',
                                       encoding='utf-8')
        self.tg = tgt.read_textgrid('data/testif.TextGrid',
                                    encoding='utf-8',
                                    include_empty_intervals=False)

        self.ic1 = open_intervalframe_from_increco('data/test.inc_reco')

        self.ic2 = open_intervalframe_from_increco('data/test.inc_reco',
                                                   lastonly=True)

    def test_stream_from_xio(self):

        self.failUnlessEqual(self.f.ix[10]['framenumber'], 45771.0)
        self.failUnlessEqual(self.f.index[1], 20)
        self.failUnlessEqual(self.fraw.index[0], 1341393414826)
        self.failUnlessEqual(self.ff.index[1], 10)
        #wrong sensor name should result in an empty DataFrame
        #being returned
        self.failUnlessEqual(len(self.rsn), 0)


    def test_stream_to_xio(self):
        self.failUnlessEqual(self.outtake_from_xio.xio_getline(5),
                             '<sffloat value="-0.7323895" timestamp="10"'
                             ' sensorName="lab-labtop/irioKinect 2/so'
                             'undAngle"/>\n')

    def test_many_stream_to_xio(self):

        self.failUnlessEqual(self.outtake_from_xio_2.xio_getline(6),
                             '<sffloat value="46286.0" timestamp="14"'
                             ' sensorName="lab-labtop/irioKinect/fram'
                             'enumber"/>\n')

        self.failUnlessEqual(self.outtake_from_xio_2.xio_getline(5),
                             '<sffloat value="-0.7323895" timestamp="10"'
                             ' sensorName="lab-labtop/irioKinect 2/so'
                             'undAngle"/>\n')

    def test_interval_from_textgrid(self):
        self.failUnlessEqual(self.if_from_tg_tier.ix[100]['end_time'], 1095.864)

    def test_interval_to_textgrid(self):
        self.failUnlessEqual(type(self.tg.tiers[0].intervals[10]),
                             tgt.core.Interval)

    def test_quantize(self):
        self.failUnlessEqual(self.q, -0.7323895)

    def test_pointtier_to_stream(self):
        self.failUnlessEqual(str(self.cv['mark'].values[1]), 'B')

    def test_stream_to_pointframe(self):
        self.failUnlessEqual(self.outtake_from_pf, 10)

    def test_intervals_from_increco(self):
        self.failUnlessEqual(len(self.ic1.keys()), 106)

        self.failUnlessEqual(self.ic1.keys()[3:6], ['6.43', '3.78', '6.5'])

        self.failUnlessEqual(self.ic1['3.78'].ix[0]['text'], 'der')

        self.failUnlessEqual(len(self.ic2.keys()), 1)

        self.failUnlessEqual(self.ic2.keys()[0], '38.4')

        self.failUnlessEqual(self.ic2['38.4'].ix[0]['text'], 'ragt')

    def tearDown(self):
        os.system('rm data/sf_to_xio.xio.gz')
        os.system('rm data/sf_to_xio2.xio.gz')

if __name__ == "__main__":
    unittest.main()



