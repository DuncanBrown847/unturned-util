import ctypes
import ctypes.wintypes as wintypes
import time
import unittest

#Defining windows functions in python
#Opted not to use win32api due to less functionality (eg ReleaseDC has no return in win32api)
GetDC = ctypes.windll.user32.GetDC
GetDC.argtypes = [wintypes.HWND]
GetDC.restype = wintypes.HDC

ReleaseDC = ctypes.windll.user32.ReleaseDC
ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
ReleaseDC.restype = bool

SetDeviceGammaRamp = ctypes.windll.gdi32.SetDeviceGammaRamp
SetDeviceGammaRamp.argtypes = [wintypes.HDC, wintypes.LPVOID] #hdc, pointer to table
SetDeviceGammaRamp.restype = bool

GetDeviceGammaRamp = ctypes.windll.gdi32.GetDeviceGammaRamp
GetDeviceGammaRamp.argtypes = [wintypes.HDC, wintypes.LPVOID] #hdc, pointer to table
GetDeviceGammaRamp.restype = bool

""" Night Vision """
#gamma file format: 3 long lines appended with \n. Spaces only between numbers. Lines correspond to R,G,B in that order.
#example:
#0 256 512 [...] 65280\n
#0 256 512 [...] 65280\n
#0 256 512 [...] 65280\n

#loads premade gamma settings for nv
def load_gamma(gamma_filename):
    gamma_table = ((wintypes.WORD * 256) * 3)()

    with open(gamma_filename, 'r') as file:
        for i, line in enumerate(file.readlines()):
            current = line[:-1].split(" ")
            for j, num in enumerate(current):
                gamma_table[i][j] = int(num)

    #return gamma table
    return gamma_table

#Saves current gamma settings
def save_gamma(gamma_filename, gamma_table):
    with open(gamma_filename, 'w') as file:
        for row in gamma_table:
            file.write(" ".join(map(str, row)) + "\n") #map ints to strs to make join work
    

""" Class for managing gamma changes """
class NightVision():
    def __init__(self, dg_filename, nvg_filename):
        #if anny errors occur... send to client, client can handle and program can run w/o nvg
        try:
            self.default_gamma_table = load_gamma(dg_filename)
            self.nightvision_gamma_table = load_gamma(nvg_filename)
        except FileNotFoundError as e:
            raise e
        
        self.hdc = wintypes.HDC(GetDC(None))
        if not self.hdc:
            raise RuntimeError("GetDC failure") #I can do better
        
        self.nightvision_toggle = False

    #sets gammas based on already constructed gamma arrays
    def set_default_gamma(self):
        SetDeviceGammaRamp(self.hdc, self.default_gamma_table)
        self.nightvision_toggle = False
    
    def set_nightvision_gamma(self):
        SetDeviceGammaRamp(self.hdc, self.nightvision_gamma_table)
        self.nightvision_toggle = True
    
    def toggle(self):
        if self.nightvision_toggle:
            self.set_default_gamma()
        else:
            self.set_nightvision_gamma()
    
    def release(self):
        if self.hdc:
            ReleaseDC(None, self.hdc)

""" unit test """
class TestNightVision(unittest.TestCase):
    def setUp(self):
        self.night_vision = NightVision("../bin/default_gamma.txt", "../bin/nightvision_gamma.txt")

    def tearDown(self):
        self.night_vision.release()

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            nv = NightVision("file1.txt", "file2.txt")

        with self.assertRaises(FileNotFoundError):
            nv = NightVision("../bin/default_gamma.txt", "file2.txt")
    
    def test_hdc_handling(self):
        hdc = GetDC(None)
        self.assertTrue(hdc)
        self.assertTrue(ReleaseDC(None, hdc))

    def setting_nightvision_gamma(self):
        current_gamma_table = ((wintypes.WORD * 256) * 3)()
        self.night_vision.set_nightvision_gamma()
        self.assertTrue(GetDeviceGammaRamp(self.night_vision.hdc, current_gamma_table))
        self.assertEqual(list(map(list, current_gamma_table)), list(map(list, self.night_vision.nightvision_gamma_table)))

    def setting_default_gamma(self):
        current_gamma_table = ((wintypes.WORD * 256) * 3)()
        self.night_vision.set_default_gamma()
        self.assertTrue(GetDeviceGammaRamp(self.night_vision.hdc, current_gamma_table))
        self.assertEqual(list(map(list, current_gamma_table)), list(map(list, self.night_vision.default_gamma_table)))
    
    def test_setting_gamma(self):
        self.setting_nightvision_gamma()
        self.setting_default_gamma() #maintain right order
    
    def test_toggle(self):
        current_gamma_table = ((wintypes.WORD * 256) * 3)()
        #time.sleep(1)
        self.night_vision.toggle()
        self.assertTrue(GetDeviceGammaRamp(self.night_vision.hdc, current_gamma_table))
        self.assertEqual(list(map(list, current_gamma_table)), list(map(list, self.night_vision.nightvision_gamma_table)))
        
        self.night_vision.toggle()
        self.assertTrue(GetDeviceGammaRamp(self.night_vision.hdc, current_gamma_table))
        self.assertEqual(list(map(list, current_gamma_table)), list(map(list, self.night_vision.default_gamma_table)))

if __name__ == "__main__":
    unittest.main()

    