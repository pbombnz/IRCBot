class IRCModuleException(Exception):
    def __init__(self, module_name: str, exception: Exception):
        self.module_name = module_name
        self.exception = exception
        pass


"""
MODULE DESIGN:
    def on_init(bot):
        pass

    def on_process_forever(bot):
        pass

    def on_connect(bot):
        pass

    def on_raw_numeric(bot, mask, numeric, target, message):
        pass

    def on_nick_change(bot, user_mask, user_old_nick, user_new_nick):
        pass

    def on_action(bot, user_mask, user_nick, channel, action):
        pass

    def on_channel_pm(bot, user_mask, user_nick, channel, message):
        pass

    def on_ctcp(bot, user_mask, user_nick, target, ctcp_command, ctcp_params):
        pass

    def on_user_pm(bot, user_mask, user_nick, target, message):
        pass

    def on_kick(bot, user_mask, user_nick, channel, target, message):
        pass

    def on_invite(bot, user_mask, user_nick, target, channel):
        pass

    def on_join(bot, user_mask, user_nick, channel):
        pass

    def on_part(bot, user_mask, user_nick, channel, part_message):
        pass

    def on_quit(bot, user_mask, user_nick, quit_message):
        pass

    def on_channel_notice(bot, user_mask, user_nick, channel, message):
        pass

    def on_user_notice(bot, user_mask, user_nick, target, message):
        pass

    def on_notice_auth(bot, mask, message):
        pass

    def on_ping(bot, ping_reply):
        pass

    def on_mode_user(bot, user, target, mode_sting):
        pass

    def on_mode_channel_setbyuser(bot, user_mask, user_nick, channel, mode_sting, mode_params):
        pass

    def on_mode_channel_setbyserv(bot, serv_user, channel, mode_sting, mode_params):
        pass

    def on_error(bot, error_message):
        pass

    def on_unload(bot):
        pass
"""
