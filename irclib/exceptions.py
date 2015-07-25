class IRCModuleException(Exception):
    def __init__(self, module_name: str, exception: Exception):
        self.module_name = module_name
        self.exception = exception
        pass
