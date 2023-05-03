import sys
import os

def parseChangeSettingsInput(raw_in):
    ret = {
        'valid': False,
        'setting': '',
        'value': ''
    }

    parts = raw_in.split(' ')

    if len(parts) == 2:
        if parts[0] == '/set':
            to_change = parts[1]

            if '=' in to_change:
                change_parts = to_change.split('=')
                setting = change_parts[0]
                new_val = change_parts[1]

                if setting == 'resx':
                    if validate_resx(new_val):
                        ret['valid'] = True
                elif setting == 'resy':
                    if validate_resy(new_val):
                        ret['valid'] = True
                elif setting == 'framerate':
                    if validate_framerate(new_val):
                        ret['valid'] = True
                elif setting == 'sensitivity':
                    if validate_threshold(new_val):
                        ret['valid'] = True
                
                if ret['valid']:
                    ret['setting'] = setting
                    ret['value'] = new_val
    
    return ret


def validate_resx(val):
    # Must be integer between ? and ?
    ret = False

    if isValidInt(val):
        if int(val) > 100 and int(val) < 1921:
            ret = True

    return ret
    
def validate_resy(val):
    # Must be integer between ? and ?
    ret = False

    if isValidInt(val):
        if int(val) > 100 and int(val) < 1281:
            ret = True

    return ret

def validate_threshold(val):
    # Must be integer between ? and ?
    ret = False

    if isValidInt(val):
        if int(val) > 4 and int(val) < 40:
            ret = True
    
    return ret

def validate_framerate(val):
    # Must be integer between 5 and 60
    ret = False

    if isValidInt(val):
        if int(val) > 4 and int(val) < 60:
            ret = True
    
    return ret

def isValidInt(s):
    try: 
        int(str(s))
        return True
    except ValueError:
        return False