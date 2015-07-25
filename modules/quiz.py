import os
import json
import time
import re
import random
from modules import userDatabase


class CaseInsensitiveDict(dict):
    def __contains__(self, key):
        return dict.__contains__(self, key.lower())

    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())

    def __setitem__(self, key, value):
        return dict.__setitem__(self, key.lower(), value)


tmp_quiz_data = CaseInsensitiveDict()
quiz_data = {'questions': list()}

# quizData = { "questions" : [{ "question" : cmd[1],
#                              "answers" : [ cmd[3] ],
#                              "bestTime" : [ "" , 0.0 ],
#                              "answeredCorrect" : 0,
#                              "answeredIncorrect" : 0,
#                              "answeredCorrectMessage" : "",
#                              "showAnswers" : True,
#                               
#                              "timePeriod" : float(cmd[2]),
#                              "creator" : sender[0],
#                              "createdTime" : time.time()
#                                                    } ]}


def save_quiz_database():
    file = open('./resources/quiz.dat', 'w')
    json.dump(quiz_data, file)
    file.close()


def load_quiz_database():
    global quiz_data
    file = open('./resources/quiz.dat', 'r')
    quiz_data = json.load(file)
    file.close()


def on_init(irc):
    if os.path.isfile("./resources/quiz.dat"):
        load_quiz_database()
    else:
        save_quiz_database()


def on_process_forever(bot):
    current_time = time.time()

    for channel in tmp_quiz_data:
        if tmp_quiz_data[channel.lower()]['isActive']:
            time_difference = current_time - tmp_quiz_data[channel]["startTime"]
            if time_difference >= tmp_quiz_data[channel]["timePeriod"]:
                if len(tmp_quiz_data[channel]["players"].keys()) > 1:
                    bot.send_private_message(channel, '5Quiz automatically finished - No one got the right answer.')
                else:
                    bot.send_private_message(channel, '5Quiz automatically finished - Time in the round ended.')

                save_quiz_database()
                del tmp_quiz_data[channel]
                return


