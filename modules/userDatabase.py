import json
import os

# 0 Reg
# 1 Trusted
# 2 Admin
# 3 Owner


def create_user_account(irc, nick_name, access_level=0):
    if nick_name.lower() not in irc.user_info:
        irc.user_info[nick_name.lower()] = {
            "nick_name": nick_name,
            "access_level": access_level,
            "quiz": {"participated": 0,
                     "correct": 0,
                     "incorrect": 0},
            "steam64": str(),
            "whatpulse": str(),
            "location": str(),
        }
    save_user_database(irc)


def save_user_database(irc):
    file = open('./resources/users.dat', 'w')
    json.dump(irc.user_info, file)
    file.close()


def load_user_database(irc):
    file = open('./resources/users.dat', 'r')
    irc.user_info = json.load(file)
    file.close()


def on_init(irc):
    if os.path.isfile("./resources/users.dat"):
        irc.add_attributes(user_info=dict())
        load_user_database(irc)
    else:
        try:
            bot_owner = irc.get_resources.BOT_OWNER
        except NameError:
            irc.quit(error_message="bot owner undefined in resources module. Create a variable called \"BOT_OWNER\" "
                                   "and declare it as bot owner's irc nickname.", reconnect_on_error=False)
            return

        irc.add_attributes(user_info=dict())
        create_user_account(irc, bot_owner, 3)
        save_user_database(irc)


def on_nick_change(irc, user_mask, user_old_nick, user_new_nick):
    create_user_account(irc, user_new_nick)


def on_join(irc, user_mask, user_nick, channel):
    create_user_account(irc, user_nick)


def on_raw_numeric(irc, mask, numeric, message):
    if numeric == '353':
        # collecting actually string of nicks
        users_list = message.split()
        # Sorting each name into right admin group
        for user_with_op_symbols in users_list:
            if user_with_op_symbols != '':
                user = user_with_op_symbols[1:]
                if user_with_op_symbols.startswith('~') or user_with_op_symbols.startswith('&') \
                        or user_with_op_symbols.startswith('@') or user_with_op_symbols.startswith('%') \
                        or user_with_op_symbols.startswith('+'):
                    pass
                else:
                    user = user_with_op_symbols
                create_user_account(irc, user)
