import time
import re


class CaseInsensitiveDict(dict):
    def __contains__(self, key):
        return dict.__contains__(self, key.lower())

    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())

    def __setitem__(self, key, value):
        return dict.__setitem__(self, key.lower(), value)


poll_data = CaseInsensitiveDict()


def on_constant_call(irc):
    if len(poll_data) < 1:
        return

    poll_data_to_delete = list()

    for channel in poll_data:
        if not poll_data[channel]['nearExpire']:
            if (poll_data[channel]['expireTime'] - time.time()) <= 60.0:
                poll_data[channel]['nearExpire'] = True
                irc.send_private_message(channel, "The poll for this channel is about to expire in a minute. "
                                                  "Please check the !poll and !vote if you haven't yet.")

        if time.time() > poll_data[channel]['expireTime']:
            irc.send_private_message(channel, 'The poll for this channel has expired. The Final results are...')
            irc.send_private_message(channel,
                                     'Expired Poll for {0}: \"{1}\" By {2} on {3}, Votes: Yes: {4} No: {5}'.format(
                                         str(poll_data[channel]['channel']),
                                         str(poll_data[channel]['poll']),
                                         str(poll_data[channel]['creator']),
                                         str(time.ctime(poll_data[channel]['createdTime'])),
                                         str(poll_data[channel]['vote']['yes']),
                                         str(poll_data[channel]['vote']['no'])))
            poll_data_to_delete.append(channel)

    for channel in poll_data_to_delete:
        del poll_data[channel]


