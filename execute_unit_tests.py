import unittest

tests_dir = "components/tests"
loader = unittest.TestLoader()
tests = loader.discover(tests_dir, pattern="*Test.py")

runner = unittest.TextTestRunner()
result = runner.run(tests)
