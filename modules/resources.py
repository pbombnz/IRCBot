from irclib.module import IRCModule


class Module(IRCModule):
    def __init__(self, bot):
        super().__init__(bot)
        bot.add_attributes(BOT_OWNER="PBomb")