def on_channel_pm(irc, user_mask, user, channel, message):
    global tmp_quiz_data, quiz_data

    command = message.split()

    for chan in tmp_quiz_data:
        if message.lower() in tmp_quiz_data[chan]["wrongAnswers"] or message.lower() == tmp_quiz_data[chan]["rightAnswer"]:
            if user.lower() not in tmp_quiz_data[chan]['players']:
                tmp_quiz_data[chan]['players'][user.lower()] = 0

            if tmp_quiz_data[chan]['players'][user.lower()] == 0:
                if message.lower() == tmp_quiz_data[chan]["rightAnswer"].lower():
                    real_time_secs = time.time()
                    irc.userData[user.lower()]["quiz"]["correct"] += 1
                    userDatabase.save_user_database(irc)
                    irc.send_private_message(channel,
                                             '3Congrats 1' + user + ', 3You have correctly answered the question.')
                    quiz_id = tmp_quiz_data[channel.lower()]['id']

                    if round(real_time_secs - tmp_quiz_data[chan]["startTime"], 2) < \
                            quiz_data["questions"][quiz_id]["bestTime"][1]:
                        time_dif = quiz_data["questions"][quiz_id]["bestTime"][1] - (
                            real_time_secs - tmp_quiz_data[chan]["startTime"])
                        quiz_data["questions"][quiz_id]["bestTime"][1] = round(
                            real_time_secs - tmp_quiz_data[chan]["startTime"], 2)
                        quiz_data["questions"][quiz_id]["bestTime"][0] = user
                        irc.send_private_message(channel, user + '3 has just set the new best time of ' + str(
                            quiz_data["questions"][quiz_id]["bestTime"][
                                1]) + ' 3secs. ' + user + ' 3beat the old best time by ' + str(
                            round(time_dif, 2)) + ' 3secs.')

                    elif quiz_data["questions"][quiz_id]["bestTime"][0] == "":
                        quiz_data["questions"][quiz_id]["bestTime"][1] = round(
                            real_time_secs - tmp_quiz_data[chan]["startTime"], 2)
                        quiz_data["questions"][quiz_id]["bestTime"][0] = user
                        irc.send_private_message(channel, user + '3 has just set the new best time of ' + str(
                            quiz_data["questions"][quiz_id]["bestTime"][1]) + ' 3secs.')

                    quiz_data["questions"][quiz_id]["answeredCorrect"] += 1
                    save_quiz_database()
                    del tmp_quiz_data[chan]
                else:
                    quiz_id = tmp_quiz_data[channel.lower()]['id']
                    irc.send_private_message(channel,
                                             '5Sorry 1' + user + ', 5that is the wrong answer. You cannot attempt anymore for this round.')
                    tmp_quiz_data[chan]["players"][user.lower()] += 1
                    quiz_data["questions"][quiz_id]["answeredIncorrect"] += 1
                    irc.user_info[user.lower()]["quiz"]["incorrect"] += 1

                irc.userData[user.lower()]["quiz"]["participated"] += 1
                userDatabase.save_user_database(irc)
                return

    if command[0].lower() == '!quizhelp':
        irc.send_private_message(channel,
                                 user + ', basically you get given a multi-choice question and your job is to carefully type in what you think is the right answer before the time runs out and before any other IRC users guess the right answer. You can only guess once, so double check that you are right. So what are you waiting for? start a !quiz.')

    elif command[0].lower() == '!quiz':
        if len(quiz_data['questions']) == 0:
            irc.send_private_message(channel, '5ERROR: No quiz questions in database.')
            return

        #if len(quiz_data['questions']) in range(0, 10):
        #    irc.send_private_message(channel,
        #                             '5ERROR: There are only a few quiz questions in database. Until more are added, the quiz will be unavailable.')
        #    return

        if channel in tmp_quiz_data:
            return

        random_quiz_id = random.randint(0, len(quiz_data['questions']))

        # print quizQuestionID
        # print "creating tmp data"
        tmp_quiz_data[channel] = dict()
        tmp_quiz_data[channel]['isActive'] = False
        tmp_quiz_data[channel]["numOfPlayers"] = 0
        tmp_quiz_data[channel]["players"] = {}
        tmp_quiz_data[channel]["timePeriod"] = float(quiz_data['questions'][random_quiz_id]["timePeriod"])
        tmp_quiz_data[channel]["rightAnswer"] = quiz_data['questions'][random_quiz_id]['answers'][0].lower()
        tmp_quiz_data[channel]["wrongAnswers"] = []

        for i in range(1, len(quiz_data['questions'][random_quiz_id]['answers'])):
            tmp_quiz_data[channel]["wrongAnswers"].append(quiz_data['questions'][random_quiz_id]['answers'][i].lower())

        tmp_quiz_data[channel]["startTime"] = round(time.time(), 1)
        tmp_quiz_data[channel]['id'] = random_quiz_id
        # print "creating tmp data (part 2)"

        quiz_answers = quiz_data['questions'][random_quiz_id]['answers']
        quiz_answers = sorted(quiz_answers, key=lambda k: random.random())

        tmp_quiz_data[channel.lower()]['isActive'] = True
        irc.send_private_message(channel, '6Question: "' + str(
            quiz_data['questions'][random_quiz_id]["question"]) + '" 6Answers: ' + str(quiz_answers).strip(
            '[]') + '.')
        if quiz_data['questions'][random_quiz_id]["bestTime"][0] != "":
            irc.send_private_message(channel,
                                     '\u00036Best time set by\u0003 {0} \u00036in\u0003 {1} \u00036secs.'.format(
                                         str(quiz_data['questions'][random_quiz_id]["bestTime"][0]),
                                         str(quiz_data['questions'][random_quiz_id]["bestTime"][1])))

    elif command[0].lower() == '!numberofquizquestions':
        irc.send_private_message(channel,
                                 "There are " + str(len(quiz_data['questions'])) + " questions in the Quiz database.")

    elif command[0].lower() == '!createquizquestion' or command[0].lower() == '!cqq':
        if irc.user_info[user.lower()]["access_level"] >= 1:
            question_re = re.compile("!c(?:(?:reate)?)q(?:(?:uiz)?)q(?:(?:uestion)?)\s(.*\?)\s([0-9]+[0-9]?)\s(.*)",
                                     re.IGNORECASE)
            match = question_re.match(message)
            if match:
                command_params = question_re.findall(message)[0]
                print(command_params)
                question = command_params[0]
                time_period = command_params[1]
                answer_str = command_params[2]

                if re.match('"([\w\s]*)"', answer_str):
                    answers = re.findall('"([\w\s]*)"', answer_str)
                else:
                    irc.send_private_message(channel, "USAGE: !c[reate]q[uiz]q[uestion] (Question)? "
                                                      "(Question Time Period (in Secs)) \"(Correct Answer)\" "
                                                      "\"(Wrong Answer)\" [\"(Wrong Answer)\" \"(...)\"]")
                    irc.send_private_message(channel, "EXAMPLE: !cqq 1 + 1 = ? 2 1 3 4 5")
                    return

                if int(time_period) < 5 or int(time_period) > 60:
                    irc.send_private_message(channel,
                                             '5ERROR: The time period is not pratical. Set a more appropriate time period (between 5 - 60 seconds).')
                    return

                for question_data in quiz_data['questions']:
                    if question_data['question'].lower() == question.lower():
                        irc.send_private_message(channel, '5ERROR: The question has already been created.')
                        return

                question_data = {"question": question,
                                 "answers": [],
                                 "bestTime": ["", 0.0],
                                 "answeredCorrect": 0,
                                 "answeredIncorrect": 0,
                                 "answeredCorrectMessage": "",
                                 "showAnswers": True,
                                 "timePeriod": float(time_period),
                                 "creator": user,
                                 "createdTime": time.time()
                                 }

                for i in range(0, len(answers)):
                    question_data['answers'].append(answers[i])

                quiz_data['questions'].append(question_data)
                save_quiz_database()

                irc.send_private_message(channel, '3SUCCESS: Quiz Question, "' + question + '" (ID: ' + str(
                    len(quiz_data['questions']) - 1) + ') has been added into the quiz database.')
            else:
                irc.send_private_message(channel, "USAGE: !c[reate]q[uiz]q[uestion] (Question)? "
                                                  "(Question Time Period (in Secs)) \"(Correct Answer)\" "
                                                  "\"(Wrong Answer)\" [\"(Wrong Answer)\" \"(...)\"]")
                irc.send_private_message(channel, "EXAMPLE: !cqq 1 + 1 = ? 2 1 3 4 5")
