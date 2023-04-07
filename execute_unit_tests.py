import unittest

components_dir = 'components'
loader = unittest.TestLoader()
tests = loader.discover(components_dir, pattern='*Test.py')

runner = unittest.TextTestRunner()
result = runner.run(tests)