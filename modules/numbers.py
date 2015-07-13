import urllib.request


def on_channel_pm(irc, user_mask, user_nick, channel, message):
    command = message.split()
    
    if command[0] == "!numbers":
        if len(command) != 2:
            irc.send_private_message(channel, "USAGE: !numbers (Number)")
            return

        if not command[1].isdigit():
            irc.send_private_message(channel, "USAGE: !numbers (Number)")
            return

        try:
            numbers_response = urllib.request.urlopen("http://numbersapi.com/" + str(command[1]))
            numbers_math_response = urllib.request.urlopen("http://numbersapi.com/" + str(command[1]) + "/math")
            numbers_text = numbers_response.read().decode('utf-8')
            numbers_math_text = numbers_math_response.read().decode('utf-8')
            numbers_response.close()
            numbers_math_response.close()
            irc.send_private_message(channel, numbers_text)
            irc.send_private_message(channel, numbers_math_text)
        except IOError:
            irc.send_private_message(channel, "\u00035ERROR: Numbers command is currently not available")
            return
