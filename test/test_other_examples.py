import os, pytest, random, subprocess
from unittest import TestCase


class TestOther_examples(TestCase):
    ## UTILITY METHODS
    def get_oexamples_dir(self):
        return os.path.join(os.path.dirname(__file__), "../other-examples")

    def get_data_dir(self):
        return os.path.join(os.path.dirname(__file__), "demo/ds001/sub-01/anat")

    ##TESTS
    def test_create_histo(self):
        command = [os.path.join(self.get_oexamples_dir()
                                , "gen_histo.py")
            , "-b", "5"
            , os.path.join("./", self.get_data_dir())]
        print(command)
        try:
            self.actual_result = subprocess.call(self, command)
        except:
            print("Failed. Error!")

        self.expected_result = "[(0.0, 6412336), (819.0, 26374), (1638.0, 163), (2457.0, 26), (3276.0, 13)]"
        self.assertTrue(self.actual_result == self.expected_result)