def on_channel_pm(irc, user_mask, user, channel, message):
    command = message.split()

    if command[0].lower() == '!vote':
        if channel not in poll_data:
            irc.send_private_message(channel, '5ERROR: There is currently no poll on this channel.')
            return

        if user_mask[0].lower() in poll_data[channel.lower()]['voted']['nickName']:
            irc.send_notice_message(user, '5ERROR: You have already voted.')
            return

        if user_mask[1].lower() == 'mibbit':
            irc.send_private_message(channel, '5ERROR: Sorry, Mibbit users are not allowed to vote.')
            return

        if user_mask[2].lower() in poll_data[channel.lower()]['voted']['hostName']:
            irc.send_private_message(channel, '5ERROR: Someone with the same hostname has already voted.')
            return

        if len(command) != 2:
            irc.send_private_message(channel, 'USAGE: !vote (y[es]/n[o])')
            return

        command = message.split(' ', 1)
        if command[1].lower() == 'y' or command[1].lower() == 'yes':
            poll_data[channel.lower()]['vote']['yes'] += 1
        elif command[1].lower() == 'n' or command[1].lower() == 'no':
            poll_data[channel.lower()]['vote']['no'] += 1
        else:
            irc.send_private_message(channel, 'USAGE: !vote (y[es]/n[o])')
            return

        irc.send_notice_message(user, 'Thanks for Voting.')
        poll_data[channel.lower()]['voted']['nickName'].append(user_mask[0].lower())
        poll_data[channel.lower()]['voted']['hostName'].append(user_mask[2].lower())
        irc.send_private_message(channel, 'Current Poll for {0}: \"{1}\" By {2} on {3}, !vote yes or !vote no'.format(
            str(channel),
            str(poll_data[channel.lower()]['poll']),
            str(poll_data[channel.lower()]['creator']),
            str(time.ctime(poll_data[channel.lower()]['createdTime']))))

    elif command[0].lower() == '!setpoll':
        channel_info = irc.get_channel_info()

        if user in channel_info[channel]['Operator'] or user in channel_info[channel]['Admin'] or user in \
                channel_info[channel]['Owner']:
            if len(command) >= 3:
                match = re.match("!setpoll\s(.*\?)\s(2m|5m|10m|30m|1h|2h|5h|10h|1d)", message, re.IGNORECASE)
                if match:
                    command_params = \
                        re.findall("!setpoll\s(.*\?)\s(2m|5m|10m|30m|1h|2h|5h|10h|1d)", message, re.IGNORECASE)[0]

                    question = command_params[0]
                    expiry_time = command_params[1]
                    current_time = time.time()

                    if expiry_time.lower() == '2m':
                        expiry_time = current_time + 120.0
                    elif expiry_time.lower() == '5m':
                        expiry_time = current_time + (60.0 * 5)
                    elif expiry_time.lower() == '10m':
                        expiry_time = current_time + (60.0 * 10)
                    elif expiry_time.lower() == '30m':
                        expiry_time = current_time + (60.0 * 30)
                    elif expiry_time.lower() == '1h':
                        expiry_time = current_time + (60.0 * 60)
                    elif expiry_time.lower() == '2h':
                        expiry_time = current_time + (60.0 * 120)
                    elif expiry_time.lower() == '5h':
                        expiry_time = current_time + ((60.0 * 60) * 5)
                    elif expiry_time.lower() == '10h':
                        expiry_time = current_time + ((60.0 * 60) * 10)
                    elif expiry_time.lower() == '1d':
                        expiry_time = current_time + ((60.0 * 60) * 24)
                else:
                    irc.send_private_message(channel, 'USAGE: !setpoll (Poll Question)? '
                                                      '(Poll Expires In [2m/5m/10m/30m/1h/2h/5h/10h/1d])')
                    return
            else:
                irc.send_private_message(channel, 'USAGE: !setpoll (Poll Question)? '
                                                  '(Poll Expires In [2m/5m/10m/30m/1h/2h/5h/10h/1d])')
                return

            if channel in poll_data:
                if poll_data[channel]['poll'] != "":
                    irc.send_private_message(channel, '5ERROR: Their is currently a poll going on in this channel.'
                                                      ' If you truly wish to force finish the current poll,'
                                                      ' type !abortpoll')
                    return

            poll_data[channel] = dict()
            poll_data[channel]['poll'] = question
            poll_data[channel]['createdTime'] = current_time
            poll_data[channel]['expireTime'] = expiry_time
            poll_data[channel]['nearExpire'] = False
            poll_data[channel]['creator'] = user
            poll_data[channel]['channel'] = channel
            poll_data[channel]['voted'] = {'nickName': list(), 'hostName': list(), 'userName': list()}
            poll_data[channel.lower()]['vote'] = {'yes': 0, 'no': 0}

            irc.send_private_message(channel,
                                     'Current Poll for {0}: \"{1}\" By {2} on {3}, !vote yes or !vote no'.format(
                                         str(channel),
                                         str(poll_data[channel.lower()]['poll']),
                                         str(poll_data[channel.lower()]['creator']),
                                         str(time.ctime(poll_data[channel.lower()]['createdTime']))))

    elif command[0].lower() == '!abortpoll':
        channel_info = irc.get_channel_info()

        if channel in poll_data:
            if user in channel_info[channel]['Admin'] or user in channel_info[channel]['Owner'] \
                    or user == poll_data[channel]['creator']:
                irc.send_private_message(channel, 'The poll for this channel has aborted by {0}. '
                                                  'The Final results are...'.format(str(user)))
                irc.send_private_message(channel,
                                         'Poll for {0}: \"{1}\" By {2} on {3}, Votes: Yes: {4} No: {5}'.format(
                                             str(channel),
                                             str(poll_data[channel]['poll']),
                                             str(poll_data[channel]['creator']),
                                             str(time.ctime(poll_data[channel]['createdTime'])),
                                             str(poll_data[channel]['vote']['yes']),
                                             str(poll_data[channel]['vote']['no'])))

                del poll_data[channel]
            else:
                irc.send_private_message(channel, '5ERROR: Only a channel admin, channel owner '
                                                  'or the OP of the poll to abort the current poll.')

    elif command[0].lower() == '!poll':
        if channel in poll_data:
            irc.send_private_message(channel,
                                     'Current Poll for {0}: \"{1}\" By {2} on {3}, !vote yes or !vote no'.format(
                                         str(poll_data[channel]['channel']),
                                         str(poll_data[channel]['poll']),
                                         str(poll_data[channel]['creator']),
                                         str(time.ctime(poll_data[channel]['createdTime']))))
        else:
            irc.send_private_message(channel, '5ERROR: The poll for this channel expired or does not exist.')

    elif command[0].lower() == '!currentpolls':
        if irc.user_info[user]['botLevel'] >= 3:
            if len(poll_data) > 1:
                irc.send_private_message(user, 'Polls - (Total: ' + str(len(poll_data)) + ')')
                for poll_channel in poll_data:
                    irc.send_private_message(user,
                                             'Poll in {0}: \"{1}\" By {2} on {3}, Votes: Yes: {4} No: {5}'.format(
                                                 str(poll_data[poll_channel]['channel']),
                                                 str(poll_data[poll_channel]['poll']),
                                                 str(poll_data[poll_channel]['creator']),
                                                 str(time.ctime(poll_data[poll_channel]['createdTime'])),
                                                 str(poll_data[poll_channel]['vote']['yes']),
                                                 str(poll_data[poll_channel]['vote']['no'])))
            else:
                irc.send_private_message(user, '5ERROR: No polls are currently active.')
