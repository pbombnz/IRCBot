import urllib.request
from modules import userDatabase
import xml.etree.ElementTree as Et


def on_channel_pm(irc, user_mask, user, channel, message):
    command = message.split()

    if command[0].lower() == '!steam':
        steam_url = str()
        if len(command) == 1:
            if len(irc.user_info[user.lower()]['steam64']) > 0:
                steam_url = "http://steamcommunity.com/profiles/" + str(irc.user_info[user.lower()]['steam64']) + "/?xml=1"
            else:
                irc.send_private_message(channel, 'USAGE: !steam (Custom URL/Steam64ID)')
                irc.send_private_message(channel, 'USAGE: !setsteamid (Steam64ID)')
                return
        elif len(command) == 2:
            if command[1].lower() in irc.user_info:
                if len(irc.user_info[command[1].lower()]['steam64']) > 0:
                    steam_url = "http://steamcommunity.com/profiles/"+str(irc.user_info[command[1].lower()]['steam64'])+"/?xml=1"
                else:
                    irc.send_private_message(channel, str(irc.user_info[command[1].lower()]['ircNickName']) +
                                             " hasn't their steam64ID yet. Attempting to process anyways...")
                    steam_url = "http://steamcommunity.com/id/"+str(command[1])+"/?xml=1"
            else:
                if len(command[1]) == 17 and command[1].isdigit():
                    steam_url = "http://steamcommunity.com/profiles/"+str(command[1])+"/?xml=1"
                else:
                    steam_url = "http://steamcommunity.com/id/"+str(command[1])+"/?xml=1"

        print(1)
        try:
            response = urllib.request.urlopen(steam_url)
            html_source = response.read().decode('utf-8')
            response.close()
        except IOError:
            irc.send_private_message(channel, "5ERROR: The Steam API is currently unavailable.")
            return
        print(2)
        root = Et.fromstring(html_source)
        if root.tag == "response":
            if root[0].tag == "error":
                irc.send_private_message(channel, "5ERROR: " + str(root[0][0].text))
            return
        else:
            if root.tag == "profile":
                pass

            # steam_id64 = root.find('[steamID64]').text
            steam_id = root.find('steamID').text
            online_state = root.find('onlineState').text
            state_message = root.find('stateMessage').text
            vac_status = root.find('vacBanned').text
            if vac_status == "1":
                vac_status = "4Banned"
            else:
                vac_status = "3Not Banned"
            register_date = root.find('memberSince').text
            ranking = root.find('steamRating').text
            location = root.find('location').text
            # real_name = root.find('[realname]').text
            most_played_games = str()
            for most_played_game in root.find('mostPlayedGames').findall('mostPlayedGame'):
                game_name = most_played_game.find('gameName').text
                if len(most_played_games) == 0:
                    most_played_games += game_name
                else:
                    most_played_games += ", " + game_name

            irc.send_private_message(channel, "10SteamID:1 " + str(steam_id) +
                                     " 10Online State:1 " + str(online_state.capitalize()) +
                                     " 10General State:1 '" + str(state_message) +
                                     "' 10VAC Banned:1 " + str(vac_status) +
                                     " 10Steam Member Since:1 " + str(register_date) +
                                     " 10Steam Rating:1 " + str(ranking) +
                                     " 10Location:1 " + str(location) +
                                     " 10Most Played Games: 1"+str(most_played_games))

    if command[0].lower() == '!setsteamid':
        if len(command) != 2:
            irc.send_private_message(channel, 'USAGE: !setsteamid (Steam64ID)')
            irc.send_private_message(channel, 'USAGE: To find your Steam64ID, go to http://steamidconverter.com/')
            return

        if not command[1].isdigit():
            irc.send_private_message(channel, 'USAGE: !setsteamid (Steam64ID)')
            irc.send_private_message(channel, 'USAGE: To find your Steam64ID, go to http://steamidconverter.com/')
            return

        irc.send_private_message(channel, "3SUCESS: You have changed your SteamID(64-Bit).")
        irc.user_info[user.lower()]['steam64'] = str(command[1])
        userDatabase.save_user_database(irc)
