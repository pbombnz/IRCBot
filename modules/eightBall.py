import random

eightBall = {"answers": ["The answer lies in your heart...", "I do not know", "Almost certainly", "No", "Yes",
                         "Go away. I do not wish to answer at this time.", "Only time will tell"],
             "questions": {"hello": "This is not a question"}
             }


def on_channel_pm(irc, user_mask, user, channel, message):
    command = message.split()[0].lower()

    if command[0].lower() == '!8ball':
        if len(command) >= 2:
            message = message.split(' ', 1)[1]
            if message not in eightBall["questions"]:
                n = random.randint(0, len(eightBall["answers"]) - 1)
                eightBall["questions"][command[1]] = str(eightBall["answers"][n])
            irc.send_private_message(channel, user + ', ' + str(eightBall["questions"][command[1]]))
        else:
            irc.send_private_message(channel, 'USAGE: !8ball (Question)')
