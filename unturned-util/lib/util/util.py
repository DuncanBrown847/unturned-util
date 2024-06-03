from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button

""" Various helper functions used throughout the project """
#returns more readable string representation of a given KeyCode/Key/Button
def button_text_prettify(bind):
    #Null value case:
    if bind == None:
        return ''

    #pynput.KeyCode case:
    elif isinstance(bind, KeyCode):
        return str(bind)[1]

    #pynput.Key case:
    elif isinstance(bind, Key):
        return bind.name

    #pynput.Button case:
    elif isinstance(bind, Button):
        if bind.name == 'left':
            return 'mouse1'
        elif bind.name == 'right':
            return 'mouse2'
        elif bind.name == 'middle':
            return 'mouse3'
        else:
            return f'mouse{str(3 + int(bind.name[-1]))}'

    #Boolean case:
    elif type(bind) == bool:
        if bind:
            return 'Yes'
        else:
            return 'No'

    #Default case:
    else:
        return str(bind)

    #Obsolete condition unturned.exe path
    """ 
    elif type(bind) == str and len(bind) > 42:
        return bind[:39] + '...'
    """

#Returns lowercase version of a given KeyCode
#Important because pressing shift may cause pynput to ignore input (KeyCode.H instead of KeyCode.h, for example)
#this func is sketch; TODO redo
def shift_fix(bind):
    if isinstance(bind, KeyCode):
        try:
            #to lowercase
            if (ord(str(bind).strip("\'\"")) >= 65 and ord(str(bind).strip("\'\"")) <= 90):
                return KeyCode.from_char(chr(ord(str(bind).strip("\'\"")) + 32))
        except:
            return bind
    return bind
    
#IMPORTANT FOOTNOTE:
#   This file has also been plagued by Windows Defender.
#   Seems like the same case as in config.py: too many variables named 'key'.
#   It will now be protocal from this point onward to use 'bind' when naming a variable that corresponds to a keyboard or button press.
