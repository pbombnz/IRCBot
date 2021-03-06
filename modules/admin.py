import sys
from modules import userDatabase
from io import StringIO

MAX_SPAM = 50


def on_channel_pm(bot, user_mask, user, channel, message):
    command = message.split()

    if command[0].lower() == '!join':
        if bot.user_info[user.lower()]["access_level"] >= 1:
            if len(command) == 2:
                bot.join(command[1])
            elif len(command) == 3:
                bot.join(command[1], command[2])
            else:
                bot.send_private_message(channel, "USAGE: !join (Channel) [(Key)]")

    elif command[0].lower() == "!part":
        if bot.user_info[user.lower()]["access_level"] >= 2:
            if len(command) == 2:
                command = message.split(' ', 1)
                bot.part(command[1])
            elif len(command) > 2:
                command = message.split(' ', 2)
                bot.part(command[1], command[2])
            else:
                bot.send_private_message(channel, "USAGE: !part (Channel) [(Message)]")

    elif command[0].lower() == "!cycle":
        if bot.user_info[user.lower()]["access_level"] >= 1:
            if len(command) == 2:
                command = message.split(' ', 1)
                bot.cycle(command[1])
            elif len(command) > 2:
                command = message.split(' ', 2)
                bot.cycle(command[1], command[2])
            else:
                bot.send_private_message(channel, "USAGE: !cycle (Channel) [(Key)]")

    elif command[0].lower() == "!identify":
        if bot.user_info[user.lower()]["access_level"] >= 3:
            if len(command) == 1:
                bot.identify()
            elif len(command) == 2:
                bot.identify(command[1])
            else:
                bot.send_private_message(channel, "USAGE: !identify [(Password)]")

    elif command[0].lower() == "!say":
        if bot.user_info[user.lower()]["access_level"] >= 2:
            if len(command) >= 3:
                command = message.split(' ', 2)
                if len(command[1]) > 0 and len(command[2]) > 0:
                    bot.send_private_message(command[1], command[2])
                else:
                    bot.send_private_message(channel, "USAGE: !say (Channel) (Message)")
            else:
                bot.send_private_message(channel, "USAGE: !say (Channel) (Message)")

    elif command[0].lower() == "!action":
        if bot.user_info[user.lower()]["access_level"] >= 2:
            if len(command) >= 3:
                command = message.split(' ', 2)
                if len(command[1]) > 0 and len(command[2]) > 0:
                    bot.send_private_message(command[1], '\001ACTION ' + str(command[2]) + '\001')
                else:
                    bot.send_private_message(channel, "USAGE: !action (Channel) (Action Message)")
            else:
                bot.send_private_message(channel, "USAGE: !action (Channel) (Action Message)")

    elif command[0].lower() == "!spam":
        if bot.user_info[user.lower()]["access_level"] >= 3:
            command = message.split(' ', 3)
            if len(command) == 4:
                if len(command[1]) > 1 and len(command[2]) > 0 and len(command[3]) > 0:
                    if command[2].isdigit():
                        if int(command[2]) in range(0, MAX_SPAM + 1):
                            for i in range(int(command[2])):
                                bot.send_private_message(command[1], command[3])
                            return
            bot.send_private_message(channel, "USAGE: !spam (Channel/Recipient) (Repetition Number) (Message)")

    elif command[0].lower() == "!raw":
        if bot.user_info[user.lower()]["access_level"] >= 3:
            if len(command) >= 2:
                command = message.split(' ', 1)
                if len(command[1]) > 0:
                    if command[1].lower().startswith('quit'):
                        bot.send_private_message(channel,
                                                 "ERROR: You cannot disconnect the bot with the RAW command. Please use !quit.")
                    elif command[1].lower().startswith('ns drop') or command[1].lower().startswith(
                            'msg nickserv drop'):
                        bot.send_private_message(channel, "ERROR: You cannot drop this nick via RAW command.")
                    else:
                        bot.sendRawMessage(command[1])
                    return
            bot.send_private_message(channel, 'USAGE: !raw (Server Message)')

    elif command[0].lower() == "!nick":
        if bot.user_info[user.lower()]["access_level"] >= 2:
            if len(command) == 2:
                command = message.split(' ', 1)
                if len(command[1]) > 0:
                    bot.changeNickname(command[1])
                    return
            bot.send_private_message(channel, "USAGE: !nick (Nickname)")

    elif command[0].lower() == "!quit":
        if bot.user_info[user.lower()]["access_level"] >= 3:
            if len(command) == 2 and len(command[1]) > 0:
                command = message.split(' ', 1)
                bot.quit(command[1])
            else:
                bot.quit()

    elif command[0].lower() == "!setbotlevel" or command[0].lower() == "!sbl":
        if bot.user_info[user.lower()]["access_level"] >= 3:
            if len(command) != 3:
                bot.send_private_message(channel, 'USAGE: !s[et]b[ot]l[evel] (Nickname) (Bot Level[0-3])')
                return

            command = message.split(' ', 2)
            if not command[2].isdigit():
                bot.send_private_message(channel, 'USAGE: !s[et]b[ot]l[evel] (Nickname) (Bot Level[0-3]')
                return

            if command[1].lower() == user.lower() and bot.user_info[user.lower()]["access_level"] < 3:
                bot.send_private_message(channel, '5ERROR: You cannot set your own bot level.')
                return

            if int(command[2]) < 0 or int(command[2]) > 3:
                bot.send_private_message(channel, '5ERROR: Access level must be between 0-3.')
                return

            if command[1].lower() in bot.user_info:
                old_access_level = bot.user_info[command[1].lower()]["access_level"]
                if old_access_level != int(command[2]):
                    bot.user_info[command[1].lower()]["access_level"] = int(command[2])
                    userDatabase.save_user_database(bot)
                    bot.send_private_message(channel,
                                             '\u00033SUCESS: Bot Level has changed for {0} from {1} to {2}.'.format(
                                                 str(bot.user_info[command[1].lower()]['ircNickName']),
                                                 str(old_access_level), str(command[2])))
                else:
                    bot.send_private_message(channel, '\u00035ERROR: {0} is already set at that level.'.format(
                        str(bot.user_info[command[1].lower()]['ircNickName'])))
            else:
                bot.send_private_message(channel, "5ERROR: '" + str(command[1]) + "' does not exist.")

    elif command[0].lower() == "!botadmins":
        if bot.user_info[user.lower()]["access_level"] >= 1:
            client_admin_list = dict()
            for nick in bot.user_info:
                if bot.user_info[nick]["access_level"] > 0:
                    client_admin_list[bot.user_info[nick]['nick_name']] = bot.user_info[nick][
                        "access_level"]

            for users_ranks in sorted(client_admin_list.items(), key=lambda x: x[1], reverse=True):
                nick, level = users_ranks
                if level == 1:
                    bot.send_private_message(channel, str(nick) + ', Trusted User')
                elif level == 2:
                    bot.send_private_message(channel, str(nick) + ', Bot Admin')
                elif level == 3:
                    bot.send_private_message(channel, str(nick) + ', Bot Owner')

    elif command[0].lower() == "!loadmodule":
        if bot.user_info[user.lower()]["access_level"] >= 3:
            bot.send_private_message(channel, "USAGE: To load a new module, add an import statement into the "
                                              "modules's __init__.py file, then type !reloadmodules. "
                                              "This will refresh all modules and import new modules.")

    elif command[0].lower() == "!reloadmodule":
        if bot.user_info[user.lower()]["access_level"] >= 3:
            if len(command) != 2:
                bot.send_private_message(channel, "USAGE: !reloadmodule (Module Name)")
                return

            is_reloaded = bot.reload_module(command[1])
            if is_reloaded:
                bot.send_private_message(channel, "3SUCCESS: Module loaded.")
            else:
                bot.send_private_message(channel, "5ERROR: Module is already loaded or does not exist.")

    elif command[0].lower() == "!unloadmodule":
        if bot.user_info[user.lower()]["access_level"] >= 3:
            if len(command) != 2:
                bot.send_private_message(channel, "USAGE: !unloadmodule (Module Name)")
                return

            is_unloaded = bot.unload_module(command[1])
            if is_unloaded:
                bot.send_private_message(channel, "3SUCCESS: Module unloaded.")
            else:
                bot.send_private_message(channel, "5ERROR: Module is already unloaded or does not exist.")

    elif command[0].lower() == "!reloadallmodules":
        if bot.user_info[user.lower()]["access_level"] >= 3:
            if len(command) == 1:
                is_reloaded = bot.reload_all_modules()
                if is_reloaded:
                    bot.send_private_message(channel, "3SUCCESS: All modules reloaded/reimported.")
                else:
                    bot.send_private_message(channel,
                                             "5ERROR: Could not reload all modules. Possibly a compiler error occured with recently modified code.")

    elif command[0].lower() == ">>":
        if bot.user_info[user.lower()]["access_level"] >= 3:
            if len(command) >= 2:
                command = message.split(' ', 1)

                if command[1].lower().find('quit') != -1:
                    bot.send_private_message(channel,
                                             '5ERROR: You cannot quit bot using the console command. You must !quit.')
                    return
                elif command[1].lower().find('ns drop') != -1 or command[1].lower().find("msg nickserv drop") != -1:
                    bot.send_private_message(channel, '5ERROR: You cannot drop this nick.')
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
                    bot.send_private_message(channel, "ERROR: " + str(err_str))

                # restore stdout and stderr
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

                errors = code_err.getvalue()
                results = code_out.getvalue()

                code_out.close()
                code_err.close()

                if len(errors) > 0:
                    bot.send_private_message(channel, "ERROR (via stderr): " + str(errors))

                if len(results) > 0:
                    if results.find('\n') != -1:
                        results = results.split('\n')
                    else:
                        results = results.split(' ')
                    for result in results:
                        bot.send_private_message(channel, str(result))
