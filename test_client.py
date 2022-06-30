from unittest import TestCase
import numpy as np

from client import compute_weights_from_dbms


class Test(TestCase):
    def test_compute_weights_from_dbms(self):

        dbms = np.array([-30, -40, -50])
        expected_weights = np.array([0.900900901, 0.0900900901, 0.00900900901])

        weights = compute_weights_from_dbms(dbms)

        np.testing.assert_array_almost_equal(expected_weights, weights)