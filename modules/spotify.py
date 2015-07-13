import urllib.request
import urllib.parse
import json

SPOTIFY_SEARCH_API_URL = "http://ws.spotify.com/search/1/%SEARCH_TYPE%.json?q=%QUERY%"
SPOTIFY_LOOKUP_API_URL = "http://ws.spotify.com/lookup/1/.json?uri=%QUERY%"


def on_channel_pm(irc, user_mask, user, channel, message):
    command = message.split()

    if message.find('spotify:') != -1:
        for command_arg in command:
            if command_arg.find('spotify:') != -1:
                try:
                    response = urllib.request.urlopen(SPOTIFY_LOOKUP_API_URL.replace("%QUERY%", command_arg))
                    html = response.read().decode('utf-8')
                    response.close()
                except IOError:
                    return

                spotify_info = json.loads(html)

                if spotify_info["info"]["type"] == "artist":
                    irc.send_private_message(channel, "\u00039[\u00033Spotify\u00039][\u00033Artist\u00039] " + str(
                        spotify_info["artist"]["name"]))
                elif spotify_info["info"]["type"] == "album":
                    irc.send_private_message(channel,
                                             "\u00039[\u00033Spotify\u00039][\u00033Album\u00039]\u0003 \'{0}\" by {1} released in {2}".format(
                                                 str(spotify_info["album"]["name"]),
                                                 str(spotify_info["album"]["artist"]),
                                                 str(spotify_info["album"]["released"])))
                elif spotify_info["info"]["type"] == "track":
                    irc.send_private_message(channel, "9[3Spotify9][3Track9] '" + str(
                        spotify_info["track"]["name"].encode('utf-8', 'ignore')) + '" by ' + str(
                        spotify_info["track"]["artists"][0]["name"]) + ' on "' + str(
                        spotify_info["track"]["album"]["name"]) + '" released in ' + str(
                        spotify_info["track"]["album"]["released"]))
                return

    if command[0].lower() == '!spotify':
        # !spotify (album/artist/track) (UTF-8 query)
        if len(command) < 3:
            irc.send_private_message(channel, "USAGE: !spotify (Album/Artist/Track) (Search Query)")
            return

        command = message.split(' ', 2)

        spotify_url = str() + SPOTIFY_SEARCH_API_URL
        spotify_url = spotify_url.replace("%QUERY%", urllib.parse.quote_plus(command[2]))
        if command[1].lower() == "album":
            search_type = "album"
        elif command[1].lower() == "artist":
            search_type = "artist"
        elif command[1].lower() == "track":
            search_type = "track"
        else:
            irc.send_private_message(channel, "USAGE: !spotify (Album/Artist/Track) (Search Query)")
            return

        spotify_url = spotify_url.replace("%SEARCH_TYPE%", search_type)

        try:
            response = urllib.request.urlopen(spotify_url)
            html_source = response.read().decode('utf-8')
            response.close()
        except IOError:
            irc.send_private_message(channel, "5ERROR: Spotify search API currently unavailable.")
            return

        spotify_info = json.loads(html_source)
        import pprint
        pprint.pprint(spotify_info)

        search_type_with_s = search_type + "s"
        if len(spotify_info[search_type_with_s]) < 1:
            irc.send_private_message(channel, "5ERROR: No results were retrieved.")
            return

        results_limit = len(spotify_info[search_type_with_s])
        if len(spotify_info[search_type_with_s]) > 3:
            results_limit = 3

        if search_type == "album":
            irc.send_private_message(channel, "3Spotify Album Search - '" + str(command[2]) + "'")
            for num in range(0, results_limit):
                irc.send_private_message(channel, "3Result " + str(num + 1) + ": '"
                                         + str(spotify_info["albums"][num]["name"]) + "' By " + str(
                                         spotify_info["albums"][num]["artists"][0]["name"]) +
                                         ' 3Album URL: http://open.spotify.com/album/'
                                         + str(spotify_info["albums"][num]["href"].split(':')[2]))
                # spotify["albums"][0]["name"] #Album Name
                # spotify["albums"][0]["href"] #Album Spotify URI
                # spotify["albums"][0]["artists"][0]["name"] #Artist Name
                # spotify["albums"][0]["artists"][0]["href"] #Artist Spotify URI
        elif search_type == "artist":
            irc.send_private_message(channel, "3Spotify Artist Search - '" + str(command[2]) + "'")
            for num in range(0, results_limit):
                irc.send_private_message(channel, "3Result " + str(num + 1) + ": '" + str(
                    spotify_info["artists"][num][
                        "name"]) + '" 3Artist URL: http://open.spotify.com/artist/' + str(
                    spotify_info["artists"][num]["href"].split(':')[2]))
        elif search_type == "track":
            irc.send_private_message(channel, "3Spotify Track Search - '" + str(command[2]) + "'")
            for num in range(0, results_limit):
                irc.send_private_message(channel, "3Result " + str(num + 1) + ": '" + str(
                    spotify_info["tracks"][num]["name"]) + '" by ' + str(
                    spotify_info["tracks"][num]["artists"][0]["name"]) + ' on "' + str(
                    spotify_info["tracks"][num]["album"][
                        "name"]) + '" 3Track URL http://open.spotify.com/track/' + str(
                    spotify_info["tracks"][num]["href"].split(':')[2]))
