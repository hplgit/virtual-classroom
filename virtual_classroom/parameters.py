import pkg_resources
import os
import shutil

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
        key, value = line.decode("utf-8").split(":")
        process_value = value[:-1].lower()
        if process_value in ("false", "no", "nei"):
            _parameters[key] = False
        else:
            _parameters[key] = value[:-1]
    contents.close()


def create_local_config_file():
    # TODO: It could be nice to have an interactively created config file.
    #       However it is relatively small and easy to format so really not that useful.
    try:
        open("default_parameters.txt", "rb")
        print("You already have a local default_parameters.txt. Delete this before copying.")
        return
    except:
        pass

    filename = os.path.join(os.path.dirname(__file__), "default_parameters.txt")
    shutil.copy(filename, "default_parameters.txt")
    print("Local configuration file created: default_parameters.txt")
