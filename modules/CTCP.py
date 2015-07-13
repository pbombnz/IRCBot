import time

CTCP_VERSION_REPLY = "The Kobra Framework - By Prashant B. (https://github.com/pbombnz)"


def on_ctcp(irc, user_mask, user, target, ctcp_command, ctcp_params):
    ctcp_command = ctcp_command.lower()

    if ctcp_command == "ping":
        irc.send_raw_message("NOTICE "+user+" :\001PING " + str(time.time()) + "\001")

    elif ctcp_command == "time":
        irc.send_raw_message("NOTICE "+user+" :\001TIME " + str(time.ctime(time.time())) + "\001")
        
    elif ctcp_command == "version":
        irc.send_raw_message("NOTICE "+user+" :\001VERSION " + str(irc.resources.CTCP_VERSION_REPLY) + "\001")
        
    elif ctcp_command == "finger":
        irc.send_raw_message("NOTICE "+user+" :\001VERSION " + str(irc.resources.CTCP_VERSION_REPLY) + "\001")
