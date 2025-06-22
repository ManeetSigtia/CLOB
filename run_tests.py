# File: run_tests.py

import unittest


def run_all_tests():
    """
    Discovers and runs all tests in the 'tests' directory.
    """
    # Create a TestLoader instance. The TestLoader is used to create test suites.
    loader = unittest.TestLoader()

    # Use the discover method to find all tests.
    # It starts discovery in the 'tests' directory and looks for any file
    # named 'test*.py'. It will search recursively through all subdirectories.
    suite = loader.discover("tests")

    # Create a TextTestRunner instance to run the suite.
    # verbosity=2 provides more detailed output, listing each test as it runs.
    runner = unittest.TextTestRunner(verbosity=2)

    # Run the test suite.
    print("Starting test discovery and execution...")
    result = runner.run(suite)
    print("Testing complete.")

    # Optional: Exit with a non-zero status code if tests failed, for CI/CD pipelines.
    if not result.wasSuccessful():
        exit(1)


if __name__ == "__main__":
    run_all_tests()
