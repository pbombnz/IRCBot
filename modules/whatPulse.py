import urllib.request
import json
from modules import userDatabase


def get_what_pulse_url(param: str):
    return "http://api.whatpulse.org/user.php?user=" + str(param) + "&formatted=yes&format=json"


# noinspection PyUnusedLocal
def on_channel_pm(irc, user_mask, user, channel, message):
    command = message.split()

    if command[0].lower() == '!setwhatpulse' or command[0].lower() == '!setwp':
        if len(command) != 2:
            irc.send_private_message(channel, "USAGE: !setw[hat]p[ulse] (WhatPulse ID/WhatPulse Username)")
            return
        if command[1].isdigit():
            irc.send_private_message(channel, "USAGE: !setw[hat]p[ulse] (WhatPulse ID/WhatPulse Username)")
            return

        irc.send_private_message(channel, "3SUCCESS: Your WhatPulse ID has been changed.")
        irc.user_info[user.lower()]['whatpulse'] = str(command[1])
        userDatabase.save_user_database(irc)

    elif command[0].lower() == '!whatpulse' or command[0].lower() == '!wp':
        param = str()
        if len(command) == 1:
            param = str(irc.userData[user.lower()]['whatpulse'])
            if irc.userData[user.lower()]['whatpulse'] == "":
                irc.send_private_message(channel, "5ERROR: You have not set your WhatPulse ID yet.")
                irc.send_private_message(channel,
                                         "USAGE: !w[hat]p[ulse] (WhatPulse ID/WhatPulse Username/IRC Nickname)")
                irc.send_private_message(channel, "USAGE: !setw[hat]p[ulse] (WhatPulse ID)")
                return
        elif len(command) == 2:
            command = message.split(' ', 1)
            param = str(command[1])
            if command[1].lower() in irc.user_info:
                if irc.user_infoData[command[1].lower()]['whatpulse'] != "":
                    param = str(irc.userData[command[1].lower()]['whatpulse'])

        try:
            response = urllib.request.urlopen(get_what_pulse_url(param))
            html_source = response.read().decode('utf-8')
            response.close()
        except IOError:
            irc.send_private_message(channel, "5ERROR: The WhatPulse service is currently unavailable.")
            return

        try:
            whatpulse_info = json.loads(html_source)
        except ValueError:
            irc.send_private_message(channel, '5ERROR: An unknown WhatPulse Username/ID was given.')
            return

        if 'error' in whatpulse_info:
            irc.send_private_message(channel, '5ERROR: An unknown WhatPulse Username/ID was given.')
            return

        account_name = whatpulse_info['AccountName']  # Username
        user_id = whatpulse_info['UserID']  # ID
        country = whatpulse_info['Country']  # User's Country
        joined_date = whatpulse_info['DateJoined']  # Date Joined
        last_pulse_date = whatpulse_info['LastPulse']  # Last Pulsed
        pulses = whatpulse_info['Pulses']  # Pulses
        total_key_count = whatpulse_info['Keys']  # Total Key Count
        total_mouse_clicks = whatpulse_info['Clicks']  # Total Mouse Clicks
        avg_kpp = whatpulse_info['AvKeysPerPulse']  # Average Keys Per Pulse
        avg_cpp = whatpulse_info['AvClicksPerPulse']  # Average Clicks Per Pulse
        avg_kps = whatpulse_info['AvKPS']  # Average Keys Per Second
        avg_cps = whatpulse_info['AvCPS']  # Average Clicks Per Second
        # Ranks
        clicks_rank = whatpulse_info['Ranks']['Clicks']
        keys_rank = whatpulse_info['Ranks']['Keys']
        uptime_rank = whatpulse_info['Ranks']['Uptime']
        irc.send_private_message(channel,
                                 "\u000310WhatPulse:\u0003 {0}(ID:{1}) \u000310Country:\u0003 {2} "
                                 "\u000310Date Joined:\u0003 {3} \u000310LastPulsed:\u0003 {4} "
                                 "\u000310Pulses:\u0003 {5} \u000310Keys:\u0003 {6} \u000310Clicks:\u0003 {7} "
                                 "\u000310AvKeysPerPulse:\u0003 {8} \u000310AvClicksPerPulse:\u0003 {9} "
                                 "\u000310AvKeyPerSecond:\u0003 {10} \u000310AvClicksPerSecond:\u0003 {11} "
                                 "\u000310Rank: Clicks:\u0003 {12} \u000310Keys:\u0003 {13} "
                                 "\u000310Uptime:\u0003 {14}".format(
                                     str(account_name), str(user_id), str(country), str(joined_date),
                                     str(last_pulse_date),
                                     str(pulses), str(total_key_count), str(total_mouse_clicks), str(avg_kpp),
                                     str(avg_cpp),
                                     str(avg_kps), str(avg_cps), str(clicks_rank), str(keys_rank), str(uptime_rank)))
