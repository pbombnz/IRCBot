# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json
import re

WEATHER_UNDERGROUND_API_KEY = "ecf579a205be1ff9"

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


def found_weather_info_errors(irc, channel, weather_info:dict):
    if "response" in weather_info:
        if "error" in weather_info["response"]:
            if weather_info["response"]["error"]["type"] == "notfound":
                irc.send_private_message(channel, '5ERROR: No City/State/Country match your search.')
            elif weather_info["response"]["error"]["type"] == "querynotfound":
                irc.send_private_message(channel, '5ERROR: No City/State/Country match your search.')
            else:
                try:
                    irc.send_private_message(channel, '5ERROR: ' + str(weather_info["response"]["error"]["type"]))
                except:
                    irc.send_private_message(channel, '5ERROR: Unknown Error occured.')
            return True

        # When results sub-dict appears in in responce, it means serveral locations were found. Return error message to user.
        if "results" in weather_info["response"]:
            irc.send_private_message(channel,
                                     '5ERROR: Serveral cities/states/countries match your search. Please Be more specific.')
            return True
    return False


def get_location(irc, user, channel, message):
    command = message.split()

    if len(command) == 1:
        if user.lower() in irc.user_info:
            if len(irc.user_info[user.lower()]['location']) > 0:
                return irc.user_info[user.lower()]['location']
            irc.send_private_message(channel, "5ERROR: You need to set your location before you use"
                                              " this command without an argument.")
            irc.send_private_message(channel, "USAGE: !setlocation (Location)")
        return str()
    elif len(command) >= 2:
        command = message.split(' ', 1)

        if command[1].lower() in irc.user_info:
            if len(irc.user_info[command[1].lower()]['location']) > 0:
                return irc.user_info[command[1].lower()]['location']
            else:
                irc.send_private_message(channel, "5ERROR: " + str(irc.user_info[command[1].lower()]['nick_name']) +
                                         " hasn't set their location yet.")
                return str()
        else:
            return command[1]


