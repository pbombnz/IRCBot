class IRCDict(dict):
    """
        An Internal class that overrides certain methods of a standard dictionary
        object in order for the keys to be case insensitive.
    """

    def __contains__(self, key):
        return dict.__contains__(self, key.lower())

    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())

    def __setitem__(self, key, value):
        return dict.__setitem__(self, key.lower(), value)


def console_print(type_str: str, message: str):
    """ A formatted way to print to console. Shows information in a more visually pleasing way """
    print("[" + type_str + "] " + message)
