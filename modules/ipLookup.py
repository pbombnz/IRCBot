import urllib.request
from urllib.parse import urlparse
import re
import json
import socket
import configparser
import os


IPLOOKUP_API_KEY = str()  # API key can go directly here. Code below is so my API key doesnt show on github


def on_init(irc):
    global IPLOOKUP_API_KEY

    config = configparser.ConfigParser()
    if os.path.exists("./resources/api-keys.ini"):
        config.read("./resources/api-keys.ini")
        if 'IPLookup' in config:
            IPLOOKUP_API_KEY = config['IPLookup']['APIkey']
            return

    irc.unload_module("modules.ipLookup")


def tinyurl_shorten(url):
    tinyurl_url = "http://tinyurl.com/api-create.php?url="

    if not re.match("^(https*)://.+", url, re.IGNORECASE):
        url = 'http://' + str(url)

    with urllib.request.urlopen(tinyurl_url + str(url)) as response:
        html = response.read().decode('utf-8')
        return html


def on_channel_pm(irc, user_mask, user, channel, message):
    command = message.split()

    if command[0].lower() == '!dns' or command[0].lower() == '!rdns':
        if len(command) == 2:
            if command[1] == "127.0.0.1" or command[1].lower() == "localhost" or command[1].startswith("192.168.") or command[1] == "::1":
                irc.send_private_message(channel, str(user) + ", " + str(command[1]) + " -> 127.0.0.1 -> ::1")
                return
            try:
                dns = socket.gethostbyaddr(str(command[1]))
            except IOError:
                irc.send_private_message(channel, '5ERROR: Could not be resolved.')
                return

            irc.send_private_message(channel, str(user) + ", " + str(command[1]) + " -> " + str(dns[2]).strip(
                '[]') + " -> " + str(dns[0]))
        else:
            irc.send_private_message(channel, 'USAGE: ![r]dns (IP/URL)')

    elif command[0].lower() == '!checkserver':
        if len(command) != 2:
            irc.send_private_message(channel, "USAGE: !checkserver (URL[:Port])")

        if command[1] == "127.0.0.1" or command[1].lower() == "localhost" or command[1].startswith("192.168.") or command[1] == "::1":
            return

        if command[1].startswith('http'):
            try:
                url = urllib.request.urlopen(command[1])
                url.close()
                is_online = "3Online"
            except IOError:
                is_online = "4Offline"
            irc.send_private_message(channel, "HTTP SERVER STATUS: " + command[1] + " is " + str(is_online))
        else:
            server_info = command[1].split(':')
            if len(server_info) != 2:
                server_info = [command[1], "80"]

            if int(server_info[1]) < 0 or int(server_info[1]) > 65535:
                irc.send_private_message(channel, '5ERROR: Port Number must be between 0 - 65535.')
                return

            is_online = str()
            try:
                sock = socket.socket()
                sock.connect((str(server_info[0]), int(server_info[1])))
                sock.close()
                is_online = "3Online"
            except TimeoutError:
                is_online = "7Online, but the server actively rejected access on the specified port"
            except IOError:
                is_online = "4Offline"
            finally:
                irc.send_private_message(channel, "SERVER STATUS: " + server_info[0] + ":" + server_info[
                    1] + " is " + is_online)

    elif command[0].lower() == '!lookup' or command[0].lower() == '!lu':
        if len(command) != 2:
            irc.send_private_message(channel, 'USAGE: !l[ook]u[p](IP/URL)')
            return

        if command[1] == "127.0.0.1" or command[1].lower() == "localhost" or command[1].startswith("192.168.") or command[1] == "::1":
            return

        if re.match("^(https*)://.+", command[1], re.IGNORECASE):
            command[1] = urlparse(command[1]).netloc

        if command[1].lower().startswith('www.'):
            command[1] = command[1][4:]

        ip_lookup_url = "http://api.ipinfodb.com/v3/ip-city/?key=" + IPLOOKUP_API_KEY + "&ip=" + command[1] + \
                        "&format=json"
        response = urllib.request.urlopen(ip_lookup_url)
        json_data = json.loads(response.read().decode('utf-8'))

        if json_data["statusCode"] != "OK":
            irc.send_private_message(channel, '5ERROR: This command is not available currently, try again later.')
            return
        try:
            rdns = socket.gethostbyaddr(str(json_data["ipAddress"]))
        except IOError:
            rdns = [""]
        print(json_data)
        ip = str(json_data["ipAddress"])
        country = str(json_data["countryName"]).title()
        region = str(json_data["regionName"]).title()
        city = str(json_data["cityName"]).title()
        zip_code = str(json_data["zipCode"])
        latitude = str(json_data["latitude"])
        longitude = str(json_data["longitude"])
        time_zone = str(json_data["timeZone"])

        if longitude == "" and latitude == "":
            shortened_url = ""
        else:
            shortened_url = tinyurl_shorten("http://maps.google.com/maps?q=" + str(latitude) + "," + str(longitude))

        irc.send_private_message(channel, '6IP:1 ' + str(ip) + ' 6Domain:1 ' + str(rdns[0]) +
                                 ' 6City:1 ' + str(city) + ' 6Country:1 ' + str(country) +
                                 ' 6Region:1 ' + str(region) + ' 6Zip Code:1 ' + str(zip_code) +
                                 ' 6Time Zone:1 ' + str(time_zone) +
                                 ' 6Location(Google Maps):1 ' + str(shortened_url))
