from modules import userDatabase


def on_channel_pm(irc, user_mask, user, channel, message):
    command = message.split()
    
    if command[0].lower() == '!setlocation':  
        if len(command) >= 2:
            command = message.split(' ', 1)
            irc.send_private_message(channel, "3SUCESS: You have changed your location.")
            irc.user_info[user.lower()]['location'] = str(command[1])
            userDatabase.save_user_database(irc)
        else:
            irc.send_private_message(channel, "USAGE: !setlocation (Location)")
