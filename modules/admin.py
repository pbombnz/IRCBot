import sys
from modules import userDatabase
from io import StringIO


MAX_SPAM = 50


# noinspection PyUnusedLocal
def on_channel_pm(irc, user_mask, user, channel, message):
    command = message.split()

    if command[0].lower() == 'a':
        irc.send_private_message(channel, "b")

    if command[0].lower() == '!join':
        if irc.user_info[user.lower()]["access_level"] >= 1:
            if len(command) == 2:
                irc.join(command[1])
            elif len(command) == 3:
                irc.join(command[1], command[2])
            else:
                irc.send_private_message(channel, "USAGE: !join (Channel) [(Key)]")

    elif command[0].lower() == "!part":
        if irc.user_info[user.lower()]["access_level"] >= 2:
            if len(command) == 2:
                command = message.split(' ', 1)
                irc.part(command[1])
            elif len(command) > 2:
                command = message.split(' ', 2)
                irc.part(command[1], command[2])
            else:
                irc.send_private_message(channel, "USAGE: !part (Channel) [(Message)]")

    elif command[0].lower() == "!cycle":
        if irc.user_info[user.lower()]["access_level"] >= 1:
            if len(command) == 2:
                command = message.split(' ', 1)
                irc.cycle(command[1])
            elif len(command) > 2:
                command = message.split(' ', 2)
                irc.cycle(command[1], command[2])
            else:
                irc.send_private_message(channel, "USAGE: !cycle (Channel) [(Key)]")

    elif command[0].lower() == "!identify":
        if irc.user_info[user.lower()]["access_level"] >= 3:
            if len(command) == 1:
                irc.identify()
            elif len(command) == 2:
                irc.identify(command[1])
            else:
                irc.send_private_message(channel, "USAGE: !identify [(Password)]")

    elif command[0].lower() == "!say":
        if irc.user_info[user.lower()]["access_level"] >= 2:
            if len(command) >= 3:
                command = message.split(' ', 2)
                if len(command[1]) > 0 and len(command[2]) > 0:
                    irc.send_private_message(command[1], command[2])
                else:
                    irc.send_private_message(channel, "USAGE: !say (Channel) (Message)")
            else:
                irc.send_private_message(channel, "USAGE: !say (Channel) (Message)")

    elif command[0].lower() == "!action":
        if irc.user_info[user.lower()]["access_level"] >= 2:
            if len(command) >= 3:
                command = message.split(' ', 2)
                if len(command[1]) > 0 and len(command[2]) > 0:
                    irc.send_private_message(command[1], '\001ACTION ' + str(command[2]) + '\001')
                else:
                    irc.send_private_message(channel, "USAGE: !action (Channel) (Action Message)")
            else:
                irc.send_private_message(channel, "USAGE: !action (Channel) (Action Message)")

    elif command[0].lower() == "!spam":
        if irc.user_info[user.lower()]["access_level"] >= 3:
            command = message.split(' ', 3)
            if len(command) == 4:
                if len(command[1]) > 1 and len(command[2]) > 0 and len(command[3]) > 0:
                    if command[2].isdigit():
                        if int(command[2]) in range(0, MAX_SPAM + 1):
                            for i in range(int(command[2])):
                                irc.send_private_message(command[1], command[3])
                            return
            irc.send_private_message(channel, "USAGE: !spam (Channel/Recipient) (Repetition Number) (Message)")

    elif command[0].lower() == "!raw":
        if irc.user_info[user.lower()]["access_level"] >= 3:
            if len(command) >= 2:
                command = message.split(' ', 1)
                if len(command[1]) > 0:
                    if command[1].lower().startswith('quit'):
                        irc.send_private_message(channel, "ERROR: You cannot disconnect the bot with the RAW command. "
                                                          "Please use !quit.")
                    elif command[1].lower().startswith('ns drop') or command[1].lower().startswith('msg nickserv drop'):
                        irc.send_private_message(channel, "ERROR: You cannot drop this nick via RAW command.")
                    else:
                        irc.sendRawMessage(command[1])
                    return
            irc.send_private_message(channel, 'USAGE: !raw (Server Message)')

    elif command[0].lower() == "!nick":
        if irc.user_info[user.lower()]["access_level"] >= 2:
            if len(command) == 2:
                command = message.split(' ', 1)
                if len(command[1]) > 0:
                    irc.changeNickname(command[1])
                    return
            irc.send_private_message(channel, "USAGE: !nick (Nickname)")

    elif command[0].lower() == "!quit":
        if irc.user_info[user.lower()]["access_level"] >= 3:
            if len(command) == 2 and len(command[1]) > 0:
                command = message.split(' ', 1)
                irc.quit(command[1])
            else:
                irc.quit()

    elif command[0].lower() == "!setbotlevel" or command[0].lower() == "!sbl":
        if irc.user_info[user.lower()]["access_level"] >= 3:
            if len(command) != 3:
                irc.send_private_message(channel, 'USAGE: !s[et]b[ot]l[evel] (Nickname) (Bot Level[0-3])')
                return

            command = message.split(' ', 2)
            if not command[2].isdigit():
                irc.send_private_message(channel, 'USAGE: !s[et]b[ot]l[evel] (Nickname) (Bot Level[0-3]')
                return

            if command[1].lower() == user.lower() and irc.user_info[user.lower()]["access_level"] < 3:
                irc.send_private_message(channel, '5ERROR: You cannot set your own bot level.')
                return

            if int(command[2]) < 0 or int(command[2]) > 3:
                irc.send_private_message(channel, '5ERROR: Access level must be between 0-3.')
                return

            if command[1].lower() in irc.user_info:
                old_access_level = irc.user_info[command[1].lower()]["botLevel"]
                if old_access_level != int(command[2]):
                    irc.user_info[command[1].lower()]["botLevel"] = int(command[2])
                    userDatabase.save_user_database(irc)
                    irc.send_private_message(channel,
                                             '\u00033SUCESS: Bot Level has changed for {0} from {1} to {2}.'.format(
                                                 str(irc.user_info[command[1].lower()]['ircNickName']),
                                                 str(old_access_level), str(command[2])))
                else:
                    irc.send_private_message(channel, '\u00035ERROR: {0} is already set at that level.'.format(
                        str(irc.user_info[command[1].lower()]['ircNickName'])))
            else:
                irc.send_private_message(channel, "5ERROR: '" + str(command[1]) + "' does not exist.")

    elif command[0].lower() == "!botadmins":
        if irc.user_info[user.lower()]["access_level"] >= 1:
            client_admin_list = dict()
            for nick in irc.user_info:
                if irc.user_info[nick]["access_level"] > 0:
                    client_admin_list[irc.user_info[nick]['nick_name']] = irc.user_info[nick]["access_level"]

            for users_ranks in sorted(client_admin_list.items(), key=lambda x: x[1], reverse=True):
                nick, level = users_ranks
                if level == 1:
                    irc.send_private_message(channel, str(nick) + ', Trusted User')
                elif level == 2:
                    irc.send_private_message(channel, str(nick) + ', Bot Admin')
                elif level == 3:
                    irc.send_private_message(channel, str(nick) + ', Bot Owner')

    elif command[0].lower() == "!loadmodule":
        if irc.user_info[user.lower()]["access_level"] >= 3:
            irc.send_private_message(channel, "USAGE: To load a new module, add an import statement into the "
                                              "modules's __init__.py file, then type !reloadmodules in IRC. "
                                              "This will refresh all modules and import new modules.")

    elif command[0].lower() == "!reloadmodule":
        if irc.user_info[user.lower()]["access_level"] >= 3:
            if len(command) != 2:
                irc.send_private_message(channel, "USAGE: !reloadmodule (Module Name)")
                return

            is_reloaded = irc.reload_module(command[1])
            if is_reloaded:
                irc.send_private_message(channel, "3SUCCESS: Module loaded.")
            else:
                irc.send_private_message(channel, "5ERROR: Module is already loaded or does not exist.")

    elif command[0].lower() == "!unloadmodule":
        if irc.user_info[user.lower()]["access_level"] >= 3:
            if len(command) != 2:
                irc.send_private_message(channel, "USAGE: !unloadmodule (Module Name)")
                return

            is_unloaded = irc.unload_module(command[1])
            if is_unloaded:
                irc.send_private_message(channel, "3SUCCESS: Module unloaded.")
            else:
                irc.send_private_message(channel, "5ERROR: Module is already unloaded or does not exist.")

    elif command[0].lower() == "!reloadallmodules":
        if irc.user_info[user.lower()]["access_level"] >= 3:
            if len(command) == 1:
                is_reloaded = irc.reload_all_modules()
                if is_reloaded:
                    irc.send_private_message(channel, "3SUCCESS: All modules reloaded/reimported.")
                else:
                    irc.send_private_message(channel, "5ERROR: Could not reload all modules. "
                                                      "Possibly a compiler error occured with recently modified code.")

    elif command[0].lower() == ">>":
        if irc.user_info[user.lower()]["access_level"] >= 3:
            if len(command) >= 2:
                command = message.split(' ', 1)

                if command[1].lower().find('quit') != -1:
                    irc.send_private_message(channel,
                                             '5ERROR: You cannot quit bot using the console command. You must !quit.')
                    return
                elif command[1].lower().find('ns drop') != -1 or command[1].lower().find("msg nickserv drop") != -1:
                    irc.send_private_message(channel, '5ERROR: You cannot drop this nick.')
                    return

                # create file-like string to capture output
                code_out = StringIO()
                code_err = StringIO()

                # capture output and errors
                sys.stdout = code_out
                sys.stderr = code_err

                try:
                    exec(command[1])
                except Exception as err_str:
                    irc.send_private_message(channel, "ERROR: " + str(err_str))

                # restore stdout and stderr
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

                errors = code_err.getvalue()
                results = code_out.getvalue()

                code_out.close()
                code_err.close()

                if len(errors) > 0:
                    irc.send_private_message(channel, "ERROR (via stderr): " + str(errors))

                if len(results) > 0:
                    if results.find('\n') != -1:
                        results = results.split('\n')
                    else:
                        results = results.split(' ')
                    for result in results:
                        irc.send_private_message(channel, str(result))
