import unittest
from mumodo.increco import IncReco

class IncRecoTest(unittest.TestCase):

    def setUp(self):
        self.reco = IncReco('data/test.inc_reco')

    def test_methods(self):
        self.failUnlessEqual(self.reco[0], {'Chunk': [['0.08',
                                                       '0.13',
                                                       '\xc3\xa4h']],
                                            'Time': 0.13})

        self.failUnlessEqual(str(self.reco)[143:155], "'Time': 0.71")

        self.failUnlessEqual(len(self.reco), 106)

        self.failUnlessEqual(list(self.reco)[55], {'Chunk': [['6.95',
                                                              '7.10',
                                                              'ph']],
                                                   'Time': 7.1})

        self.failUnlessEqual(self.reco.get_latest_chunk(13.66)['Time'], 13.58)

        self.failUnlessEqual(self.reco.get_latest_chunk(13.67)['Time'], 13.67)

        self.failUnlessEqual(self.reco.get_latest_chunk(13.68)['Time'], 13.67)

        self.failUnlessEqual(self.reco.get_last_chunk()['Time'], 38.4)

        self.failUnlessEqual(self.reco.get_times()[33], 3.56)

        self.failUnlessEqual([x['Time'] for x in self.reco[5:10]],
                             [0.82, 0.93, 0.98, 1.02, 1.08])

if __name__ == "__main__":
    unittest.main()
