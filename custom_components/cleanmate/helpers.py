import json
import socket

def parse_value(value):
    if(isinstance(value, str)):
        try:
            return parse_value(json.loads(value))
        except:
            pass
        semi_values = value.split(';')
        if(len(semi_values) > 1):
            return list(map(parse_value, semi_values))
        comma_values = value.split(',')
        if(len(comma_values) > 1):
            return list(map(parse_value, comma_values))
        if(value.replace('.','',1).isdigit()):
            return int(value)
    if(isinstance(value, dict)):
        return {k: parse_value(v) for k, v in value.items()}
    if(isinstance(value, list)):
        return list(map(parse_value, value))
    return value

def hostAvailable(host: str, port: int) -> bool:
    success = True
    s = socket.socket()
    try:
        s.connect((host, port)) 
    except Exception:
        success =  False
    finally:
        s.close()
    return success