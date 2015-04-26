import unittest
import pandas as pd
from mumodo.mumodoIO import open_intervalframe_from_textgrid, \
                            open_streamframe_from_xiofile
from mumodo.analysis import intervalframe_overlaps, intervalframe_union, \
                            invert_intervalframe, \
                            create_intervalframe_from_streamframe, \
                            slice_streamframe_on_intervals, \
                            slice_intervalframe_by_time, \
                            convert_times_of_tier, convert_times_of_tiers, \
                            shift_tier, shift_tiers, get_tier_type, \
                            get_tier_boundaries, join_intervals_by_label, \
                            join_intervals_by_time, \
                            create_streamframe_from_intervalframe, \
                            slice_pointframe_by_time


class AnalysisTest(unittest.TestCase):

    def setUp(self):
        self.dict1 = open_intervalframe_from_textgrid('data/r1-20120704-cam1-'
                                                      'head-sk'
                                                      '.TextGrid', 'utf-8')
        self.dict2 = open_intervalframe_from_textgrid('data/r1-20120704-cam1-'
                                                      'head-zm.TextGrid',
                                                      'utf-8')
        self.dict3 = open_intervalframe_from_textgrid('data/mytextgrid'
                                                      '.TextGrid', 'utf-8')
        self.dict4 = dict()
        self.dict4['speaker A'] = self.dict3['speaker A'][0:4].copy(deep=True)
        self.dict4['speaker B'] = self.dict3['speaker B'][0:4].copy(deep=True)
        shift_tiers(self.dict4, 1)
        self.tier1 = self.dict1['HeadSK']
        self.tier2 = self.dict2['HeadZM']
        self.stream = open_streamframe_from_xiofile('data/fseeksmaller.xio.gz',
                                                    "lab-labtop/irioKinect 2",
                                                     window_size=5,
                                                    with_fields=None,
                                                    without_fields=None,
                                                    discard_duplicates=True,
                                                    start_time=0,
                                                    end_time=500,
                                                    timestamp_offset=None)
        self.ifr = create_intervalframe_from_streamframe(self.stream,
                                                         'soundAngle',
                                                         lambda x: True \
                                                            if x <- 0.7323895 \
                                                            else False,
                                                         10)

        self.iframe = open_intervalframe_from_textgrid('data/mytextgrid.Text'
                                                       'Grid', 'utf-8')
        self.speaker_a = self.iframe['speaker A']
        self.speaker_b = self.iframe['speaker B']
        self.overlap_ab_shouldbe = [{'end_time': 3.47134775993, 'start_time':
                                     3.4540353413, 'text': u'exactly and at '
                                     'the very end of the corridor is just '
                                     'the bathroom/I see yes'},
                                    {'end_time': 3.8781895978200001, 'start_'
                                     'time': 3.7223778301200001,
                                     'text': u'exactly and at the very end of '
                                     'the corridor is just the bathroom/yes'},
                                    {'end_time': 7.3163672878900003,
                                     'start_time': 6.9095254500000003,
                                     'text': u'that you quasi such have so '
                                     'zack zack zack/yes'},
                                    {'end_time': 7.5933659860300002,
                                     'start_time': 7.4029293810599999,
                                     'text': u'that you quasi such have so '
                                              'zack zack zack/yes'},
                                    {'end_time': 11.168380433799999,
                                     'start_time': 10.8740693171,
                                     'text': u'know you ?/yes I think I'},
                                    {'end_time': 11.644471946299999,
                                     'start_time': 11.2895673643,
                                     'text': u'if this the corridor is here a '
                                              'room there a room there a room '
                                              'there and above/yes I think I'},
                                    {'end_time': 14.892213031400001,
                                     'start_time': 13.1073713208,
                                     'text': u'if this the corridor is here a '
                                     'room there a room there a room there '
                                     'and above/there a room there there and '
                                     'then there yes'},
                                    {'end_time': 15.558741148799999,
                                     'start_time': 15.376960753100001,
                                     'text': u'that is perfect/yes'},
                                    {'end_time': 17.679512431399999,
                                     'start_time': 17.4544509891,
                                     'text': u'yes/sure'},
                                    {'end_time': 27.8435647606,
                                     'start_time': 27.5492536438,
                                     'text': u'twentyfive/so I would already '
                                     'gladly a large room have'}]

        self.right_overlap_ab = pd.DataFrame(self.overlap_ab_shouldbe,
                                             columns=['start_time', 'end_time',
                                                      'text'])

        self.union_dict = [{'end_time': 2.5191647350899999, 'start_time': 0.0,
                            'text': 'union'},
                           {'end_time': 6.1304666115000002, 'start_time': \
                            2.80481964254,
                            'text': 'union'},
                           {'end_time': 9.5669817102499994,
                            'start_time': 6.7796823102500001,
                            'text': 'union'},
                           {'end_time': 15.0393685898, 'start_time': \
                            10.7528823866, 'text': 'union'},
                           {'end_time': 16.1646758009,
                            'start_time': 15.281742450599999,
                            'text': 'union'},
                           {'end_time': 17.3159516401,
                            'start_time': 17.064921569900001,
                            'text': 'union'},
                           {'end_time': 17.714137268599998,
                            'start_time': 17.4457947798,
                            'text': 'union'},
                           {'end_time': 19.393441876099999,
                            'start_time': 17.826667989699999,
                            'text': 'union'}]

        self.union_mustbe = pd.DataFrame(self.union_dict, columns=['start_'
                                         'time', 'end_time', 'text'])

        self.invert = [{'start_time': 0., 'end_time': 547.016,
           'text': 'nod'},
          {'start_time': 547.464, 'end_time': 549.507,
           'text': 'nod/turn-aw'},
          {'start_time': 549.988, 'end_time': 556.808,
           'text': 'turn-aw/nod-2'},
          {'start_time': 557.404, 'end_time': 561.428,
           'text': 'nod-2/nod-3'},
          {'start_time': 563.345, 'end_time': 600.000,
           'text': 'nod-3'}]

        self.inversion = pd.DataFrame(self.invert, columns=['start_'
                                      'time', 'end_time', 'text'])


        self.tier1_inverted = [{'end_time': 547.01599999999996,
                                'start_time': 0.0, 'text': u'nod'},
                               {'end_time': 549.50699999999995,
                                'start_time': 547.46400000000006,
                                'text': u'nod/turn-aw'},
                               {'end_time': 556.80799999999999,
                                'start_time': 549.98800000000006,
                                'text': u'turn-aw/nod-2'},
                               {'end_time': 561.428, 'start_time': 557.404,
                                'text': u'nod-2/nod-3'},
                               {'end_time': 567.51099999999997,
                                'start_time': 563.34500000000003,
                                'text': u'nod-3/slide-right'},
                               {'end_time': 578.17100000000005,
                                'start_time': 568.02300000000002,
                                'text': u'slide-right/nod-4'},
                               {'end_time': 586.03599999999994,
                                'start_time': 579.53499999999997,
                                'text': u'nod-4/nod-3'},
                               {'end_time': 604.73699999999997,
                                'start_time': 587.10699999999997,
                                'text': u'nod-3/nod-4-turn-aw-tw'},
                               {'end_time': 609.11800000000005,
                                'start_time': 607.35699999999997,
                                'text': u'nod-4-turn-aw-tw/nod-4'},
                               {'end_time': 617.30899999999997,
                                'start_time': 611.16600000000005,
                                'text': u'nod-4/nod-5'}]

        self.invert_tier1 = pd.DataFrame(self.tier1_inverted,
                                  columns=['start_time', 'end_time', 'text'])

        self.empty = pd.DataFrame([])

        self.withna = [{'start_time': 3, 'end_time': 6, 'text': 'hi'},
                       {'start_time': 7, 'end_time': 8.5},
                       {'start_time': 9, 'end_time': 13, 'text': 'bye'}]

        self.emptyint = pd.DataFrame(self.withna, columns=['start_time',
                                                           'end_time', 'text'])

        self.emptyshouldbe = [{'end_time': 3.0, 'start_time': 0, 'text': 'hi'},
                              {'end_time': 7.0, 'start_time': 6,
                               'text': 'hi/empty'},
                              {'end_time': 9.0, 'start_time': 8.5,
                               'text': 'empty/bye'}]

        self.emptyshouldbepd = pd.DataFrame(self.emptyshouldbe, columns= \
                                            ['start_time', 'end_time', 'text'])

        self.no_overlap1 = [{'start_time': 3, 'end_time': 5, 'text': 'eins'},
                            {'start_time': 9, 'end_time': 15, 'text': 'zwei'},
                            {'start_time': 19, 'end_time': 21, 'text': 'drei'}]

        self.no_overlap2 = [{'start_time': 0, 'end_time': 2.5, 'text': 'vier'},
                            {'start_time': 6, 'end_time': 7, 'text': 'fuenf'},
                            {'start_time': 23, 'end_time': 27, 'text': 'sechs'}]

        self.pd_no_overlap1 = pd.DataFrame(self.no_overlap1,
                                     columns=['start_time', 'end_time', 'text'])

        self.pd_no_overlap2 = pd.DataFrame(self.no_overlap2,
                                     columns=['start_time', 'end_time', 'text'])

        self.convert = [{'start_time': 4, 'end_time': 5, 'text': 'eins'},
                        {'start_time': 9, 'end_time': 15, 'text': 'zwei'},
                        {'start_time': 19, 'end_time': 21, 'text': 'drei'}]

        self.convert_pd = pd.DataFrame(self.convert,
                                     columns=['start_time', 'end_time', 'text'])


        convert_times_of_tier(self.convert_pd, lambda y: int(1000 * y))

        self.converted = [{'start_time': 4000, 'end_time': 5000,
                           'text': 'eins'}, {'start_time': 9000,
                           'end_time': 15000, 'text': 'zwei'},
                          {'start_time': 19000, 'end_time': 21000,
                           'text': 'drei'}]

        self.converted_pd = pd.DataFrame(self.converted,
                                     columns=['start_time', 'end_time', 'text'])

        self.tiers_shifted_a = [{'end_time': 4.47134775993,
                                 'start_time': 3.80481964254,
                                 'text': u'I see yes'},
                                {'end_time':4.8781895978200001,
                                 'start_time': 4.7223778301200001,
                                 'text': u'yes'},
                                {'end_time': 8.3163672878900003,
                                 'start_time': 7.9095254500000003,
                                 'text': u'yes'},
                                {'end_time': 8.5933659860300002,
                                 'start_time': 8.4029293810599999,
                                 'text': u'yes'}]

        self.tiers_shifted_pd = pd.DataFrame(self.tiers_shifted_a,
                                     columns=['start_time', 'end_time', 'text'])

        self.shift_dict = [{'start_time': 3, 'end_time': 5, 'text': 'eins'},
                           {'start_time': 9, 'end_time': 15, 'text': 'zwei'},
                           {'start_time': 19, 'end_time': 21, 'text': 'drei'}]

        self.shift = pd.DataFrame(self.shift_dict,
                                  columns=['start_time', 'end_time', 'text'])

        shift_tier(self.shift, 1)

        self.shifted_dict = [{'start_time': 4, 'end_time': 6, 'text': 'eins'},
                           {'start_time': 10, 'end_time': 16, 'text': 'zwei'},
                           {'start_time': 20, 'end_time': 22, 'text': 'drei'}]


        self.shifted = pd.DataFrame(self.shifted_dict,
                                     columns=['start_time', 'end_time', 'text'])

        for col in self.dict4['speaker A'].columns:
            self.dict4['speaker A'].loc[:, col] = \
            self.dict4['speaker A'][col].map(lambda x: str(x))
        for col in self.tiers_shifted_pd.columns:
            self.tiers_shifted_pd.loc[:, col] = \
            self.tiers_shifted_pd[col].map(lambda x: str(x))

        self.withPoint = open_intervalframe_from_textgrid('data/r1_12_15with'
                                                          'Point.TextGrid',
                                                          'utf-8')

        self.points = self.withPoint['P'][0:4].copy(deep=True)
        shift_tier(self.points, 10)

        for col in self.points.columns:
            self.points.loc[:, col] = self.points[col].map(lambda x: str(x))

        self.points_shifted = [{'mark': 'A', 'time': 12.804819642542952},
                               {'mark': 'B', 'time': 13.454035341299345},
                               {'mark': 'A', 'time': 13.722377830118717},
                               {'mark': 'B', 'time': 16.779682310252952}]

        self.points_shifted_pd = pd.DataFrame(self.points_shifted,
                                     columns=['time', 'mark'])


        for col in self.points_shifted_pd.columns:
            self.points_shifted_pd.loc[:, col] = \
            self.points_shifted_pd[col].map(lambda x: str(x))

        self.labeljoin = open_intervalframe_from_textgrid('data/joinlabels'
                                                          '.TextGrid', 'utf-8')

        self.streamdict1 = [{'value': u'nod_start'},
                        {'value': u'nod_end'},
                        {'value': u'turn-aw_start'},
                        {'value': u'turn-aw_end'},
                        {'value': u'nod-2_start'},
                        {'value': u'nod-2_end'},
                        {'value': u'nod-3_start'},
                        {'value': u'nod-3'},
                        {'value': u'nod-3_end'}]

        self.stream1 = pd.DataFrame(self.streamdict1, columns=['value'])
        self.stream1.index = [547.016, 547.464, 549.507, 549.988, 556.808,
                              557.404, 561.428, 562.428, 563.345]

        self.inv1 = [{'end_time': '547.016', 'start_time': '300.0',
                      'text': u'nod'},
                     {'end_time': '549.507', 'start_time': '547.464',
                      'text': u'nod/turn-aw'},
                     {'end_time': '556.808', 'start_time': '549.988',
                      'text': u'turn-aw/nod-2'},
                     {'end_time': '561.428', 'start_time': '557.404',
                      'text': u'nod-2/nod-3'},
                     {'end_time': '700.0', 'start_time': '563.345',
                      'text': u'nod-3'}]

        self.inverted1 = pd.DataFrame(self.inv1,
                                    columns=['start_time', 'end_time', 'text'])

        self.inv1_str = invert_intervalframe(self.tier1[0:4], 300, 700)
        for col in self.inv1_str:
            self.inv1_str.loc[:, col] = \
            self.inv1_str[col].map(lambda x: str(x))


        self.inv_default_conc = [{'end_time': '549.507',
                                  'start_time': '547.464', 'text': u'nod'},
                            {'end_time': '556.808',
                             'start_time': '549.988', 'text': u'turn-aw+nod-2'},
                            {'end_time': '561.428',
                             'start_time': '557.404', 'text': u'nod-2'}]

        self.inv_def_pd = pd.DataFrame(self.inv_default_conc,
                                     columns=['start_time', 'end_time', 'text'])
        self.inv_def_str = invert_intervalframe(self.tier1[0:4],
                                                     concat_delimiter='+')
        for col in self.inv_def_str:
            self.inv_def_str.loc[:, col] = \
            self.inv_def_str[col].map(lambda x: str(x))


    def test_overlaps(self):

        self.failUnlessEqual((intervalframe_overlaps(self.pd_no_overlap1,
                                                    self.pd_no_overlap2) == \
                             pd.DataFrame(columns=['start_time', 'end_time',
                                                   'text'])).all().all(), True)


        self.failUnlessEqual(intervalframe_overlaps(self.tier1,
                                             self.tier2).ix[0]['start_time'],
                                                    547.01599999999996)
        self.failUnlessEqual(intervalframe_overlaps(self.tier1,
                                             self.tier2).ix[0]['end_time'],
                                                    547.090)
        self.failUnlessEqual(intervalframe_overlaps(self.tier1,
                                             self.tier2).ix[3]['start_time'],
                                                    561.480)
        self.failUnlessEqual(intervalframe_overlaps(self.tier1,
                                             self.tier2).ix[3]['end_time'],
                                                    563.345)
        self.failUnlessEqual(intervalframe_overlaps(self.tier1,
                                             self.tier2).ix[0]['text'],
                                                    u'nod/turn-1-tw')
        self.failUnlessEqual(intervalframe_overlaps(self.tier1,
                                             self.tier2).ix[1]['text'],
                                                  u'turn-aw/turn-1-aw')
        self.failUnlessEqual(intervalframe_overlaps(self.tier1,
                                             self.tier2, False).ix[1]['text'],
                                                  u'overlap')

        self.failUnlessEqual((intervalframe_overlaps(self.speaker_a,
                              self.speaker_b).ix[0:9]  == \
                              self.right_overlap_ab).all().all(), True)

    def test_union(self):

        self.failUnlessEqual((intervalframe_union(self.speaker_a,
                              self.speaker_b).iloc[:, 0:2][0:8] == \
                              self.union_mustbe.iloc[:, 0:2]).all().all(),
                               True)


        self.failUnlessEqual(intervalframe_union(self.tier1[0:5],
                                            self.tier2[0:5]).ix[0]['end_time'],
                                                 547.464)
        self.failUnlessEqual(intervalframe_union(self.tier1[0:5],
                                        self.tier2[0:5]).ix[4]['start_time'],
                                                 561.428)

    def test_slicing(self):

        self.failUnlessEqual(slice_streamframe_on_intervals(self.stream,
                                      self.ifr)['framenumber'][1341393414961],
                                                            45776.0)
        self.failUnlessEqual(slice_intervalframe_by_time(self.tier1,
                                                         578.171,
                                                         698.440).index[0],
                                                         5)
        self.failUnlessEqual(slice_intervalframe_by_time(self.tier1,
                                                         578.171,
                                                         698.440).index[-1],
                                                         21)

        self.failUnlessEqual(slice_pointframe_by_time(self.withPoint['P'],
                                                      10, 100)['mark'].iloc[0],
                             'B')


    def test_inversion(self):

        self.failUnlessEqual((invert_intervalframe(self.tier1[0:4], 0, 600) == \
                              self.inversion).all().all(), True)


        #self.failUnlessEqual(invert_intervalframe(self.tier1, 0,
        #                     self.tier1['end_time'].iloc[-1])\
        #                     ['start_time'].ix[len(invert_intervalframe\
        #                    (self.tier1, 0, self.tier1['end_time'].\
        #                     iloc[-1]))-1], 1306.064)

        self.failUnlessEqual((self.inv1_str == self.inverted1).all().all(),
                              True)

        self.failUnlessEqual((self.inv_def_pd == self.inv_def_str).all().\
                              all(), True)
        #self.failUnlessEqual((invert_intervalframe(self.tier1[0:10], 0) == \
        #                     self.invert_tier1).all().all(), True)

       # self.failUnlessEqual(str(type(invert_intervalframe(self.empty))),
       #                      '<type \'NoneType\'>')
        self.failUnlessEqual(str(type(invert_intervalframe(pd.DataFrame()))),
                             '<type \'NoneType\'>')

       # self.failUnlessEqual((invert_intervalframe(self.emptyint, 0) == \
       #                       self.emptyshouldbepd).all().all(), True)

    def test_convertions_and_shifts(self):

        self.failUnlessEqual((self.convert_pd == \
                              self.converted_pd).all().all(), True)

        self.failUnlessEqual((self.shift == \
                              self.shifted).all().all(), True)

        self.failUnlessEqual((self.dict4['speaker A'] == \
                              self.tiers_shifted_pd).all().all(), True)


        self.failUnlessEqual((self.points == \
                             self.points_shifted_pd).all().all(), True)

    def test_stream_from_intervals(self):

        self.failUnlessEqual((create_streamframe_from_intervalframe(self.tier1\
                              [0:4], start_label_appendix='start',
                              end_label_appendix='end', fillstep=1)==\
                              self.stream1).all().all(), True)

        self.failUnlessEqual(str(create_streamframe_from_intervalframe(self.\
                                 tier1[0:4], True, start_label_appendix=\
                                 'start', end_label_appendix='end',
                                 fillstep=1).index[2]), '2.491')
        self.failUnlessEqual(str(type(create_streamframe_from_intervalframe\
                            (pd.DataFrame()))), '<type \'NoneType\'>')


    def test_get_tier_type(self):

        self.failUnlessEqual(get_tier_type(self.withPoint['A']), 'interval')

        self.failUnlessEqual(get_tier_type(self.withPoint['P']), 'point')

        self.failUnlessEqual(get_tier_type(pd.DataFrame(None,
                                                        columns=['start_time',
                                                                 'end_time',
                                                                 'text'])),
                                            'interval')

        self.failUnlessEqual(get_tier_type(None), None)

    def test_get_tier_boundaries(self):
        self.failUnlessEqual([int(x) for x in get_tier_boundaries(\
                                 self.withPoint['A'])],
                             [2, 179])

        self.failUnlessEqual([int(x) for x in get_tier_boundaries(\
                                 self.withPoint['P'])],
                             [2, 32])

        self.failUnlessEqual(get_tier_boundaries(None), None)

        self.failUnlessEqual(get_tier_boundaries(pd.DataFrame(None, columns=\
                                                              ['start_time',
                                                               'end_time',
                                                               'text'])),
                                                 None)

        self.failUnlessEqual([int(x) for x in get_tier_boundaries(\
                                  self.withPoint['P'][:1])], [2, 2])

    def test_join_intervals_by_label_or_by_time(self):

        t = self.labeljoin['labels']

        self.failUnlessEqual(join_intervals_by_label(t)['end_time'].ix[2], 18)

        self.failUnlessEqual(join_intervals_by_label(t, 1.0)['end_time'].ix[5],
                             18)

        self.failUnlessEqual(len(join_intervals_by_label(self.empty)), 0)

        self.failUnlessEqual(join_intervals_by_time(t)['end_time'].ix[3], 10)

        self.failUnlessEqual(join_intervals_by_time(t, 1.0)['end_time'].ix[1],
                             6)

        self.failUnlessEqual(join_intervals_by_time(t, 2.0, '+')['text'].ix[0],
                             'a+b+b+b+c')

        self.failUnlessEqual(len(join_intervals_by_time(self.empty)), 0)

if __name__ == "__main__":
    unittest.main()
