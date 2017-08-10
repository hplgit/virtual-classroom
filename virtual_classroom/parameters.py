import pkg_resources

_parameters = None


def get_parameters():
    if _parameters is None:
        parse_config_file()
    return _parameters


def parse_config_file():
    global _parameters
    contents = pkg_resources.resource_stream(__name__, "default_parameters.txt")
    _parameters = {} if _parameters is None else _parameters
    for line in contents.readlines():
        key, value = line.split(':')
        _parameters[key] = value[:-1]
    contents.close()



