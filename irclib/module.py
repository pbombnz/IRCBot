class IRCModuleException(Exception):
    def __init__(self, module_name: str, exception: Exception):
        self.module_name = module_name
        self.exception = exception
        pass


"""
class IRCModule(object):

    def __init__(self, bot):
        self.bot = bot

    def on_process_forever(self):
        pass

    def on_connect(self):
        pass

    def on_raw_numeric(self, mask, numeric, target, message):
        pass

    def on_nick_change(self, user_mask, user_old_nick, user_new_nick):
        pass

    def on_action(self, user_mask, user_nick, channel, action):
        pass

    def on_channel_pm(self, user_mask, user_nick, channel, message):
        pass

    def on_ctcp(self, user_mask, user_nick, target, ctcp_command, ctcp_params):
        pass

    def on_user_pm(self, user_mask, user_nick, target, message):
        pass

    def on_kick(self, user_mask, user_nick, channel, target, message):
        pass

    def on_invite(self, user_mask, user_nick, target, channel):
        pass

    def on_join(self, user_mask, user_nick, channel):
        pass

    def on_part(self, user_mask, user_nick, channel, part_message):
        pass

    def on_quit(self, user_mask, user_nick, quit_message):
        pass

    def on_channel_notice(self, user_mask, user_nick, channel, message):
        pass

    def on_user_notice(self, user_mask, user_nick, target, message):
        pass

    def on_notice_auth(self, mask, message):
        pass

    def on_ping(self, ping_reply):
        pass

    def on_mode_user(self, user, target, mode_sting):
        pass

    def on_mode_channel_setbyuser(self, user_mask, user_nick, channel, mode_sting, mode_params):
        pass

    def on_mode_channel_setbyserv(self, serv_user, channel, mode_sting, mode_params):
        pass

    def on_error(self, error_message):
        pass

    def on_unload(self):
        pass
"""
