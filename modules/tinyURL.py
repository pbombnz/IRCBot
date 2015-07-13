import urllib.request
import re

TINYURL = "http://tinyurl.com/api-create.php?url="


def tinyurl_shorten(url):

    if not re.match("^(https*)://.+", url, re.IGNORECASE):
        url = 'http://' + str(url)

    try:
        response = urllib.request.urlopen(TINYURL + str(url))
        html = response.read().decode('utf-8')
        return html
    except IOError:
        return str()


def on_channel_pm(irc, user_mask, user, channel, message):
    command = message.split()
    
    if command[0].lower() == '!tinyurl':  
        if len(command) != 2:
            irc.send_private_message(channel, 'USAGE: !tinyurl (Link)')
            return

        command = message.split(' ', 1)
        shortened_url = tinyurl_shorten(command[1])
        if len(shortened_url) > 0:
            irc.send_private_message(channel, user + ", " + tinyurl_shorten(command[1]))
        else:
            irc.send_private_message(channel, user + ", " + tinyurl_shorten(command[1]))
