def on_channel_pm(irc, user_mask, user_nick, channel, message):
    command = message.split()
    channel_admin_info = irc.get_channel_info()

    if command[0].lower() == "!poop":
        if len(command) != 2:
            irc.send_private_message(channel, "USAGE: !poop (Nickname)")
            return

        command = message.split(' ', 1)
        for op in channel_admin_info[channel]:
            for nick in channel_admin_info[channel][op]:
                if command[1].lower() == nick.lower():
                    irc.send_private_message(channel, "\x01ACTION poops on " + str(nick) + '!\x01')
                    return
        irc.send_private_message(channel, "5ERROR: " + str(command[1]) + ' is not on this channel.')

    elif command[0].lower() == "!slap":
        if len(command) == 2:
            command = message.split(' ', 1)

            for op in channel_admin_info[channel]:
                for nick in channel_admin_info[channel][op]:
                    if command[1].lower() == nick.lower():
                        irc.send_private_message(channel, "\x01ACTION slaps " + str(nick) + " around a bit "
                                                                                            "with a large trout\x01")
                        return
            irc.send_private_message(channel, "5ERROR: " + str(command[1]) + ' is not on this channel.')
        else:
            irc.send_private_message(channel, "USAGE: !slap (Nickname)")
