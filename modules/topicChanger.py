#!/usr/bin/python
# -*- coding: utf-8 -*-

IRC_TOPIC_TEMPLATES = ['4,9Â°~`~*Â¤Â§Æ’12 TOPIC_HERE 4Æ’Â§Â¤*~`~Â°',
                       '9,1Ã¸Â¤Â°`Â°Â¤Ã¸  TOPIC_HERE 9,1Ã¸Â¤Â°`Â°Â¤Ã¸ ',
                       '4Â©ÂºÂ°Â¨Â¨Â°ÂºÂ©Â©ÂºÂ°Â¨Â¨Â°ÂºÂ©12 TOPIC_HERE 4Â©ÂºÂ°Â¨Â¨Â°ÂºÂ©Â©ÂºÂ°Â¨Â¨Â°ÂºÂ©',
                       '12(Â¯`Â·._(Â¯`Â·._(Â¯`Â·._(4 TOPIC_HERE 12)_.Â·Â´Â¯)_.Â·Â´Â¯)_.Â·Â´Â¯)',
                       '4 (Â¯`Â·.Â¸Â¸.Â·Â´Â¯`Â·.Â¸Â¸.->12 TOPIC_HERE 8<-.Â¸Â¸.Â·Â´Â¯`Â·.Â¸Â¸.Â·Â´Â¯)',
                       '4Â¯Â°Â·.Â¸Â¸.Â·Â°Â¯Â°Â·.Â¸Â¸.Â·Â°Â¯Â°Â·.Â¸Â¸.->12 TOPIC_HERE 4<-.Â¸Â¸.Â·Â°Â¯Â°Â·.Â¸Â¸.Â·Â°Â¯Â°Â·.Â¸Â¸.Â·Â°Â¯',
                       '8,12.,-*-,._.,-*"^"~*-,._.,-*~>4 TOPIC_HERE 8<~*-,._.,-*~"^"~*-,._.,-*-,.',
                       '11|!Â¤*"~``~"*Â¤!||!Â¤*"~``~"*Â¤!|13 TOPIC_HERE 11|!Â¤*"~``~"*Â¤!||!Â¤*"~``~"*Â¤!|',
                       '4.8Â§Â¤*~`~*Â¤Â§|Â§Â¤*~`~*Â¤Â§|Â§Â¤*~ -=Â?=-12 TOPIC_HERE 4-=Â?=- ~*Â¤Â§|Â§Â¤*~`~*Â¤Â§|Â§Â¤*~`~*Â¤Â§',
                       '12,1,Ã¸Â¤Â°9`11Â°Â¤Ã¸,Â¸ 12Â¸,Ã¸Â¤Â°9`11Â°Â¤Ã¸,Â¸ TOPIC_HERE 12,1,Ã¸Â¤Â°9`11Â°Â¤Ã¸,Â¸ 12Â¸,Ã¸Â¤Â°9`11Â°Â¤Ã¸,Â¸',
                       '9,1.Â»Âº}8Â®9{ÂºÂ«Âº}8Â®9{ÂºÂ«. TOPIC_HERE 9,1.Â»Âº}8Â®9{ÂºÂ«Â»Âº}8Â®9{ÂºÂ«.',
                       '3,1{Ã¦{13Â©3{Ã¦{13Â©3{Ã¦{13Â©3{Ã¦{13Â© 12{  TOPIC_HERE 12,1} 13Â©3}Ã¦}13Â©3}Ã¦}13Â©3}Ã¦}13Â©3}Ã¦}',
                       '0,19Â¿13?7Â¿11?9Â¿13?7Â¿109Â¿13?7Â¿11?9Â¿13?7Â¿10 TOPIC_HERE 0,19Â¿13?7Â¿11?9Â¿13?7Â¿109Â¿13?7Â¿11?9Â¿13?7Â¿10',
                       '2!3Â¡4!6Â¡7!8Â¡9!10Â¡11!12Â¡13!14Â¡2!3Â¡46!7Â¡8!9Â¡10!11Â¡ 4 TOPIC_HERE 2!3Â¡4!6Â¡7!8Â¡9!10Â¡11!12Â¡13!14Â¡2!3Â¡46!7Â¡8!9Â¡10!11Â¡ 4',
                       '12Â»Â»-4(Â¯`vÂ´Â¯)12--Â»6 TOPIC_HERE 12Â»Â»-4(Â¯`vÂ´Â¯)12--Â»6',
                       '4,2Â«2,4Â»13,2Â«2,13Â»15,2Â«2,15Â»8,2Â«2,8Â»11,2Â«2,11Â»9,2Â«2,9Â»0,1 TOPIC_HERE 2,9Â«9,2Â»2,11Â«11,2Â»2,8Â«8,2Â»2,15Â«15,2Â»2,13Â«13,2Â»2,4Â«4,2Â»',
                       '8,0|0,8|7,8|8,7|4,7|7,4|5,4|4,5|1,5|5,1| 9,1 TOPIC_HERE 5,1 |1,5|4,5|5,4|7,4|4,7|8,7|7,8|',
                       '3,1\1,3\9,3\3,9\0,9\9,0\0,0-15,0\0,15\14,15\15,14\1,14\14,1\1,1-0,1 TOPIC_HERE 1,1-14,1/1,14/15,14/14,15/0,15/15,0/0,0-9,0/0,9/3,9/9,3/1,3/3,1/0,0',
                       '8,1Â®8,14Â®8,15Â®8,0Â®8,15Â®8,14Â®8,1Â® 0 TOPIC_HERE 8,1Â®8,14Â®8,15Â®8,0Â®8,15Â®8,14Â®8,1Â®',
                       '8,6Â¯0`Â°Â²Âº4Â¤8Ã¦=Â¬0Â«.,Â¸8_0,6 TOPIC_HERE 8,6_Â¸,.0Â»Â¬=8Ã¦4Â¤0ÂºÂ²Â°`8Â¯',
                       '2{3{4{5{6{7{8{9{10{11{12{13{14{15{2{3{4{5{6{7{8{9{10{11{12{13{14{15{1 TOPIC_HERE 15}14}13}12}11}10}9}8}7}6}5}4}3}2}15}14}13}12}11}10}9}8}7}6}5}4}3}2}',
                       '1,11,21,31,41,51,61,71,81,91,108,1  TOPIC_HERE  1,101,91,81,71,61,51,41,31,21',
                       '1215,8%8,8|4,8%8,4%4,4|5,4%4,5%5,5|1,5%5,1%1-- 16 TOPIC_HERE 1--5,1%1,5%5,5|4,5%5,4%4,4|8,4%4,8%8,8|15,8%1',
                       '9`%16,9%,  3,9`%9,3%,  1,3`%3,1%,16,1 TOPIC_HERE 3,1`%1,3%,  9,3`%3,9%,  16,9`%9,16%, 1',
                       '0,15%,14`%15,14%,1`%14,1%,15,1 TOPIC_HERE  14,1`%1,14%,15`%14,15%,0`%3,0',
                       '15,0,%0,15%`13,15,%15,13%`6,13,%13,6%`5,6,% 8 TOPIC_HERE 5,6%,13,6`%6,13%,15,13`%13,15%,0,15`%15,0%,',
                       '8,0 ,%0,8%`7,8,%8,7%`4,7,%7,4%`8,4 TOPIC_HERE 7,4`%4,7%,8,7`%7,8%,0,8`%8,0%, ',
                       '13,0<0,13>6,13<13,6>2,6<6,2>1,2<2,1>0,1 TOPIC_HERE 2,1<1,2>6,2<2,6>13,6<6,13>0,13<13,0>']


