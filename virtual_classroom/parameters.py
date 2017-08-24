import pkg_resources
import os

_parameters = None


def get_parameters():
    if _parameters is None:
        parse_config_file()
    return _parameters


def parse_config_file():
    global _parameters
    try:
        contents = open("default_parameters.txt", "rb")
    except:
        print("Could not open default_parameters.txt. Using global config file instead.")
        contents = pkg_resources.resource_stream(__name__, "default_parameters.txt")
    _parameters = {} if _parameters is None else _parameters
    for line in contents.readlines():
        key, value = line.decode().split(":")
        process_value = value[:-1].lower()
        if process_value in ("false", "no", "nei"):
            _parameters[key] = False
        else:
            _parameters[key] = value[:-1]
    contents.close()



