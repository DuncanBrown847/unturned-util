import PySimpleGUI as sg
from pynput.keyboard import Listener as kListener, Key, KeyCode, Controller as kController
from pynput.mouse import Listener as mListener, Button, Controller as mController
import threading
import config as cfg
import util.util as util
#tpa1 = [[sg.Text("TPA1")], [sg.In(key = "tpa1target")]]
#tpa2 = [[sg.Text("TPA2")], [sg.In(key = "tpa2target")]]

#sg.theme("DarkBrown4")
#sg.theme("DarkGrey14")

#The purpose of this GUI is to make it easy to set up a config.
class ConfigSetupWindow():
    def __init__(self, config):
        self.config = config
        self.running = False
        
        self.bindobject_combatlogger = cfg.BindObject('combat_log')
        
        sg.theme("DarkGrey14")
        self.window = sg.Window("UnturnedUtil Config Setup", icon = b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAA    \
                                                         f8/9hAAAAAXNSR0IArs4c6QAAAbJJREFUOE+lk7    \
                                                         9LAmEYx7+HaenioII5NZ8KNjgFbupJ5ZDh0KB/h    \
                                                         y1BQ/4dKgVRQUuoRZCtEi0alTSWgnp2Q5qk98bz    \
                                                         xh1Wlw69y3v38nw/7/f58Qr45xI0fTqdZrlcTv+    \
                                                         fxo1Go6xcLvNYXZBMJpmiKH1BmMmwlUolPUj/kC    \
                                                         SJqaoKRVFA+ySIMcYNOZ1OdDodVKtVY0C324Xdb    \
                                                         ofJZEKv19OzWLDZsLqyhOPzOj/7E6DdSrvb7Uar    \
                                                         1YIKoPnyzIWeRQ/IjWEKsViMkQNtBQIByMorGo8    \
                                                         P/GjePM93Ahg6+AkgF4mwiIOzW1jMFh08FUBRmo    \
                                                         v4ehyW4RPaQyesVivZhsPh4KBisfi7iMFgkJfaN    \
                                                         GfGYPCGrbVldIYuLpBlGePxGPX6lCJqABJsRrzo    \
                                                         Dz9QvG4gFAqhUqnA7/fz/Gu1mnENNIDL5UK73ea    \
                                                         Qk4s7LiJxs9nknaEZmZxYPRcCbIRFXN20uOVExI    \
                                                         vTy3tu3efz8ZbSEImiiP77aPfocH/n2yhnMymWy    \
                                                         eYFSZKo9YLRJFL/6c2QUFXVUaFQMOsO9jIptp3N    \
                                                         z3wIBKC08vmv2JmCWa/9E5OH2RH8adlFAAAADmV    \
                                                         YSWZNTQAqAAAACAAAAAAAAADSU5MAAAAASUVORK5CYII=", layout = [
            [sg.TabGroup(key = "tabgroup_main", layout = [
                [sg.Tab("Pause Inputs", key = "tab_pause", layout = [
                    [sg.Text("Activation bind:"), self.bind_button("bind_pause")]
                ])],
                [sg.Tab("Combat Logger", key = "tab_combat_logger", layout = [
                    [sg.Text("Activation bind:"), self.bind_button("bind_combat_log")]
                ])],
                [sg.Tab("AutoTPA", key = "tab_autotpa", layout = [
                    [sg.TabGroup([[self.gen_autotpa(autotpa_index) for autotpa_index in range(config.autotpa_count)]], key = "tabgroup_autotpa")],
                    [sg.Button("Add", key = self.add_autotpa)]
                ])],
                [sg.Tab("Input Spam", key = "tab_inputspam", layout = [
                    [sg.TabGroup([[self.gen_inputspam(inputspam_index) for inputspam_index in range(config.inputspam_count)]], key = "tabgroup_inputspam")],
                    [sg.Button("Add", key = self.add_inputspam)]
                ])],
                [sg.Tab("Quicktype", key = "tab_quicktype", layout = [
                    [sg.TabGroup([[self.gen_quicktype(quicktype_index) for quicktype_index in range(config.quicktype_count)]], key = "tabgroup_quicktype")],
                    [sg.Button("Add", key = self.add_quicktype)]
                ])],
                [sg.Tab("Night Vision", key = "tab_nightvision", layout = [
                    [sg.Text("Activation bind:"), self.bind_button("bind_nightvision")]
                ])]
            ])], 
            [sg.Button("Save", key = self.save), sg.Button("Close", key = self.close)]
        ])
        
        #for i in range(config.autotpa_count):

    #generates an sg.Button with given id. ids correspond to 
    def bind_button(self, id):
        def key(event, values):
            self.window[event].update(" ... ")
            threading.Thread(target = self.new_bind, args = (event, values, id), daemon = True).start()
        return sg.Button(button_text = util.button_text_prettify(self.config[id]), size = (10, 1), key = key)

    def launch(self):
        self.window.finalize()
        self.running = True
    
        while self.running:
            event, values = self.window.read()

            #print("EVENT", event)
            #print("VALUES", values)
            
            if event == sg.WIN_CLOSED:
                self.close(event, values)
            else:
                event(event, values)

    #Functions below are mapped functions (that is, they appear in self.command_dict)
    #All must be of the form func_name(self, event, values) to account for event & values passed to the function
    def close(self, event, values):
        self.running = False
        self.window.close()
    
    def add_autotpa(self, event, values):
        self.window["tabgroup_autotpa"].add_tab(self.gen_autotpa(self.config.autotpa_count)) #add_tab() is crucial; update() cant add tabs
        self.config.autotpa_count += 1

    def gen_autotpa(self, index):
        new_tab = sg.Tab(util.button_text_prettify(self.config[f"target_autotpa_{index}"]) if self.config[f"target_autotpa_{index}"] is not None else f"New AutoTPA {index + 1}", [
            [sg.Text(f"Activation bind:"), self.bind_button(f"bind_autotpa_{index}")], 
            [sg.Text(f"Target:"), sg.In(util.button_text_prettify(self.config[f"target_autotpa_{index}"]), size = (15, 1), key = f"target_autotpa_{index}")]
        ], key = f"tab_autotpa_{index}")
        return new_tab

    def add_inputspam(self, event, values):
        self.window["tabgroup_inputspam"].add_tab(self.gen_inputspam(self.config.inputspam_count)) #add_tab() is crucial; update() cant add tabs
        self.config.inputspam_count += 1

    def gen_inputspam(self, index):
        new_tab = sg.Tab(util.button_text_prettify(self.config[f"target_inputspam_{index}"]) if self.config[f"target_inputspam_{index}"] is not None else f"New Input Spam {index + 1}", [
            [sg.Text(f"Activation bind:"), self.bind_button(f"bind_inputspam_{index}")], 
            [sg.Text(f"Target key:"), self.bind_button(f"target_inputspam_{index}")]
        ], key = f"tab_inputspam_{index}")
        return new_tab

    def add_quicktype(self, event, values):
        self.window["tabgroup_quicktype"].add_tab(self.gen_quicktype(self.config.quicktype_count)) #add_tab() is crucial; update() cant add tabs
        self.config.quicktype_count += 1

    def gen_quicktype(self, index):
        new_tab = sg.Tab(util.button_text_prettify(self.config[f"target_quicktype_{index}"]) if self.config[f"target_inputspam_{index}"] is not None else f"New Quicktype {index + 1}", [
            [sg.Text(f"Activation bind:"), self.bind_button(f"bind_quicktype_{index}")], 
            [sg.Text(f"Target:"), sg.In(util.button_text_prettify(self.config[f"target_quicktype_{index}"]), size = (15, 1), key = f"target_quicktype_{index}")]
        ], key = f"tab_quicktype_{index}")
        return new_tab

    def save(self, event, values):
        for k in values:
            if 'target' in k:
                if values[k] == '' or values[k] is None:
                    self.config.pop(k.replace('target', 'bind'), None) #does not work all the time; TODO: implement better saving system. It will likely involve a lot of if/else
                else:
                    self.config[k] = values[k]
        self.config.save()
    
    #general new bind method, referenced by lambdas
    def new_bind(self, event, values, id):
        #self.window[event].update(" ... ")
    
        bind_event = threading.Event()
        self.key_for_bind = None #using instance variable here because local variables are too ambiguous to be referenced in callbacks (???)
                             #old method: new_bind = []  ;;  new_bind.append(bind) to get a bind
                             #              ^^ interestingly, a local variable that can be referenced - probably something to do with '.append' vs '=' operator
                             
                             #INTERESTING NOTE: The variable name used to be called 'new_bind'. since this method is also called new_bind, this function would effectively rewrite itself to be whatever key you pressed.
                             #  But, since obviously neither KeyCode nor Button objects can be called, the thread created that attempts to get a new bind with this method will try to call the new "function" of the key previously pressed,
                             #  and return a "not callable" error. Weird! Switched the name of this local variable to avoid this.
    
        #callbacks given to 
        def on_click_binding(x, y, button, pressed):
            if pressed:
                self.key_for_bind = button
                keyboard_listener_binding.stop()
                mouse_listener_binding.stop()
                bind_event.set()
    
        def on_press_binding(key):
            #new_bind.append(shift_fix(key))
            self.key_for_bind = key
            keyboard_listener_binding.stop()
            mouse_listener_binding.stop()
            bind_event.set()
        
        mouse_listener_binding = mListener(on_click = on_click_binding)
        keyboard_listener_binding = kListener(on_press = on_press_binding)
    
        mouse_listener_binding.start()
        keyboard_listener_binding.start()
        
        bind_event.wait()
        #new_bind = new_bind[0]
        
        #map bind to new BindObject
        
        #self.config[self.key_for_bind] = id 
        self.config[id] = self.key_for_bind  #NOTE: this is the old (?) method of tying new bindings with IDs, and then converting to relevant functions in handler.py
        
        self.window[event].update(util.button_text_prettify(self.key_for_bind))

    