def on_channel_pm(irc, user_mask, user, channel, message):
    command = message.split()

    if command[0].lower() == '!settopic':
        if irc.nick_name in irc.get_channel_info()[channel]["Voice"] \
        or irc.nick_name in irc.get_channel_info()[channel]["Regular"]:
            irc.send_private_message(channel, '5ERROR: I do not have privilages to change the topic.')
            return

        if user in irc.get_channel_info()[channel]["Voice"] or user in irc.get_channel_info()[channel]["Regular"]:
            irc.send_private_message(channel, '5ERROR: You do not have access to this command.')
            return

        if len(command) < 3:
            irc.send_private_message(channel,'USAGE: !settopic (Topic Style [1- ' + str(len(IRC_TOPIC_TEMPLATES)) + ']) (Topic)')
            return

        command = message.split(' ', 2)

        if len(command[1]) < 1 or len(command[2]) < 1:
            irc.send_private_message(channel,'USAGE: !settopic (Topic Style [1- ' + str(len(IRC_TOPIC_TEMPLATES)) + ']) (Topic)')
            return

        if not command[1].isdigit():
            irc.send_private_message(channel,'USAGE: !settopic (Topic Style [1- ' + str(len(IRC_TOPIC_TEMPLATES)) + ']) (Topic)')
            return

        command[1] = int(command[1])
        if command[1] < 1 or command[1] > len(IRC_TOPIC_TEMPLATES):
             irc.send_private_message(channel, 'USAGE: !settopic (Topic Style [1- ' + str(len(IRC_TOPIC_TEMPLATES)) + ']) (Topic)')
             return

        command[1] = command[1] - 1
        irc.sendRawMessage('TOPIC ' + channel + ' :' + str(IRC_TOPIC_TEMPLATES[command[1]].replace('TOPIC_HERE', str(command[2]))))

    if command[0].lower() == '!topicstyles':
        is_channel_admin = False
        for op in irc.get_channel_info()[channel]:
            if op == "Voice" or op == "Regular":
                continue
            if user in irc.get_channel_info()[channel][op]:
                is_channel_admin = True
                break

        if is_channel_admin:
            for templateNum in range(len(IRC_TOPIC_TEMPLATES)):
                irc.send_private_message(user_mask[0], str(templateNum + 1) + '. ' + IRC_TOPIC_TEMPLATES[templateNum])
        else:
            irc.send_private_message(user_mask[0], "5ERROR: You do not have privilages to change the topic in this "
                                                  "channel, therefore you cannot use this command.")
