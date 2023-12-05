###################################################
# File Name     : test.py
# Creation Date : 21-06-2023
# Last Modified : Wed 21 Jun 2023 09:10:40 AM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################

import unittest

def add(a, b):
    return a + b

class TestMathFunctions(unittest.TestCase):

    def test_add(self):
        result = add(2, 3)
        self.assertEqual(result, 5)  # Check if the result is equal to 5

        result = add(-2, 3)
        self.assertEqual(result, 1)  # Check if the result is equal to 1

        result = add(0, 0)
        self.assertEqual(result, 0)  # Check if the result is equal to 0

if __name__ == '__main__':
    unittest.main()
