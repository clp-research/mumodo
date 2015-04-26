"""
Test file for the corpus.py package

This file tests the mumodo corpus functionallity, and in particular:

Creating a mumodo object
Creating resource objects
Adding resource objects to a mumodo
Serializing a mumodo
Creating a mumodo from a serialization
Creating a mumodo from a file
Write a mumodo to a file

"""

import unittest, os
import mumodo.corpus as cp

class MumodoTest(unittest.TestCase):

    def setUp(self):
        path_to_player = 'python test_player.py'
        self.test_mumodo = cp.Mumodo(name='A test mumodo object',
                                     description='A test mumodo object',
                                     url='[a.text.url]',
                                     localpath='data')
        self.VideoResource = cp.VideoResource(name='the_video',
                                         description='a test video resource',
                                            filename='testvideoresource.mp4',
                                              player=path_to_player,
                                              units='seconds',
                                              channel=0)
        self.AudioResource = cp.AudioResource(name='the_audio',
                                          description='a test audio resource',
                                             filename='testaudioresource.wav',
                                               player=path_to_player,
                                               units='seconds',
                                               channel=0)
        self.XIOStreamResource = cp.XIOStreamResource(name='tracked_xio',
                                     description='a test XIO stream resource',
                                            filename='testxioresource.xio.gz',
                                                      units='ms',
                                    sensorname='VeniceHubReplay/Venice/Body1',
                                            kwargs={'timestamp_offset': 10025})
        self.CSVStreamResource = cp.CSVStreamResource(name='tracked_csv',
                                                       units='ms',
                                     description='a test CSV stream resource',
                                                  filename='testxioascsv.csv',
                                     sensorname='VeniceHubReplay/Venice/Body1')
        self.PickledStreamResource = cp.PickledStreamResource(name='tracked_p',
                                                               units='ms',
                                  description='a test pickled stream resource',
                                                     filename='testpickledxio',
                                      sensorname='VeniceHubReplay/Venice/Body1')
        self.IntervalResource = cp.TextGridTierResource(name='interval_tgt',
                                                        units='seconds',
                                                  filename='testres.TextGrid',
                                                        tiername='S')
        self.PointResource = cp.TextGridTierResource(name='point_tgt',
                                                     units='seconds',
                                                  filename='testres.TextGrid',
                                                     tiername='CLAPS')
        self.IntervalCSVResource = cp.CSVTierResource(name='interval_csv',
                                                      units='seconds',
                                             filename='testintervalascsv.csv')
        self.PointCSVResource = cp.CSVTierResource(name='point_csv',
                                                   units='seconds',
                                               filename='testpointsascsv.csv')
        self.IntervalPickledResource = cp.PickledTierResource(name='interval_p',
                                                              units='seconds',
                                                  filename='testintervalpickle')
        self.PointPickledResource = cp.PickledTierResource(name='point_p',
                                                           units='seconds',
                                                     filename='testpointpickle')
        self.ImageResource = cp.ImageResource(name='image',
                                              filename='testimage.png')
        self.TextResource = cp.TextResource(name='text',
                                            filename='testres.txt',
                                            encoding='utf-16')

        self.CSVResource = cp.CSVResource(name='CSV',
                                          filename='testcsv.csv',
                                          kwargs={'sep': '\t'})

        self.BinaryResource = cp.BinaryResource(name='binary',
                                              filename='testaudioresource.wav')

        self.Resource = cp.Resource(name="generic", filename="test.eaf")

        self.test_mumodo.add_resource(self.VideoResource)
        self.test_mumodo.add_resource(self.AudioResource)
        self.test_mumodo.add_resource(self.XIOStreamResource)
        self.test_mumodo.add_resource(self.CSVStreamResource)
        self.test_mumodo.add_resource(self.PickledStreamResource)
        self.test_mumodo.add_resource(self.PointResource)
        self.test_mumodo.add_resource(self.IntervalResource)
        self.test_mumodo.add_resource(self.IntervalCSVResource)
        self.test_mumodo.add_resource(self.PointCSVResource)
        self.test_mumodo.add_resource(self.IntervalPickledResource)
        self.test_mumodo.add_resource(self.PointPickledResource)
        self.test_mumodo.add_resource(self.ImageResource)
        self.test_mumodo.add_resource(self.TextResource)
        self.test_mumodo.add_resource(self.CSVResource)
        self.test_mumodo.add_resource(self.BinaryResource)
        self.test_mumodo.add_resource(self.Resource)

        self.ser = cp.serialize_mumodo(self.test_mumodo)
        self.build = cp.build_mumodo(self.ser)[0]

        cp.write_mumodo_to_file([self.test_mumodo], "test_mumodo.mmd")
        self.from_file = cp.read_mumodo_from_file('test_mumodo.mmd')[0]

        cp.write_mumodo_to_file([self.test_mumodo],
                                "test_mumodo_enc.mmd",
                                encoding='utf-16')
        self.from_file_enc = cp.read_mumodo_from_file('test_mumodo_enc.mmd',
                                                      encoding='utf-16')[0]

        cp.write_mumodo_to_file([cp.Mumodo(), cp.Mumodo(), self.test_mumodo],
                                "many_mumodos.mmd")
        self.from_many = cp.read_mumodo_from_file('many_mumodos.mmd')[2]

        self.other_localpath = cp.read_mumodo_from_file('test_mumodo.mmd')[0]
        self.other_localpath.set_localpath("otherpath")

    def test_mumodo_object(self):
        #names of resources are returned correctly
        self.assertEqual(self.test_mumodo.get_resource_names()[0], 'CSV')
        self.assertEqual(len(self.test_mumodo.get_resource_names()), 16)

        #get the name
        self.assertEqual(self.test_mumodo.get_name(), 'A test mumodo object')

        #the correct objects are returned after iteration
        self.assertEqual(list(self.test_mumodo)[1].get_name(), 'generic')
        self.assertEqual(len(list(self.test_mumodo)), 16)

        #the correct object is returned by item access
        self.assertEqual(self.test_mumodo['point_p'].get_name(), 'point_p')
        #no object is returned if a non existing name is given
        self.assertIsNone(self.test_mumodo['Non-existent'])
        #do not allow a resource to be added if there is already one with
        #the same name
        self.assertEqual(self.test_mumodo.add_resource(self.PointResource), -1)
        #do not allow a resource with a name that is None to be added
        self.assertEqual(self.test_mumodo.add_resource(cp.Resource()), -1)
        #see if the local path was set correctly for the resources
        self.assertEqual(self.other_localpath['point_p'].get_path_prefix(),
                         'otherpath')

    def test_serialization(self):
        #serialize and de-serialize
        self.assertEqual(self.ser, cp.serialize_mumodo(self.build))
        #de-serialize from file
        self.assertEqual(self.ser, cp.serialize_mumodo(self.from_file))
        #de-serialize from file with non-default encoding
        self.assertEqual(self.ser, cp.serialize_mumodo(self.from_file_enc))
        #de-serialize from file with many mumodos
        self.assertEqual(self.ser, cp.serialize_mumodo(self.from_many))


    def test_resource_object(self):
        #Basic attributes of resources
        self.assertEqual(self.ImageResource.get_name(), "image")
        self.assertEqual(self.VideoResource.get_units(), "seconds")
        self.assertEqual(self.PointPickledResource.get_path_prefix(), "data")
        self.assertEqual(self.IntervalPickledResource.get_filepath(),
                         "data/testintervalpickle")
        #Test all types
        self.assertEqual(self.TextResource.get_type(), "TextResource")
        self.assertEqual(self.AudioResource.get_type(), "AudioResource")
        self.assertEqual(self.Resource.get_type(), "GenericResource")
        self.assertEqual(self.AudioResource.get_type(), "AudioResource")
        self.assertEqual(self.XIOStreamResource.get_type(), "StreamResource")
        self.assertEqual(self.CSVStreamResource.get_type(), "StreamResource")
        self.assertEqual(self.PickledStreamResource.get_type(),
                         "StreamResource")
        self.assertEqual(self.PointResource.get_type(), "TierResource")
        self.assertEqual(self.PointCSVResource.get_type(), "TierResource")
        self.assertEqual(self.PointPickledResource.get_type(), "TierResource")

        self.assertEqual(self.IntervalResource.get_type(), "TierResource")
        self.assertEqual(self.IntervalCSVResource.get_type(), "TierResource")
        self.assertEqual(self.IntervalPickledResource.get_type(),
                         "TierResource")
        self.assertEqual(self.ImageResource.get_type(), "ImageResource")
        self.assertEqual(self.CSVResource.get_type(), "CSVResource")
        self.assertEqual(self.BinaryResource.get_type(), "BinaryResource")


    def test_AV_resources(self):
        self.assertEqual(self.VideoResource.get_player(),
                         'python test_player.py')
        self.assertEqual(self.AudioResource.get_channel(), 0)
        self.assertIsNotNone(self.VideoResource.get_video())
        self.assertIsNotNone(self.AudioResource.get_audio())
        self.assertEqual(self.VideoResource.get_video().duration, 1.0)
        self.assertEqual(self.AudioResource.get_audio().duration, 1.0)
        self.assertEqual(self.AudioResource.get_slice(0.1, 0.5).duration, 0.4)
        self.assertEqual(self.VideoResource.get_slice(0.1, 0.5).duration,
                         0.4)
        self.assertIsNone(self.AudioResource.show())
        self.assertIsNone(self.VideoResource.show())

    def test_stream_resources(self):
        #Check items access
        self.assertEqual(self.XIOStreamResource.get_streamframe().loc\
                              [10025, 'JointPositions3'][0].x,
                         0.949964)
        #Check slicing
        self.assertEqual(self.XIOStreamResource.get_slice(10900, 11000)\
                              ['JointPositions3'].iloc[0][0].x,
                         0.954108)
        #Check equality of storage types
        self.assertTrue((self.XIOStreamResource.get_streamframe()\
                          ['JointPositions3'].map(lambda x: str(x)) == \
                         self.CSVStreamResource.get_streamframe()\
                          ['JointPositions3'].map(lambda x: str(x))).all())
        self.assertTrue((self.XIOStreamResource.get_streamframe()\
                          ['JointPositions3'].map(lambda x: str(x)) == \
                         self.PickledStreamResource.get_streamframe()\
                          ['JointPositions3'].map(lambda x: str(x))).all())

    def test_tier_resources(self):
        #check additional attributes
        self.assertEqual(self.IntervalResource.get_tiername(), 'S')
        self.assertEqual(self.PointResource.get_tiername(), 'CLAPS')
        #Check items access
        self.assertEqual(self.IntervalResource.get_tier().loc[0, 'text'],
                         u"Hello")
        self.assertEqual(self.PointResource.get_tier().loc[0, 'mark'],
                         u'First Clap')
        #check slicing
        self.assertEqual(self.IntervalResource.get_slice(10.0, 11.0)['text']\
                            .iloc[0],
                         u"We have developed Mumodo, and Venice")
        self.assertEqual(self.PointResource.get_slice(11.0, 12.0)['mark']\
                            .iloc[0],
                         u"First Clap")
        #slicing that should return empty DataFrame
        self.assertEqual(len(self.PointResource.get_slice(12.0, 13.0)), 0)

        #Check equality of storage types
        self.assertTrue((self.IntervalResource.get_tier()['text'] == \
                         self.IntervalCSVResource.get_tier()['text']).all())
        self.assertTrue((self.IntervalResource.get_tier()['text'] == \
                         self.IntervalPickledResource.get_tier()['text']).all())
        self.assertTrue((self.PointResource.get_tier()['mark'] == \
                         self.PointCSVResource.get_tier()['mark']).all())
        self.assertTrue((self.PointResource.get_tier()['mark'] == \
                         self.PointPickledResource.get_tier()['mark']).all())

    def test_image_resource(self):
        #check item access
        self.assertEqual(self.ImageResource.get_image().size, (320, 200))

    def test_text_resource(self):
        #check additional attributes
        self.assertEqual(self.TextResource.get_encoding(), "utf-16")
        #check item access
        self.assertEqual(self.TextResource.get_text().split('\n')[0],
                         u'This is a sample text. ')
        self.assertFalse(self.TextResource.get_file_object().closed)
        #make sure we can always reload the object if we closed it
        self.TextResource.get_file_object().close()
        self.assertFalse(self.TextResource.get_file_object().closed)

    def test_binary_resource(self):
        self.assertFalse(self.BinaryResource.get_file_object().closed)
        #make sure we can always reload the object if we closed it
        self.TextResource.get_file_object().close()
        self.assertFalse(self.BinaryResource.get_file_object().closed)
        #read 4 bytes
        self.assertEqual(self.BinaryResource.get_file_object().read(4), 'RIFF')

    def test_csv_resource(self):
        #check item access
        self.assertEqual(self.CSVResource.get_table()['text'][0], 'Hello')

    def test_resource(self):
        #check item access
        self.assertEqual(self.Resource.get_filepath(), 'data/test.eaf')

    def tearDown(self):
        os.system("rm *.mmd")

if __name__ == "__main__":
    unittest.main()



