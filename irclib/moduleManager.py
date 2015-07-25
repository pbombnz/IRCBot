import sys


class IRCModulesManager(object):

    def __init__(self, irc_bot: object):
        # Declaring variables that will hold the module names
        self.loaded_modules_instance = list()

        self.loaded_modules = set()
        self.loading_modules = set()  # Note, that the loading and unloading sets are constructed due to the fact we can not
        self.unloading_modules = set()  # edit the loaded_modules set when being iterated.
        self.unloaded_modules = set()

        self.irc_bot = irc_bot

        self.load_all_modules()

    def load_all_modules(self):
        for module in sys.modules:
            module_name = sys.modules[module].__name__

            if module_name.startswith("modules."):
                self.loaded_modules.add(module_name)
                console_print("MODULE-LOAD", "loaded " + str(module_name) + ".")

        self.initialise_all_modules()

    def reload_module(self, module_name: str):
        """
            Reloads an individual module that was previously loaded.

            :param module_name: The full-name of the module to be reloaded
            :return: Returns True if the IRC module was reloaded successfully, otherwise return False.
        """

        # Firstly, we check if if the module being reloaded is the 'resources' module or an IRC module as they are
        # the only two types of valid inputs when reloading.
        if module_name == "resources":
            # attempt to reload the resources modules and return True or false depending if was successful or not, respectively.
            try:
                importlib.reload(sys.modules["resources"])
                console_print("MODULE-RELOAD", "Reloaded " + str(module_name) + ".")
                return True
            except IOError:
                console_print("MODULE-RELOAD", "Unable to load " + str(module_name) + ".")
                return False

        if module_name.startswith("modules."):
            # Checks if the module's name is even a IRC module
            if module_name in self.loaded_modules or module_name in self.unloaded_modules:
                # Knowing its an IRC module, we have to attempt to reload the module
                try:
                    importlib.reload(sys.modules[module_name])
                    # If the module was was previously unloaded, we have to add it to the 'loaded_modules' set in order for it to be callable.
                    if module_name in self.unloaded_modules:
                        self.loading_modules.add(module_name)
                    # Initialise the newly loaded module
                    self.initialise_module(module_name)
                    console_print("MODULE-RELOAD", "Reloaded " + str(module_name) + ".")
                    return True
                except IOError:
                    # A compiler error occured and the module could not be loaded, hence we return False
                    console_print("MODULE-RELOAD", "Unable to load " + str(module_name) + ".")
                    return False

        # if the module's name was not the 'resources' module or an IRC module (or simply doesnt exist), then
        # there is no significance in reloading it hence why we return False
        return False

    def reload_all_modules(self):
        """
            Reloads all IRC Modules by reloading the 'modules' module which will result in all individual modules
            being reloaded. It's also useful when you want to import a new module into the bot without restarting.
            Simply add a new import line into the modules' folder's __init__.py and use this method and the new
            module will be loaded (if there was no compiler errors present)

            :return: bool. True, if all modules were reloaded successfully, otherwise False.
        """
        try:
            importlib.reload(resources)  # Reloading modules
            importlib.reload(modules)  # Reloading modules
        except IOError:
            # Indicates compiler errors in one of the modules, which also means all none of the other modules can be loaded
            console_print("MODULE-RELOAD",
                          "A specific module is causing all other modules to not be loaded due to a compiler error.")
            return False

        # clearing all module sets (except loaded) because all modules are reloaded anyways there is not going to be an unloaded module
        self.loading_modules.clear()
        self.unloading_modules.clear()
        self.unloaded_modules.clear()

        self.load_all_modules()
        # Return true to indicate that all modules were loaded successfully
        return True

    def unload_module(self, module_name: str):
        """
            Unloads the specified module from execution of IRC events

            :param module_name: The full name of the module you would like to unload
            :return: Returns True, if unloading was sucessful otherwise false.
        """

        if module_name in self.loaded_modules:
            self.unloading_modules.add(module_name)
            console_print("MODULE-UNLOAD", "Unloaded " + str(module_name) + ".")
            return True
        else:
            return False  # The module is already (or is going to be) unloaded.

    def modify_module_sets(self):
        if len(self.loading_modules) > 0:
            for module_name in self.loading_modules:
                self.unloaded_modules.discard(module_name)
                self.loaded_modules.add(module_name)
                self.initialise_module(module_name)
            self.loading_modules.clear()

        if len(self.unloading_modules) > 0:
            for module_name in self.unloading_modules:
                self.loaded_modules.discard(module_name)
                self.unloaded_modules.add(module_name)
            self.unloading_modules.clear()

    def is_method_in_module(self, module_name: str, function_name: str):
        if hasattr(sys.modules[module_name], function_name):
            if callable(getattr(sys.modules[module_name], function_name)):
                return True
        return False

    def initialise_all_modules(self):
        for module_name in self.loaded_modules:
            self.initialise_module(module_name)

    def initialise_module(self, module_name):
        if self.is_method_in_module(module_name, 'on_init'):
            getattr(sys.modules[module_name], 'on_init')(self.irc_bot)

    def on_process_forever(self):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_process_forever'):
                try:
                    getattr(sys.modules[module_name], 'on_process_forever')(self.irc_bot)
                except Exception as error:
                    console_print("MODULE-ERROR",
                                  "MODULE: " + str(module_name) + " | INPUT: Constant Call | ERROR MESSAGE: " + str(
                                      error))
                    self.unload_module(module_name)

    def on_raw_numeric(self, mask, numeric, target, message):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_raw_numeric'):
                getattr(sys.modules[module_name], 'on_raw_numeric')(mask, numeric, target, message)

    def on_nick_change(self, user_mask, user_old_nick, user_new_nick):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_nick_change'):
                getattr(sys.modules[module_name], 'on_nick_change')(user_mask, user_old_nick, user_new_nick)

    def on_action(self, user_mask, user_nick, channel, action):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_action'):
                getattr(sys.modules[module_name], 'on_action')(user_mask, user_nick, channel, action)

    def on_channel_pm(self, user_mask, user_nick, channel, message):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_channel_pm'):
                getattr(sys.modules[module_name], 'on_channel_pm')(user_mask, user_nick, channel, message)

    def on_ctcp(self, user_mask, user_nick, target, ctcp_command, ctcp_params):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_ctcp'):
                getattr(sys.modules[module_name], 'on_ctcp')(user_mask, user_nick, target, ctcp_command, ctcp_params)

    def on_user_pm(self, user_mask, user_nick, target, message):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_user_pm'):
                getattr(sys.modules[module_name], 'on_user_pm')(user_mask, user_nick, target, message)

    def on_kick(self, user_mask, user_nick, channel, target, message):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_kick'):
                getattr(sys.modules[module_name], 'on_kick')(user_mask, user_nick, channel, target, message)

    def on_invite(self, user_mask, user_nick, target, channel):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_invite'):
                getattr(sys.modules[module_name], 'on_invite')(user_mask, user_nick, target, channel)

    def on_join(self, user_mask, user_nick, channel):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_join'):
                getattr(sys.modules[module_name], 'on_join')(user_mask, user_nick, channel)

    def on_part(self, user_mask, user_nick, channel, part_message):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_part'):
                getattr(sys.modules[module_name], 'on_part')(user_mask, user_nick, channel, part_message)

    def on_quit(self, user_mask, user_nick, quit_message):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_quit'):
                getattr(sys.modules[module_name], 'on_quit')(user_mask, user_nick, quit_message)

    def on_channel_notice(self, user_mask, user_nick, channel, message):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_channel_notice'):
                getattr(sys.modules[module_name], 'on_channel_notice')(user_mask, user_nick, channel, message)

    def on_user_notice(self, user_mask, user_nick, target, message):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_user_notice'):
                getattr(sys.modules[module_name], 'on_user_notice')(user_mask, user_nick, target, message)

    def on_notice_auth(self, mask, message):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_notice_auth'):
                getattr(sys.modules[module_name], 'on_notice_auth')(mask, message)

    def on_ping(self, ping_reply):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_ping'):
                getattr(sys.modules[module_name], 'on_ping')(ping_reply)

    def on_mode_user(self, user, target, mode_sting):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_mode_user'):
                getattr(sys.modules[module_name], 'on_mode_user')(user, target, mode_sting)

    def on_mode_channel_setbyuser(self, user_mask, user_nick, channel, mode_sting, mode_params):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_mode_channel_setbyuser'):
                getattr(sys.modules[module_name], 'on_mode_channel_setbyuser')(user_mask, user_nick, channel,
                                                                               mode_sting, mode_params)

    def on_mode_channel_setbyserv(self, serv_user, channel, mode_sting, mode_params):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_mode_channel_setbyserv'):
                getattr(sys.modules[module_name], 'on_mode_channel_setbyserv')(serv_user, channel, mode_sting,
                                                                               mode_params)

    def on_error(self, error_message):
        for module_name in self.loaded_modules:
            if self.is_method_in_module(module_name, 'on_error'):
                getattr(sys.modules[module_name], 'on_error')(error_message)
