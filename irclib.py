# Importing standard modules
import socket
import threading
import ssl
import time
import re
import sys
import random
import importlib
import importlib.util
from collections import OrderedDict

# Importing bot modules
import modules
import resources

# static variables initialised
PING_TIMEOUT = 300.0  # the amount of time (in secs) to disconnect a socket that is inactive or improperly disconnected
CONNECTION_ATTEMPTS = 100  # the number of attempts to connect on failure

# Regular expressions of common IRC events
IRC_EVENT_PATTERN = {'RAW-NUMERIC': ":(.*)\s(\d\d\d)\s(.*)\s:(.*)",
                     'NICK-CHANGE': ":(.*)!(.*)@(.*)\sNICK\s:(.*)",
                     'ACTION': ":(.*)!(.*)@(.*)\sPRIVMSG\s(.*)\s:\001ACTION\s(.*)\001",
                     'CHANNEL-PM': ":(.*)!(.*)@(.*)\sPRIVMSG\s([#|&].*)\s:(?!\x01ACTION)(.*)",
                     'CTCP': ":(.*)!(.*)@(.*)\sPRIVMSG\s(?![#&])(.*)\s:\001(?!ACTION)(\S+)\s*(.*)\001",
                     'USER-PM': ":(.*)!(.*)@(.*)\sPRIVMSG\s[^#|&](.*)\s:(?!\001)(.*)",
                     'KICK': ":(.*)!(.*)@(.*)\sKICK\s(.*)\s(.*)\s:(.*)",
                     'INVITE': ":(.*)!(.*)@(.*)\sINVITE\s(.*)\s:(.*)",
                     'JOIN': ":(.*)!(.*)@(.*)\sJOIN\s:(.*)",
                     'PART': ":(.*)!(.*)@(.*)\sPART\s([#|&]\w*)\s?:?(.*)",
                     'QUIT': ":(.*)!(.*)@(.*)\sQUIT\s:(.*)",
                     'CHANNEL-NOTICE': ":(.*)!(.*)@(.*)\sNOTICE\s([#|&].*)\s:(.*)",
                     'USER-NOTICE': ":(.*)!(.*)@(.*)\sNOTICE\s(?![#|&])(.*)\s:(.*)",
                     'NOTICE-AUTH': ":(.*)\sNOTICE\sAUTH\s:(.*)",
                     'PING': "PING\s:(.*)",
                     'MODE-USER': ":(\w*)\sMODE\s(.*)\s:(\S*)",
                     'MODE-CHANNEL-SETBYUSER': ":(.*)!(.*)@(.*)\sMODE\s([#|&].*)\s([+|-][a-z+-]*)\s(.*)",
                     'MODE-CHANNEL-SETBYSERV': ":(.*)\sMODE\s([#|&].*)\s( .*)\s(.*)",
                     'ERROR': "ERROR :(.*)"}


def console_print(type_str: str, message: str):
    """ A formatted way to print to console. Shows information in a more visually pleasing way """
    print("[" + type_str + "] " + message)


class _CaseInsensitiveDict(dict):
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


