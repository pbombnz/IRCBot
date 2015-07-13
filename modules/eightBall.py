import random

questions = dict()
answers = ["The answer lies in your heart...", "I do not know", "Almost certainly", "No", "Yes",
           "Go away. I do not wish to answer at this time.", "Only time will tell"]

def on_channel_pm(irc, user_mask, user, channel, message):
    command = message.split()[0].lower()

    if command[0].lower() == '!8ball':
        if len(command) >= 2:
            question = message.split(' ', 1)[1]
            if question not in questions:
                n = random.randint(0, len(answers))
                questions[question] = str(answers[n])
            irc.send_private_message(channel, user + ', ' + str(questions[question]))
        else:
            irc.send_private_message(channel, 'USAGE: !8ball (Question)')
