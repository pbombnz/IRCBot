import urllib.request
import re
import html

EVENTS_CALLED = "CHANNEL-PM"

NO_URL_TITLE_EXTENSIONS = [
    '.ai', '.bmp', '.drw', '.gif',
    '.jpeg', '.jpg', '.jif', '.jfif',
    '.jp2', '.jpx', '.j2k', '.j2c',
    '.pcd', '.psd', '.pbm', '.png',
    '.tiff', '.tif', '.svg', '.raw', '.yuv'
]

URL_REGEX = re.compile("^(?:https*)://.*")


def on_channel_pm(irc, user_mask, user_nick, channel, message):
    if len(message.split()) > 1:
        message = message.split()[0]

    if URL_REGEX.match(message):
        # Checking If URL is an image link
        for extension in NO_URL_TITLE_EXTENSIONS:
            if message.lower().endswith(extension):
                return

        # Collecting HTML Source
        try:
            response = urllib.request.urlopen(message)
            html_source = response.read().decode('utf-8').replace('\r', '').replace('\n', '').replace('\t', '')
            response.close()
        except IOError:
            return

        # Collecting Title Tag from HTML Source and decoding it
        title = html_source.partition('<title>')[2].partition('</title>')[0]
        title = html.unescape(str(title))

        # Sending title to irc channel
        if title != "":
            irc.send_private_message(channel, 'URL Title: ' + str(title))