if __name__ == "__main__":
    print("Start")
    ConfigSetupWindow(cfg.Config(None)).launch()

"""
def __init__(self, delay, button, controller, block_input_when_running = True):
        super(ButtonSpam, self).__init__()
        self.delay = delay
        self.button = button
        self.controller = controller
        
        self.running = False
        self.program_running = True
        
        self.block_input_when_running = block_input_when_running
"""


""" Waits for input and returns first button pressed, mouse button or key
def get_new_bind(window, bind):
    bind_got = threading.Event()

    def on_click_binding(x, y, button, pressed):
        global NEW_BIND
        if pressed:
            NEW_BIND = button
            keyboard_listener_binding.stop()
            mouse_listener_binding.stop()
            bind_got.set()

    def on_press_binding(key):
        global NEW_BIND
        NEW_BIND = shift_fix(key)
        keyboard_listener_binding.stop()
        mouse_listener_binding.stop()
        bind_got.set()

    mouse_listener_binding = mListener(on_click = on_click_binding)
    keyboard_listener_binding = kListener(on_press = on_press_binding)

    mouse_listener_binding.start()
    keyboard_listener_binding.start()
    
    bind_got.wait()
    
    #sends 'new_bind' event with tuple containing bind values
    window.write_event_value('new_bind', (bind, NEW_BIND))
"""