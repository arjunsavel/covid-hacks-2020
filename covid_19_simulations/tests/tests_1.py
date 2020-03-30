import unittest

import sys
import os
sys.path.append(os.getcwd()[:-16])
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestImports(unittest.TestCase):

	def test_import_0D(self):
		import zero_d
		return
		# self.assertTrue(zero_d in sys.modules)

	def test_import_1D(self):
		import one_d
		return
		# self.assertTrue(one_d in sys.modules)

	def test_import_2D(self):
		import two_d
		return
		# self.assertTrue(two_d not in sys.modules)