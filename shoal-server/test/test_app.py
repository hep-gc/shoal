import unittest
from utilities_tests import HaversineTest

def main():
    # Add your TestCase subclasses to the array below:
    testList = [HaversineTest]

    testLoader = unittest.TestLoader()
 
    caseList = []
    for testCase in testList:
        testSuite = testLoader.loadTestsFromTestCase(testCase)
        caseList.append(testSuite)
 
    newSuite = unittest.TestSuite(caseList)
    testRunner = unittest.TextTestRunner()
    testRunner.run(newSuite)


if __name__ == '__main__':
    main()
