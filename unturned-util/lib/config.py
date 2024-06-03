""" Config object, used for managing binds """
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button

#converts string to the needed object
#primarily used in load_config
def string_to_key(string):
    if string == 'None':
        return None
    elif string == 'True':
        return True
    elif string == 'False':
        return False
    elif len(string) == 1: #possible issues here (length may not be 1) TODO
        return KeyCode.from_char(string)
    elif string[:3] == 'Key':
        return Key[string.split('.')[1]]
    elif string[:6] == 'Button':
        return Button[string.split('.')[1]]
    return string

#formats bindings for consistent saving/reading
def save_format(bind):
    if bind == None:
        return 'None'
    elif isinstance(bind, KeyCode):
        return str(bind).strip("\'\"")
    return str(bind)

#Class representing config of the program
#
#Current system: config maps functionalities to keys
#   eg. 'bind_combat_log' => KeyCode('n')
#   map of keys to funcs has to be generated from this binding, which requires a "shift" of the dict
#   special considerations have to be made for non-bind mappings (eg. tpa target)
#
#proposed change: instead map keys to functionalities;
#   this would require restructuring the bind getting procedure, likely new class for representing a functionality, changing handler functionality, 
#   eg. KeyCode('n') => ConfigObject(type: tpa, target: succ)
#       'tpa' would correspond to a function in Handler __init__, and the object would be converted to the proper function then
#   this idea may be difficult to implement with regard to pysimplegui, so for now I am sticking to the old method.
#   pros: straightforward handler init process, better organization of functions at runtime(?), prevents bind conflicts by nature
#   cons: harder to read cfg file, special cases for recording non-bind keys (eg inputspam target button)
#
#   Stick to first idea for now

#This object should consist of a dict mapping binds to their BindObjects
class Config(dict):
    def __init__(self, filename):
        self.autotpa_count = 0
        self.inputspam_count = 0
        self.quicktype_count = 0
        self._filename = filename
        #print(filename, self._filename)

    def save(self):
        with open(self._filename, 'w') as file:
            for k in self:
                file.write(f"{str(k)} :: {save_format(self[k])}\n")

    def load(self):
        with open(self._filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                split_line = line.strip('\n').split(' :: ')

                if "bind_autotpa" in split_line[0]:
                    self.autotpa_count += 1

                if "bind_inputspam" in split_line[0]:
                    self.inputspam_count += 1

                if "bind_quicktype" in split_line[0]:
                    self.quicktype_count += 1

                self[split_line[0]] = string_to_key(split_line[1])

    def __missing__(self, key):
        return None

    def display(self):
        print("disp")
        for x in self:
            print(x, self[x])

#This object represents a single binding. (Config will map binds to these)
class BindObject(dict):
    def __init__(self, feature):
        #represents the feature of this binding
        self.feature = feature

    def __missing__(self, key):
        return None

#IMPORTANT FOOTNOTE!
#   This file has had a particularly bad history with Windows Defender, constantly getting marked as a malicious keylogger since I'm using libraries that are 
#   This was eventually avoided by avoiding naming variable names 'key':
#       In save_format, the parameter 'key' was renamed to 'bind';
#       and in Config.save, the iteration variable 'key' was changed to 'k' (even though this was named to represent keys of hash maps, not keyboards!)
#       However, it should be mentioned that using 'key' in methods like __missing__ or __setitem__ seem to not get tagged

