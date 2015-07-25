from irclib.module import *


class Module(IRCModule):
    def __init__(self, bot: IRCBot):
        super().__init__(bot)
        bot.add_attributes(BOT_OWNER="PBomb")
