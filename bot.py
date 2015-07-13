import irclib

server = "irc.sacnr.com"
port = 6697
ssl = True
user_name = "K"
nick_name = "Kobra"
real_name = "Kobra - IRC Python Framework (By PBombNZ)"
password = str()

irc = irclib.Bot(server, port, True, nick_name, user_name, real_name, password)
irc.connect()
irc.join('#PBomb')
