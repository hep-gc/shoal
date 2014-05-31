import unittest
from shoal_server import utilities
 
class HaversineTest(unittest.TestCase):
    """
    This class implements tests for the methods found in the
    shoal_server.utilities module.
    """

    def setUp(self):
        # Some coordinates used in the tests:
        self.seattle = [47.621800, -122.350326]
        self.olympia = [47.041917, -122.893766]
        

    def tearDown(self):
        # Nothing to do for now...
        pass
    

    def testHaversineToSameLocation(self):
        """
        Test to make sure Havesine to the same coordinate returns a 
        distance of 0.0.
        """
        self.assertEqual(utilities.haversine(self.seattle[0], self.seattle[1],self.seattle[0], self.seattle[1]), 0.0)


    def testHaversineSeattleToOlympia(self):
        """
        Simple test of the distance between Seattle and Olympia.
        """
        d = utilities.haversine(self.seattle[0], self.seattle[1],
                                self.olympia[0], self.olympia[1])
        print 'Distance between Seattle and Olympia: %f' % (d)
        self.assertEqual(d, 76.39)


    def testHaversineBothDirections(self):
        """
        Simple test to make sure our Haversine implementation returns the
        same results for both directions.
        """
        self.assertEqual(utilities.haversine(self.seattle[0], self.seattle[1],
                                self.olympia[0], self.olympia[1]),
                         utilities.haversine(self.olympia[0], self.olympia[1],
                                self.seattle[0], self.seattle[1]))



if __name__ == '__main__':
    unittest.main()
