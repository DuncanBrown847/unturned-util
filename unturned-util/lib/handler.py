import combatlogger
import nightvision
import util.inputspam as inputspam
import util.quicktype as quicktype
import util.util as util
import config
import threading
import time
from pynput.keyboard import Listener as kListener, Key, KeyCode, Controller as kController
from pynput.mouse import Listener as mListener, Button, Controller as mController
from collections import defaultdict
import clientsocket

#Handler for keyboard inputs and function management

class Handler():
    def __init__(self, config):
        #pause functionality
        self._paused = False
        self._pause_bind = None
        
        #controllers
        self.m_controller = mController();
        self.k_controller = kController();
        
        #listeners
        #win32_event_filter takes a callback; listener will ignore input if this callback returns false
        #   for kListener: flag 0x10 (16) represents an injected input
        #   for mListener: flag 0x01 (1) represents an injected input
        #   ('injected input' means input generated by this program or others like it; simulated, not from your actual mouse, etc.)
        self.keyboard_listener = kListener(on_press = self._klistener_on_press, on_release = self._klistener_on_release, win32_event_filter = lambda msg, data: data.flags & 16 != 16)
        self.mouse_listener = mListener(on_click = self._mlistener_on_click, win32_event_filter = lambda msg, data: data.flags & 1 != 1)

        #other various handling-related variables
        self._nightvision = nightvision.NightVision("./bin/default_gamma.txt", "./bin/nightvision_gamma.txt")
        self._quicktyper = quicktype.QuickTyper(self.k_controller);

        #map binds to internal functions
        self._map_config(config)
        
        #socket manager for autotpa
        self.client_socket = clientsocket.ClientSocket()

    #This function is needed to map KeyCodes to internal functions (loaded config cannot account for this)
    def _map_config(self, config):
        #idea: config[config[id]] = self.function 
        #      del config[id]
        
        #dict that maps key/button -> function
        self.bind_mapping = defaultdict(lambda: None)
        #list of same thing above, organized for display purposes
        self.bind_mapping_list = []
    
        for key in config:
            if 'target' in key:
                continue
            
            mapping_list_entry = [key, util.button_text_prettify(config[key]), '']
            
            if 'bind_pause' == key:
                #special case, map pause bind outside of the dict
                self._pause_bind = config[key]

            elif 'bind_autotpa' in key:
                self.bind_mapping[config[key]] = self.autotpa_gen(config[key.replace('bind', 'target')])
                mapping_list_entry[2] = util.button_text_prettify(config[key.replace('bind', 'target')])

            elif 'bind_inputspam' in key:
                self.bind_mapping[config[key]] = self.inputspam_gen(config[key.replace('bind', 'target')])
                mapping_list_entry[2] = util.button_text_prettify(config[key.replace('bind', 'target')])

            elif 'bind_quicktype' in key:
                self.bind_mapping[config[key]] = self.quicktype_gen(config[key.replace('bind', 'target')])
                mapping_list_entry[2] = util.button_text_prettify(config[key.replace('bind', 'target')])

            else:
                self.bind_mapping[config[key]] = Handler.__dict__[key[5:]] #__dict__ eg: 'bind_combat_log' -> self.combat_log
                #Note that since Handler is not an instance (self has no methods in __dict__), self has to be passed manually into function calls. 
            
            self.bind_mapping_list.append(mapping_list_entry)

    #attempts connection to a hosted server given n ip and a username to connect with
    def attempt_connection(self, ip, port, username): 
        if self._connected:
            return False
        
        try:
            self.sock.connect((ip, port))
        except ConnectionRefusedError:
            printfs('Connection to server refused!')
            return False
        except Exception as e:
            printfs(f'Connection failed: {e}')
            return False
        
        self._connected = True
        self.sock.send(username.encode('utf-8')) #server will accept username right after connection
        printfs('Connected to server!')
        self.recv_thread.start()
        return True

    #returns 
    def get_bind_mapping_list(self):
        return self.bind_mapping_list

    #Listener callbacks. Each func retrieves mapped function from mapping and calls it. 
    def _klistener_on_press(self, key):
        self._handle(key, True)

    def _klistener_on_release(self, key):
        self._handle(key, False)

    def _mlistener_on_click(self, x, y, button, pressed):
        self._handle(button, pressed)

    def _handle(self, key, state):
        if key == self._pause_bind:
            self.pause(state)
            print("paused:", self._paused)
        elif not self._paused:
            func = self.bind_mapping[key]
            if func is not None:
                print(f"calling {self.bind_mapping[key].__name__}, state {state}")
                func(self, state) #see above note line 74

    def start(self):
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        
        self._nightvision.release()

    #start of features
    def pause(self, state):
        if state:
            self._paused = not self._paused

    def combat_log(self, state):
        if state:
            combatlogger.combat_log()
    
    def nightvision(self, state):
        if state:
            self._nightvision.toggle()
    
    def autotpa_gen(self, target):
        def autotpa(self, state):
            if state:
                self._quicktyper.quick_type(f'/tpa {target}')
                self.client_socket.send(f'[AutoTPA] {target}')
                #TODO: add autoTPA functionality
        return autotpa
    
    def inputspam_gen(self, target):
        new_inputspam = inputspam.InputSpamThread(0.015, target, self.m_controller if isinstance(target, Button) else self.k_controller)
        #new_inputspam.start() #thread starts automatically
        
        def inputspam_toggle(self, state):
            if state:
                new_inputspam.start_spam()
            else:
                new_inputspam.stop_spam()
        return inputspam_toggle
    
    def quicktype_gen(self, target):
        def quicktype(self, state):
            if state:
                self._quicktyper.quick_type(target)
        return quicktype
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # To add another feature, all that is required is to create a new function here (of the form funcname(self, state)) and make a new window for it in guiconfig.py
    # Make sure the 'id' tag in the button generation function is in the form 'bind_funcname' (eg: bind_combat_log)
    # Extra consideration might be needed in the mapping step above depending on the nature of the function.
    
if __name__ == "__main__":
    cfg = config.Config('./bin/config.txt')
    cfg.load()
    cfg.display()
    hnd = Handler(cfg)
    hnd.start()
    input("enter to cnt")
    
    