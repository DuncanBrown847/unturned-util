import os
import unittest

""" Combat logger """
def combat_log():
    return os.system("TASKKILL /F /IM unturned.exe")

""" unit tests """
class TestCombatLog(unittest.TestCase):
    def test_combat_logger(self):
        self.assertTrue(combat_log())
    
if __name__ == "__main__":
    unittest.main()