def on_channel_pm(irc, user_mask, user, channel, message):
    command = message.split()

    if command[0].lower() == "!weather" or command[0].lower() == "!conditions":
        location = get_location(irc, user, channel, message)
        if len(location) == 0:
            irc.send_private_message(channel,
                                     'USAGE: !conditions (Location or IRC Nickname) OR !weather (Location or IRC Nickname)')
            return

        location = urllib.parse.quote_plus(location)
        weather_url = "http://api.wunderground.com/api/" + str(WEATHER_UNDERGROUND_API_KEY) + "/conditions/q/" + str(
            location) + ".json"

        try:
            response = urllib.request.urlopen(weather_url)
            html_source = response.read().decode('utf-8')
            response.close()
        except IOError:
            irc.send_private_message(channel, '5ERROR: Could not connect to weather services. Please Try again later.')
            return

        weather_info = json.loads(html_source)
        found_errors = found_weather_info_errors(irc, channel, weather_info)
        if found_errors:
            return

        location = weather_info["current_observation"]["display_location"]["full"]
        observation_time = weather_info["current_observation"]["observation_time"]
        weather = weather_info["current_observation"]["weather"]
        temp = weather_info["current_observation"]["temperature_string"]
        humid = weather_info["current_observation"]["relative_humidity"]
        wind = weather_info["current_observation"]["wind_string"] + " (" + str(
            weather_info["current_observation"]["wind_kph"]) + " KMH)"
        irc.send_private_message(channel, "10Location: " + location + " 10Weather: " + weather +
                                 " 10Temp: " + temp + " 10Humidity: " + humid +
                                 " 10Wind: " + wind + " 10Observation Date: " + observation_time)

    elif command[0].lower() == "!forecast10day":
        location = get_location(irc, user, channel, message)
        if len(location) == 0:
            irc.send_private_message(channel, 'USAGE: !forecast10day (Location or IRC Nickname)')
            return

        location = urllib.parse.quote_plus(location)
        weather_url = "http://api.wunderground.com/api/" + str(WEATHER_UNDERGROUND_API_KEY) + "/forecast10day/q/" + str(
            location) + ".json"

        try:
            response = urllib.request.urlopen(weather_url)
            html_source = response.read().decode('utf-8')
            response.close()
        except IOError:
            irc.send_private_message(channel, '5ERROR: Could not connect to weather services. Please Try again later.')
            return

        weather_info = json.loads(html_source)
        found_errors = found_weather_info_errors(irc, channel, weather_info)
        if found_errors:
            return

        irc.send_private_message(user, '10 == 10-Day Forcast For ' + location.title() + ' ==')
        for i in range(len(weather_info["forecast"]["txt_forecast"]["forecastday"])):
            irc.send_private_message(user, '10' + str(
                weather_info["forecast"]["txt_forecast"]["forecastday"][i]["title"]) + ' 10Forecast: ' + str(
                weather_info["forecast"]["txt_forecast"]["forecastday"][i]["fcttext_metric"]))

    elif command[0].lower() == "!alerts":
        location = get_location(irc, user, channel, message)
        if len(location) == 0:
            irc.send_private_message(channel, 'USAGE: !alerts (Location or IRC Nickname)')
            return

        location = urllib.parse.quote_plus(location)
        weather_url = "http://api.wunderground.com/api/" + str(WEATHER_UNDERGROUND_API_KEY) + "/alerts/q/" + str(
            location) + ".json"

        try:
            response = urllib.request.urlopen(weather_url)
            html_source = response.read().decode('utf-8')
            response.close()
        except IOError:
            irc.send_private_message(channel, '5ERROR: Could not connect to weather services. Please Try again later.')
            return

        weather_info = json.loads(html_source)
        found_errors = found_weather_info_errors(irc, channel, weather_info)
        if found_errors:
            return

        if len(weather_info["alerts"]) == 0:
            irc.send_private_message(channel,
                                     user + ", " + location.title() + " doesn't have any alerts at this moment.")
        else:
            irc.send_private_message(channel, '10 == Alerts in ' + location.title() + ' (Total: ' + str(
                len(weather_info["alerts"])) + ') == ')
            for i in range(len(weather_info["alerts"])):
                irc.send_private_message(channel, '10Alarm Caused By: ' + str(
                    weather_info["alerts"][i]["wtype_meteoalarm_name"]) + ' 10Servertity: ' + str(
                    weather_info["alerts"][i]["wtype_meteoalarm"]) + '/10 10Description: ' + str(
                    weather_info["alerts"][i]["description"]))

    elif command[0].lower() == "!satellite":
        location = get_location(irc, user, channel, message)
        if len(location) == 0:
            irc.send_private_message(channel, 'USAGE: !satellite (Location or IRC Nickname)')
            return

        location = urllib.parse.quote_plus(location)
        weather_url = "http://api.wunderground.com/api/" + str(WEATHER_UNDERGROUND_API_KEY) + "/satellie/q/" + str(
            location) + ".json"

        try:
            response = urllib.request.urlopen(weather_url)
            html_source = response.read().decode('utf-8')
            response.close()
        except IOError:
            irc.send_private_message(channel, '5ERROR: Could not connect to weather services. Please Try again later.')
            return

        weather_info = json.loads(html_source)
        found_errors = found_weather_info_errors(irc, channel, weather_info)
        if found_errors:
            return

        weather_info = json.loads(html_source)
        found_weather_info_errors(irc, channel, weather_info)

        satURL = tinyurl_shorten(str(weather_info["satellite"]["image_url_vis"]))
        irc.send_private_message(channel, '10Location: ' + location + ' 10Statellite Image: ' + str(satURL))

    elif command[0].lower() == "!astronomy":
        location = get_location(irc, user, channel, message)
        if len(location) == 0:
            irc.send_private_message(channel, 'USAGE: !astronomy (Location or IRC Nickname)')
            return

        location = urllib.parse.quote_plus(location)
        weather_url = "http://api.wunderground.com/api/" + str(WEATHER_UNDERGROUND_API_KEY) + "/astronomy/q/" + str(
            location) + ".json"

        try:
            response = urllib.request.urlopen(weather_url)
            html_source = response.read().decode('utf-8')
            response.close()
        except IOError:
            irc.send_private_message(channel, '5ERROR: Could not connect to weather services. Please Try again later.')
            return

        weather_info = json.loads(html_source)
        found_errors = found_weather_info_errors(irc, channel, weather_info)
        if found_errors:
            return

        moon_percentage_Illuimated = weather_info["moon_phase"]["percentIlluminated"]
        sunrise = weather_info["moon_phase"]["sunrise"]["hour"] + ":" + weather_info["moon_phase"]["sunrise"][
            "minute"]
        sunset = weather_info["moon_phase"]["sunset"]["hour"] + ":" + weather_info["moon_phase"]["sunset"]["minute"]
        irc.send_private_message(channel,
                                 '10Location: ' + location + ' 10Moon Illuimated(%): ' + moon_percentage_Illuimated + ' 10Sunrise Time: ' + str(
                                     sunrise) + ' 10Sunset Time: ' + str(sunset))

    elif command[0].lower() == "!forecast":
        location = get_location(irc, user, channel, message)
        if len(location) == 0:
            irc.send_private_message(channel, 'USAGE: !forecast (Location or IRC Nickname)')
            return

        location = urllib.parse.quote_plus(location)
        weather_url = "http://api.wunderground.com/api/" + str(WEATHER_UNDERGROUND_API_KEY) + "/forecast/q/" + str(
            location) + ".json"

        try:
            response = urllib.request.urlopen(weather_url)
            html_source = response.read().decode('utf-8')
            response.close()
        except IOError:
            irc.send_private_message(channel, '5ERROR: Could not connect to weather services. Please Try again later.')
            return

        weather_info = json.loads(html_source)
        found_errors = found_weather_info_errors(irc, channel, weather_info)
        if found_errors:
            return

        irc.send_private_message(user, '10 == 3-Day Forcast For ' + location.title() + ' ==')
        for i in range(len(weather_info["forecast"]["txt_forecast"]["forecastday"])):
            irc.send_private_message(user, '10' + str(
                weather_info["forecast"]["txt_forecast"]["forecastday"][i]["title"]) + ' 10Forecast: ' + str(
                weather_info["forecast"]["txt_forecast"]["forecastday"][i]["fcttext_metric"]))
