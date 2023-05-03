import unittest
from webapp.changesettings import *

########################################
#         Test Change Settings         #
########################################
class Test_isValidInt(unittest.TestCase):
    def test_ok(self):
        # Test case A. note that all test method names must begin with 'test.'
        assert isValidInt(10) == True, "10 is a valid integer"
    
    def test_str(self):
        # Test case A. note that all test method names must begin with 'test.'
        assert isValidInt("10") == True, "\"10\" is a valid integer"
    
    def test_decemal(self):
        # Test case A. note that all test method names must begin with 'test.'
        assert isValidInt(12.56) == False, "12.56 is not a valid integer"

    def test_decemal_str(self):
        # Test case A. note that all test method names must begin with 'test.'
        assert isValidInt("12.56") == False, "\"12.56\" is not a valid integer"

class Test_parseChangeSettingsInput(unittest.TestCase):
    def setUp(self):
        # setUp gets called before every test in this class.. tearDown gets called after.
        self.invalid = {
            'valid': False,
            'setting': '',
            'value': ''
        }
        
    def tearDown(self):
        # Not necessary, just showing how setUp and tearDown work
        self.invalid = {}

    def test_ok(self):
        # Test case A. note that all test method names must begin with 'test.'
        ret = parseChangeSettingsInput("/set framerate=30")
        assert ret['valid']   == True, "\'/set framerate=30\' is a valid command."
        assert ret['setting'] == "framerate", "\'framerate\' is a valid setting."
        assert ret['value']   == "30", "\'30\' is a valid framerate."
    
    def test_invalid_cmd(self):
        # Test case A. note that all test method names must begin with 'test.'
        ret = parseChangeSettingsInput("/seet framerate=30")
        assert ret['valid']   == self.invalid['valid'], "\'/seet framerate=30\' is an invalid command."
        assert ret['setting'] == self.invalid['setting'], "setting should be empty."
        assert ret['value']   == self.invalid['value'], "value should be empty."
    
    def test_invalid_setting(self):
        # Test case A. note that all test method names must begin with 'test.'
        ret = parseChangeSettingsInput("/set size=30")
        assert ret['valid']   == False, "\'/set size=30\' is an invalid command."
        assert ret['setting'] == "", "setting should be empty."
        assert ret['value']   == "", "value should be empty."

    def test_invalid_symbol(self):
        # Test case A. note that all test method names must begin with 'test.'
        ret = parseChangeSettingsInput("/set size:30")
        assert ret['valid']   == False, "\'/set size:30\' is an invalid command."
        assert ret['setting'] == "", "setting should be empty."
        assert ret['value']   == "", "value should be empty."
    
    def test_invalid_value(self):
        # Test case A. note that all test method names must begin with 'test.'
        ret = parseChangeSettingsInput("/set framerate=30.5")
        assert ret['valid']   == False, "\'/set framerate=30.5\' is an invalid command."
        assert ret['setting'] == "", "setting should be empty."
        assert ret['value']   == "", "value should be empty."
    

if __name__ == "__main__":
    unittest.main() # run all tests
