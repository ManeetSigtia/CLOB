import unittest
import xmlrunner

if __name__ == "__main__":
    tests = unittest.defaultTestLoader.discover(".", pattern="test_*.py")
    runner = xmlrunner.XMLTestRunner(output="test-reports")
    runner.run(tests)
