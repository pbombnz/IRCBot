from irclib.bot import IRCBot

server = "irc.sacnr.com"
port = 6697
ssl = True
user_name = "PythonBot"
nick_name = "PythonBot"
real_name = "IRC Python Framework (By Prashant B.)"
password = str()

irc = IRCBot(server, port, True, nick_name, user_name, real_name, password)
irc.connect()
irc.join('#PBomb')