class Bot(object):
    """
        This class handles all the logic of the IRC Bot. This includes handling incoming and outgoing messages.
        Parsing data recieved from the server so the user of the library doesn't have to implement certain activities
        themselves such as collecting channel data.
    """

    # Initialising variables for channel information
    channel_info = _CaseInsensitiveDict()
    channel_info_names_list_index = 0

    def __init__(self, server: str, port: int, is_ssl: bool, nick_name: str, user_name: str, real_name: str, password: str=None):
        """
            Initialise the Bot object and defines bot parameters

            :param server: The server address of the IRC Server you wish to connect to
            :param port: The port of the server address of the IRC Server you wish to connect to
            :param is_ssl: Whether you would like to connect with SSL or not
            :param nick_name: The nickname used for the bot. This is the displayed to users when the bot is communicating
            :param user_name: The user name used for the bot. This is generally only see in the bot's host mask
            :param real_name: The real name used for the bot. This can be any string which is displayed in the WHOIS command
            :param password: Optional. Insert a password if the user requires identification
            :return object: An object of the Bot
        """
        self.server = server
        self.port = port
        self.ssl = is_ssl
        self.user_name = user_name
        self.nick_name = nick_name
        self.real_name = real_name
        self.password = password
        self.host_mask = [str(), str(), str()]
        self.ircConnection = None
        self.is_connect = False

        # Declaring variables that will hold the module names
        self.loaded_modules = set()
        self.loading_modules = set()    # Note, that the loading and unloading sets are constructed due to the fact we can not
        self.unloading_modules = set()  # edit the loaded_modules set when being iterated.
        self.unloaded_modules = set()

        # Displays information about the bot in console
        console_print("INIT", "==============================================================")
        console_print("INIT", "Python IRC Bot Framework - By Prashant Bhikhu (PBombNZ) [2015]")
        console_print("INIT", "==============================================================")
        console_print("CONFIG", "SERVER: {0} PORT: {1} SSL: {2}".format(str(server), str(port), str(ssl)))
        console_print("CONFIG", "NICKNAME: \"{0}\" USERNAME: \"{1}\" REALNAME: \"{2}\"".format(str(nick_name), str(user_name), str(real_name)))
        console_print("CONFIG", "PASSWORD: {0}".format(str(password)))
        console_print("INIT", "")

        # Adds all IRC modules' names to the loaded_modules set meaning that all modules are loaded on execution
        for module in sys.modules:
            module_name = sys.modules[module].__name__

            if module_name.startswith("modules."):
                self.loaded_modules.add(module_name)
                console_print("MODULE-LOAD", "loaded " + str(module_name) + ".")

    def connect(self):
        """
            Creates a socket connection to the specified server and port and sends an initial messages
            that send information about the client to the server.
        """
        # Creates the socket and set an appropriate timeout
        self.ircConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ircConnection.settimeout(PING_TIMEOUT)
        console_print("CONNECT", "Socket Created.")

        # Loop until we are connected
        for i in range(1, CONNECTION_ATTEMPTS + 1):
            console_print("CONNECT", "Attempting to connect...[ Attempt " + str(i) + " of " + str(CONNECTION_ATTEMPTS) + " ]")
            try:
                # Connects to server
                self.ircConnection.connect((self.server, self.port))
                # if we are told that the client connects with SSL, then we wrap the current socket with SSL in order
                # to make it SSL
                if self.ssl:
                    self.ircConnection = ssl.wrap_socket(self.ircConnection)
                console_print("CONNECT", "Connected Successfully.")
                break
            except IOError:
                # when we have reached the number of number of attempted connection, we raise an error indicating there is
                #  a problem otherwise continue attempting to connect
                if i == CONNECTION_ATTEMPTS:
                    raise IOError("Cannot resolve server. Please check if the server and port parameters are correct.")
                else:
                    console_print("CONNECT", "Connection attempt failed.")
                    time.sleep(3)  # Just stop a few seconds so the connection attempts do go fast and it doesnt act like a mini DDoS attack

        # Sending all initial messages to the server
        self.ircConnection.send(
            ('USER ' + str(self.user_name) + ' host servname : ' + str(self.real_name) + '\r\n').encode())
        self.ircConnection.send(('NICK ' + str(self.nick_name) + '\r\n').encode())

        if self.password is None:
            self.ircConnection.send(('NS IDENTIFY ' + str(self.password) + '\r\n').encode())
            self.ircConnection.send('HS ON\r\n'.encode())
        # once, we have connected, we execute the on_connected method and tell the bot that the connect is active
        self.is_connect = True
        self.on_connected()

    def on_connected(self):
        for module_name in self.loaded_modules:
            if hasattr(sys.modules[module_name], 'on_init'):
                if callable(getattr(sys.modules[module_name], 'on_init')):
                    sys.modules[module_name].on_init(self)

        threading.Thread(target=self._receive_incoming_data).start()
        threading.Thread(target=self.on_constant_module_call).start()

    def on_constant_module_call(self):
        while self.is_connect:
            time.sleep(1)
            for module_name in self.loaded_modules:
                if hasattr(sys.modules[module_name], 'on_constant_call') and callable(getattr(sys.modules[module_name], 'on_constant_call')):
                    try:
                        sys.modules[module_name].on_constant_call(self)
                    except Exception as error:
                        console_print("MODULE-ERROR", "MODULE: " + str(module_name) + " | INPUT: Constant Call | ERROR MESSAGE: " + str(error))
                        self.unload_module(module_name)

    def _receive_incoming_data(self):
        while self.is_connect:
            try:
                raw_data = self.ircConnection.recv(1024)
            except IOError:
                self.quit(error_message="socket timeout")
                break

            raw_data = raw_data.decode('utf-8').split('\r\n')
            for data in raw_data:
                if len(data) > 0:
                    # print(data)
                    threading.Thread(target=self.parse_raw_data(data)).start()

    def parse_raw_data(self, data):
        for event_type in IRC_EVENT_PATTERN:
            match = re.match(IRC_EVENT_PATTERN[event_type], data)
            if match:
                parsed_data = re.findall(IRC_EVENT_PATTERN[event_type], data)[0]

                console_print("DATA-STREAM", "EVENT TYPE: " + event_type + " | DATA: " + str(parsed_data))

                if event_type == 'ERROR':
                    if parsed_data.startswith('Closing Link'):
                        self.quit(error_message="closing link error")

                elif event_type == 'RAW-NUMERIC':
                    mask = parsed_data[0]
                    numeric = parsed_data[1]
                    target = parsed_data[2]
                    message = parsed_data[3]
                    self.on_raw_numeric(mask, numeric, target, message)

                elif event_type == 'MODE-CHANNEL-SETBYUSER':
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    channel = parsed_data[3]
                    mode_string = parsed_data[4]
                    mode_params = parsed_data[5].split()
                    self.on_mode_channel_set_by_user(user_mask, channel, mode_string, mode_params)

                elif event_type == 'INVITE':
                    self.join(parsed_data[4])

                elif event_type == 'PING':
                    self.send_raw_message('PONG :' + parsed_data[0][0])

                elif event_type == 'KICK':
                    channel = parsed_data[3].lower()
                    user_kicked = parsed_data[4]
                    for op in self.channel_info[channel]:
                        if user_kicked in self.channel_info[channel][op]:
                            self.channel_info[channel][op].remove(user_kicked)

                    if user_kicked == self.nick_name:
                        self.join(parsed_data[3])

                elif event_type == 'NICK-CHANGE':
                    user_org_nick = parsed_data[0]
                    user_new_nick = parsed_data[3]

                    for channel in self.channel_info:
                        for op in self.channel_info[channel]:
                            if user_org_nick in self.channel_info[channel][op]:
                                self.channel_info[channel][op].remove(user_org_nick)
                                self.channel_info[channel][op].append(user_new_nick)
                                break

                    if user_org_nick == self.nick_name:
                        self.nick_name = user_new_nick
                        self.host_mask[0] = user_new_nick

                elif event_type == 'QUIT':
                    username = parsed_data[0]
                    for channel in self.channel_info:
                        for op in self.channel_info[channel]:
                            if username in self.channel_info[channel][op]:
                                self.channel_info[channel][op].remove(username)

                elif event_type == 'JOIN':
                    user = parsed_data[0]
                    channel = parsed_data[3]
                    if user != self.nick_name:
                        self.channel_info[channel]["Regular"].add(user)

                elif event_type == 'PART':
                    username = parsed_data[0]
                    channel = parsed_data[3]

                    if username == self.nick_name:
                        del self.channel_info[channel]
                    else:
                        for op in self.channel_info[channel]:
                            if username in self.channel_info[channel][op]:
                                self.channel_info[channel][op].remove(username)

                self.call_modules(event_type, parsed_data)

    def on_raw_numeric(self, bot_mask, numeric, target, message):
        del bot_mask

        if numeric == '311':
            target = target.split()
            if target[1] == self.nick_name:
                self.host_mask = [target[1], target[2], target[3]]
                print(self.host_mask)

        elif numeric == '376':
            self.send_raw_message('WHOIS ' + str(self.nick_name))

        elif numeric == '353':
            channel = target.split()[2].lower()

            if self.channel_info_names_list_index == 0:
                self.channel_info[channel] = OrderedDict()
                self.channel_info[channel]["Owner"] = set()
                self.channel_info[channel]["Admin"] = set()
                self.channel_info[channel]["Operator"] = set()
                self.channel_info[channel]["Half-Operator"] = set()
                self.channel_info[channel]["Voice"] = set()
                self.channel_info[channel]["Regular"] = set()

            self.channel_info_names_list_index += 1
            # collecting actually string of nicks
            users_list = message.split()
            # Sorting each name into right admin group
            for username_op in users_list:
                username = username_op[1:]
                if username_op.startswith('~'):
                    self.channel_info[channel]["Owner"].add(username)
                elif username_op.startswith('&'):
                    self.channel_info[channel]["Admin"].add(username)
                elif username_op.startswith('@'):
                    self.channel_info[channel]["Operator"].add(username)
                elif username_op.startswith('%'):
                    self.channel_info[channel]["Half-Operator"].add(username)
                elif username_op.startswith('+'):
                    self.channel_info[channel]["Voice"].add(username)
                else:
                    self.channel_info[channel]["Regular"].add(username_op)
                    continue
                self.channel_info[channel]["Regular"].add(username)
        elif numeric == '366':
            self.channel_info_names_list_index = 0
        elif numeric == '433':
            self.change_nick_name(str(self.nick_name) + str(random.randint(10, 10000)))
            if self.password != "":
                self.send_raw_message('NS GHOST ' + str(self.nick_name) + ' ' + str(self.password))
                self.change_nick_name(str(self.nick_name))
                self.identify()
                self.send_raw_message('MODE ' + str(self.nick_name) + ' +B')
        elif numeric == '482':
            self.send_private_message(target, "ERROR: Bot must have channel administration privileges for you "
                                              "to use this command in this channel.")

    def on_mode_channel_set_by_user(self, user_mask, channel, mode_string, mode_params):
        del user_mask

        # modes_a = "k f L q a o h v b e I".split()
        modes_b = "l j".split()
        modes_c = "p s m n t i r R c O A Q K V C u z N S M T G".split()
        # A = Mode that adds or removes a nick or address to a list. Always has a parameter.
        #     (NOW COMBINED AT THE END OF B)
        # A = Mode that changes a setting and always has a parameter.
        # B = Mode that changes a setting and only has a parameter when set.
        # C = Mode that changes a setting and never has a parameter.

        current_mode_symbol = str()

        for mode_index in range(len(mode_string)):
            mode_char = mode_string[mode_index]

            if mode_char == '+':
                current_mode_symbol = '+'
                continue
            elif mode_char == '-':
                current_mode_symbol = '-'
                continue

            if current_mode_symbol == '+':
                if mode_char == 'b':
                    ban_mask = mode_params[0].replace('.', '\.').replace('!', '\!').replace('*', '.+')
                    ban_mask_re = re.compile(ban_mask)
                    bot_mask_str = self.host_mask[0] + "!" + self.host_mask[1] + "@" + self.host_mask[2]
                    ban_match = ban_mask_re.match(bot_mask_str)
                    if ban_match:
                        for op in self.channel_info[channel]:
                            if op == "Regular" or op == "Voice":
                                continue
                            if self.nick_name in self.channel_info[channel][op]:
                                self.send_raw_message('MODE ' + str(channel) + ' -b ' + mode_params[0])
                                break

                if mode_char in ['q', 'a', 'o', 'h', 'v']:
                    promoted_nick_name = mode_params[0]
                    if mode_char == 'q':
                        self.channel_info[channel]["Owner"].add(promoted_nick_name)
                    elif mode_char == 'a':
                        self.channel_info[channel]["Admin"].add(promoted_nick_name)
                    elif mode_char == 'o':
                        self.channel_info[channel]["Operator"].add(promoted_nick_name)
                    elif mode_char == 'h':
                        self.channel_info[channel]["Half-Operator"].add(promoted_nick_name)
                    elif mode_char == 'v':
                        self.channel_info[channel]["Voice"].add(promoted_nick_name)

                if mode_char not in modes_c:
                    mode_params.pop(0)
            elif current_mode_symbol == '-':
                if mode_char in ['q', 'a', 'o', 'h', 'v']:
                    demoted_op = str()
                    if mode_char == 'q':
                        demoted_op = "Owner"
                    elif mode_char == 'a':
                        demoted_op = "Admin"
                    elif mode_char == 'o':
                        demoted_op = "Operator"
                    elif mode_char == 'h':
                        demoted_op = "Half-Operator"
                    elif mode_char == 'v':
                        demoted_op = "Voice"

                    demoted_nick_name = mode_params[0]
                    if demoted_nick_name in self.channel_info[channel][demoted_op]:
                        self.channel_info[channel][demoted_op].remove(demoted_nick_name)

                if mode_char in modes_c or mode_char in modes_b:
                    pass
                else:
                    mode_params.remove(mode_params[0])

    def call_modules(self, event_type, parsed_data):
        for module_name in self.loaded_modules:
            try:
                if event_type == "RAW-NUMERIC":
                    mask = parsed_data[0]
                    numeric = parsed_data[1]
                    message = parsed_data[3]
                    if hasattr(sys.modules[module_name], 'on_raw_numeric'):
                        if callable(getattr(sys.modules[module_name], 'on_raw_numeric')):
                            sys.modules[module_name].on_raw_numeric(self, mask, numeric, message)

                elif event_type == "NICK-CHANGE":
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    user_old_nick = parsed_data[0]
                    user_new_nick = parsed_data[1]
                    if hasattr(sys.modules[module_name], 'on_nick_change'):
                        if callable(getattr(sys.modules[module_name], 'on_nick_change')):
                            sys.modules[module_name].on_nick_change(self, user_mask, user_old_nick, user_new_nick)

                elif event_type == "ACTION":
                    user_nick = parsed_data[0]
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    channel = parsed_data[3]
                    action = parsed_data[4]
                    if hasattr(sys.modules[module_name], 'on_action'):
                        if callable(getattr(sys.modules[module_name], 'on_action')):
                            sys.modules[module_name].on_action(self, user_mask, user_nick, channel, action)

                elif event_type == "CHANNEL-PM":
                    user_nick = parsed_data[0]
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    channel = parsed_data[3]
                    message = parsed_data[4]
                    if hasattr(sys.modules[module_name], 'on_channel_pm'):
                        if callable(getattr(sys.modules[module_name], 'on_channel_pm')):
                            sys.modules[module_name].on_channel_pm(self, user_mask, user_nick, channel, message)

                elif event_type == "CTCP":
                    user_nick = parsed_data[0]
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    target = parsed_data[3]
                    ctcp_params = parsed_data[4].split()
                    ctcp_command = ctcp_params[0]
                    if len(ctcp_params) > 1:
                        ctcp_params = ctcp_params.pop(0)
                    else:
                        ctcp_params = list()

                    if hasattr(sys.modules[module_name], 'on_ctcp'):
                        if callable(getattr(sys.modules[module_name], 'on_ctcp')):
                            sys.modules[module_name].on_ctcp(self, user_mask, user_nick, target, ctcp_command,
                                                             ctcp_params)

                elif event_type == "USER-PM":
                    user_nick = parsed_data[0]
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    target = parsed_data[3]
                    message = parsed_data[4]
                    if hasattr(sys.modules[module_name], 'on_user_pm'):
                        if callable(getattr(sys.modules[module_name], 'on_user_pm')):
                            sys.modules[module_name].on_user_pm(self, user_mask, user_nick, target, message)

                elif event_type == "KICK":
                    user_nick = parsed_data[0]
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    channel = parsed_data[3]
                    target = parsed_data[4]
                    message = parsed_data[5]
                    if hasattr(sys.modules[module_name], 'on_kick'):
                        if callable(getattr(sys.modules[module_name], 'on_kick')):
                            sys.modules[module_name].on_kick(self, user_mask, user_nick, channel, target, message)

                elif event_type == "INVITE":
                    user_nick = parsed_data[0]
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    target = parsed_data[3]
                    channel = parsed_data[4]
                    if hasattr(sys.modules[module_name], 'on_invite'):
                        if callable(getattr(sys.modules[module_name], 'on_invite')):
                            sys.modules[module_name].on_invite(self, user_mask, user_nick, target, channel)

                elif event_type == "JOIN":
                    user_nick = parsed_data[0]
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    channel = parsed_data[3]
                    if hasattr(sys.modules[module_name], 'on_join'):
                        if callable(getattr(sys.modules[module_name], 'on_join')):
                            sys.modules[module_name].on_join(self, user_mask, user_nick, channel)

                elif event_type == "PART":
                    user_nick = parsed_data[0]
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    channel = parsed_data[3]
                    part_message = parsed_data[4]
                    if hasattr(sys.modules[module_name], 'on_part'):
                        if callable(getattr(sys.modules[module_name], 'on_part')):
                            sys.modules[module_name].on_part(self, user_mask, user_nick, channel, part_message)

                elif event_type == "QUIT":
                    user_nick = parsed_data[0]
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    quit_message = parsed_data[3]
                    if hasattr(sys.modules[module_name], 'on_quit'):
                        if callable(getattr(sys.modules[module_name], 'on_quit')):
                            sys.modules[module_name].on_quit(self, user_mask, user_nick, quit_message)

                elif event_type == "CHANNEL-NOTICE":
                    user_nick = parsed_data[0]
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    channel = parsed_data[3]
                    message = parsed_data[4]
                    if hasattr(sys.modules[module_name], 'on_channel_notice'):
                        if callable(getattr(sys.modules[module_name], 'on_channel_notice')):
                            sys.modules[module_name].on_channel_notice(self, user_mask, user_nick, channel, message)

                elif event_type == "USER-NOTICE":
                    user_nick = parsed_data[0]
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    target = parsed_data[3]
                    message = parsed_data[4]
                    if hasattr(sys.modules[module_name], 'on_user_notice'):
                        if callable(getattr(sys.modules[module_name], 'on_user_notice')):
                            sys.modules[module_name].on_user_notice(self, user_mask, user_nick, target, message)

                elif event_type == "NOTICE-AUTH":
                    mask = parsed_data[0]
                    message = parsed_data[1]
                    if hasattr(sys.modules[module_name], 'on_notice_auth'):
                        if callable(getattr(sys.modules[module_name], 'on_notice_auth')):
                            sys.modules[module_name].on_notice_auth(self, mask, message)

                elif event_type == "PING":
                    ping_reply = parsed_data[0]
                    if hasattr(sys.modules[module_name], 'on_ping'):
                        if callable(getattr(sys.modules[module_name], 'on_ping')):
                            sys.modules[module_name].on_ping(self, ping_reply)

                elif event_type == "MODE-USER":
                    user = parsed_data[0]
                    target = parsed_data[1]
                    mode_sting = parsed_data[2]
                    if hasattr(sys.modules[module_name], 'on_mode_user'):
                        if callable(getattr(sys.modules[module_name], 'on_mode_user')):
                            sys.modules[module_name].on_mode_user(self, user, target, mode_sting)

                elif event_type == "MODE-CHANNEL-SETBYUSER":
                    user_nick = parsed_data[0]
                    user_mask = [parsed_data[0], parsed_data[1], parsed_data[2]]
                    channel = parsed_data[3]
                    mode_sting = parsed_data[4]
                    mode_params = parsed_data[5]
                    if hasattr(sys.modules[module_name], 'on_mode_channel_setbyuser'):
                        if callable(getattr(sys.modules[module_name], 'on_mode_channel_setbyuser')):
                            sys.modules[module_name].on_mode_channel_setbyuser(self, user_mask, user_nick, channel,
                                                                               mode_sting, mode_params)

                elif event_type == "MODE-CHANNEL-SETBYSERV":
                    serv_user = parsed_data[0]
                    channel = parsed_data[1]
                    mode_sting = parsed_data[2]
                    mode_params = parsed_data[3]
                    if hasattr(sys.modules[module_name], 'on_mode_channel_setbyserv'):
                        if callable(getattr(sys.modules[module_name], 'on_mode_channel_setbyserv')):
                            sys.modules[module_name].on_mode_channel_setbyserv(self, serv_user, channel,
                                                                               mode_sting, mode_params)

                elif event_type == "ERROR":
                    error_message = parsed_data[0]
                    if hasattr(sys.modules[module_name], 'on_error'):
                        if callable(getattr(sys.modules[module_name], 'on_error')):
                            sys.modules[module_name].on_error(self, error_message)

            except Exception as error:
                console_print("MODULE-ERROR",
                              "MODULE: " + module_name + " INPUT: " + str(parsed_data) + " ERROR MESSAGE: " + str(
                                  error))
                self.unload_module(module_name)

        if len(self.loading_modules) > 0:
            for module_name in self.loading_modules:
                self.unloaded_modules.discard(module_name)
                self.loaded_modules.add(module_name)
                if hasattr(sys.modules[module_name], 'on_init'):
                    if callable(getattr(sys.modules[module_name], 'on_init')):
                        sys.modules[module_name].on_init(self)
            self.loading_modules.clear()

        if len(self.unloading_modules) > 0:
            for module_name in self.unloading_modules:
                self.loaded_modules.discard(module_name)
                self.unloaded_modules.add(module_name)
            self.unloading_modules.clear()

    def send_raw_message(self, message):
        """
            Sends a message to the server without any sort of IRC string formatting

            :param message: A Message to the server with IRC string formatting inorder for it to be understood by the server.
        """
        self.ircConnection.send(bytes(str(message) + '\r\n', 'UTF-8'))

    def send_private_message(self, recipient, message):
        """
            Sends a message to a recipient via private message. This is the standard way of messaging recipients in
            either a channel or to a person.

            :param recipient: The person or channel you are going to send the message to.
            :param message:
        """
        self.send_raw_message('PRIVMSG ' + str(recipient) + ' :' + str(message))

    def send_notice_message(self, recipient, message):
        """
            Sends a message to a recipient via notice message. This type of way of messaging recipients is often used
            when you need to get the recipient's attention as generally it alerts the client's IRC client.
            Not commonly used as it can be annoying. Please note that some channels do not permit the use of notice
            messages.

            :param recipient: The person or channel you are going to send the message to.
            :param message:
        """
        self.send_raw_message('NOTICE ' + str(recipient) + ' :' + str(message))

    def send_ctcp_message(self, recipient, ctcp, message=None):
        """
            Sends a CTCP message to a recipient so we can recieve information about the recipient without asking them.

            :param recipient: The person or channel you are going to send the CTCP message to.
            :param ctcp: The type of CTCP reply your requesting
            :param message: Optional. Specify a message if its required by the ctcp type
        """
        # Only send a CTCP message with the message argument if the user specified it
        if message:
            self.send_private_message(str(recipient), '\001' + str(ctcp) + ' ' + str(message) + '\001')
        else:
            self.send_private_message(str(recipient), '\001' + str(ctcp) + '\001')

    def change_nick_name(self, new_nick_name: str):
        """
            Changes the nickname of the bot

            :param new_nick_name: The new nickname you would like to set for the Bot
            :return:
        """
        console_print("BOT-NICK-CHANGE", str(self.nick_name) + " is now known as " + str(new_nick_name))
        # Send a message to the server indicating that you have changed your name.
        self.send_raw_message("NICK " + str(new_nick_name))
        # Changed the fields within the Bot instance
        self.nick_name = new_nick_name
        self.host_mask[0] = new_nick_name

    def join(self, channel, key=None):
        """
            Joins a channel

            :param channel: The name of the channel
            :param key: Optional. If the channel has a key to get in, specify it here.
            :return:
        """
        console_print("BOT-JOIN", "Joined " + str(channel))
        if key:
            self.send_raw_message("JOIN " + str(channel) + " " + str(key))
        else:
            self.send_raw_message("JOIN " + str(channel))

    def part(self, channel, message=None):
        """
            Parts a channel.

            :param channel: The channel you wish to part.
            :param message: Optional. The message you wish to part with
            :return:
        """
        console_print("BOT-PART", "Parted " + str(channel))
        if message is None:
            self.send_raw_message("PART " + str(channel))
        else:
            self.send_raw_message("PART " + str(channel) + " " + str(message))

    def cycle(self, channel, key=None):
        """
            Cylces (Parts and rejoins) a channel.

            :param channel: The channel you wish to cycle through.
            :param key: Optional. If the channel has a key to get in, specify it here.
            :return:
        """
        self.part(channel, "Cycling...")
        self.join(channel, key)

    def identify(self, password=None):
        """
            Sends a message to server to authorise and identify the user

            :param password: Optional. If this argument is present, it tells the Bot to identify using this password
             rather than the one specified within the fields
            :return:
        """
        if password:
            self.send_raw_message("NS IDENTIFY " + str(password))
            self.send_raw_message("HS ON")  # enables your fake vhost if present
            return True
        if self.password:
            self.send_raw_message("NS IDENTIFY " + str(self.password))
            self.send_raw_message("HS ON")  # enables your fake vhost if presen
            return True
        return False

    def quit(self, quit_message: str=None, error_message: str=None, reconnect_on_error: bool=True):
        """
            Closes the IRC connection and performs additonal activities based on whether it the socketed ended
            expected or unexpectedly

            :param quit_message: Optional. The message you would like to show on quit. Only needed if the quit was expected.
            :param error_message: Optional. This message is describes the error in console, if an error is present. Only
                                  needed if the quit was as unexpected.
            :param reconnect_on_error: Optional. Set to True by default. Determines whether you want to reconnect or not
                                       if the quit was as unexpected.
            :return:
        """

        # Depending on the combination of arugments present, we can determine whether to send a QUIT command to the server
        # (if the connection is still active or not) and print a suitable message to console.
        if not quit_message and not error_message:
            self.send_raw_message("QUIT : Python IRC Framework - By Prashant B. (https://github.com/pbombnz)")
            console_print("QUIT", "Bot has disconnected successfully.")

        elif quit_message and not error_message:
            self.send_raw_message("QUIT :" + str(quit_message) + " - Python IRC Framework - By Prashant B. (https://github.com/pbombnz)")
            console_print("QUIT", "Bot has disconnected successfully.")

        elif not quit_message and error_message:
            console_print("QUIT", "Bot has disconnected unexpectedly due to " + str(error_message))

        elif quit_message and error_message:
            console_print("QUIT", "Bot has disconnected unexpectedly due to " + str(error_message))
            self.send_raw_message("QUIT :" + str(quit_message) + " - Python IRC Framework - By Prashant B. (https://github.com/pbombnz)")

        # Clean up variables on quit (regardless if it was an expected quit or not)
        self.ircConnection.close()
        self.is_connect = False
        self.channel_info.clear()
        self.channel_info_names_list_index = 0

        # Reconnect if an error was present, otherwise exit the program
        if error_message and reconnect_on_error:
            console_print("QUIT", "Attempting to reestablish lost connection.")
            self.connect()
        else:
            input("Press Enter to close console...")
            exit()

    def reload_module(self, module_name: str):
        """
            Reloads an individual module that was previously loaded.

            :param module_name: The full-name of the module to be reloaded
            :return: Returns True if the IRC module was reloaded successfully, otherwise return False.
        """

        # Firstly, we check if if the module being reloaded is the 'resources' module or an IRC module as they are
        # the only two types of valid inputs when reloading.
        if module_name.lower() == "resources":
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
                    # If it was previously an unloaded module, we have to add it to the loaded modules set eventually inorder
                    # for it to be callable.
                    if module_name in self.unloaded_modules:
                        self.loading_modules.add(module_name)

                    # The module is not callable and sucessfully reloaded at this point. Now we have to call the on_init
                    # method within the module if present
                    if hasattr(sys.modules[module_name], 'on_init'):
                        if callable(getattr(sys.modules[module_name], 'on_init')):
                            sys.modules[module_name].on_init(self)

                    # Print a success message and return True for the success on reloading the module
                    console_print("MODULE-RELOAD", "Reloaded " + str(module_name) + ".")
                    return True
                except IOError:
                    # A compiler error occured and the module could not be loaded, hence we return False
                    console_print("MODULE-RELOAD", "Unable to load " + str(module_name) + ".")
                    return False

        # if the module's name was not the 'resources' module or an IRC module (or simply doesnt exist), then
        # there is no significance in reloading it hence why we return False
        return False

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

    def reload_all_modules(self):
        """
            Reloads all IRC Modules by reloading the 'modules' module which will result in all individual modules
            being reloaded.

            It's also useful when you want to import a new module into the bot without restarting.
            Simply add a new import line into the modules' folder's __init__.py and use this method and the new
            module will be loaded (if there was no compiler errors present)

            :return: bool. True, if all modules were reloaded successfully, otherwise false.
        """
        try:
            importlib.reload(modules)  # Reloading modules
            # clearing all module sets (except loaded) because all modules are reloaded anyways there is not going to be an unloaded module
            self.loading_modules.clear()
            self.unloading_modules.clear()
            self.unloaded_modules.clear()
            # Iterate through all system modules, and add all IRC modules to the loading set (to be loaded)
            # Note, we cannot add straight to the 'loaded_modules' set because it might violate the fact you cannot edit
            # a data structure that is being iterated through.
            for module in sys.modules:
                module_name = sys.modules[module].__name__

                if module_name.startswith("modules"):
                    self.loading_modules.add(module_name)
                    console_print("MODULE-RELOAD", "Reloaded " + str(module_name) + ".")

                # Check and execute code within the modules if it needs to perform actions on initialisation
                if hasattr(sys.modules[module_name], 'on_init'):
                    if callable(getattr(sys.modules[module_name], 'on_init')):
                        sys.modules[module_name].on_init(self)
            # Return true to indicate that all modules were loaded successfully
            return True
        except IOError:
            # Indicates compiler errors in one of the modules, which also means all none of the other modules can be loaded
            console_print("MODULE-RELOAD", "A specific module is causing all other modules to not be loaded.")
            # Return False to indicate that all modules were not loaded successfully
            return False

    def get_channel_info(self):
        """
            :return: Returns the channel information dictionary. keys are channel names, which also stores a nested dictionary
                     of that channel's specific information
        """
        return self.channel_info

    def get_resources(self):
        """
            :return: returns a 'module' object named resources.
        """
        return resources

    def get_loaded_modules(self):
        """
            :return: A frozenset (immutable set) of the loaded modules. You cannot modify the set.
        """
        return frozenset(self.loaded_modules)

    def get_unloaded_modules(self):
        """
            :return: A frozenset (immutable set) of the unloaded modules. You cannot modify the set.
        """
        return frozenset(self.unloaded_modules)

    def add_attributes(self, **kw):
        """
            Allows for variables to be dynamically added into the instance on runtime. This is handy for modules, that
            have variables that need to be accessed by other modules globally.
        :param kw: keyword arguments used to store dynamic variables within the Bot instance
        """
        self.__dict__.update(kw)
