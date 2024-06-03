import time
import threading
import unittest

""" Class for creating new threads used for spamming a particular key/mouse button """
class InputSpamThread(threading.Thread):
    def __init__(self, delay, button, controller):
        super().__init__()
        self.delay = delay
        self.button = button
        self.controller = controller
        self.running = True
        self.daemon = True #modern
        self.spam_signal = threading.Event()
        
        
        #print(f"starting new inputspamthread with button {self.button}")
        self.start() #starts thread and calls run()

    def start_spam(self):
        self.spam_signal.set()

    def stop_spam(self):
        self.spam_signal.clear()

    def toggle_spam(self):
        if self.spam_signal.is_set():
            self.stop_spam()
        else:
            self.start_spam()

    #Force exits thread early. Not needed since thread is a daemon
    def exit(self):
        self.running = False
        self.stop_spam()

    #overrides from threading.Thread; runs when started
    def run(self):
        while self.running:
            self.spam_signal.wait()
            if not self.running:
                break #break if not running; this clause exists to prevent situations with exit()
            self.controller.press(self.button)
            self.controller.release(self.button)
            time.sleep(self.delay) #sleeps for given delay before pressing again. Constrained by unturned servers
        #time.sleep(0.1) #CRUCIAL. Even though it seems useless, this small delay prevents busy waiting from destroying program responsiveness

""" unit tests """
class TestInputSpamThread(unittest.TestCase):
    def setUp(self):
        class TestButton():
            pass

        class TestController():
            def __init__(self):
                self.press_count = 0
                self.release_count = 0
            def press(self, button):
                self.press_count += 1
            def release(self, button):
                self.release_count += 1

        self.button_spam = InputSpamThread(0.01, TestButton(), TestController())
        #self.button_spam.start() #use start() to "start thread engine"; no longer needed

    def test_basic_check(self):
        self.button_spam.start_spam()
        time.sleep(0.1)
        self.button_spam.stop_spam()
        
        self.assertEqual(self.button_spam.controller.press_count, self.button_spam.controller.release_count)
        self.assertNotEqual(self.button_spam.controller.press_count, 0)

    """
    def test_consistency(self):
        self.button_spam.start_spam()
        time.sleep(1)
        self.button_spam.stop_spam()
        
        self.assertTrue(self.button_spam.controller.press_count in range(90, 101))
    """

if __name__ == "__main__":
    unittest.main()
