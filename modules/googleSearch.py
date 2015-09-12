import urllib.request
import html
import json

GOOGLE_SEARCH_URL = "http://ajax.googleapis.com/ajax/services/search/web?v=2.0&q="
NUMBER_OF_RESULTS_PRINTED = 3
BLACKLIST_RESULT_LIMIT = 1

PORN_WORD_LIST = ['2g1c', 'acrotomophilia', 'anal', 'anilingus', 'anus', 'arse', 'arsehole', 'ass', 'asshole',
                  'assmunch', 'autoerotic', 'babeland', 'bangbros',
                  'bareback', 'barenaked', 'bastardo', 'bastinado', 'bbw', 'bdsm', 'bestiality', 'bimbos', 'birdlock',
                  'bitch', 'blumpkin', 'bollocks',
                  'bondage', 'boner', 'boob', 'boobs', 'bukkake', 'bulldyke', 'bunghole', 'busty', 'butt', 'buttcheeks',
                  'butthole', 'camgirl', 'camslut',
                  'camwhore', 'carpetmuncher', 'circlejerk', 'clit', 'clitoris', 'clusterfuck', 'cock', 'cocks', 'coc',
                  'coprolagnia', 'coprophilia', 'cornhole',
                  'cum', 'cumshot', 'cumshoot', 'cumming', 'cunnilingus', 'cunt', 'darkie', 'daterape', 'deepthroat',
                  'dilf', 'dic', 'dick', 'dildo', 'doggiestyle', 'doggystyle', 'dolcett',
                  'domination', 'dominatrix', 'dommes', 'ecchi', 'ejaculation', 'erotic', 'erotism', 'escort', 'eunuch',
                  'faggot', 'fecal', 'felch', 'fellatio',
                  'feltch', 'femdom', 'figging', 'fingering', 'fisting', 'footjob', 'frotting', 'fuck', 'fudgepacker',
                  'futanari', 'g-spot', 'genitals', 'goatcx',
                  'goatse', 'gokkun', 'goodpoop', 'goregasm', 'grope', 'guro', 'handjob', 'hardcore', 'hentai',
                  'homoerotic', 'honkey', 'hooker', 'humping', 'incest',
                  'intercourse', 'jailbait', 'jigaboo', 'jiggaboo', 'jiggerboo', 'jizz', 'juggs', 'kike', 'kinbaku',
                  'kinkster', 'kinky', 'knobbing', 'lolita',
                  'lovemaking', 'lesbian', 'lesbians', 'lesbians', 'masturbate', 'milf', 'motherfucker', 'muffdiving',
                  'nambla', 'nawashi', 'negro', 'neonazi', 'nigga', 'nigger',
                  'nimphomania',
                  'nipple', 'nipples', 'nude', 'nudes', 'nudity', 'nympho', 'nymphomania', 'octopussy', 'omorashi',
                  'orgasm', 'orgy', 'paedophile', 'panties', 'panty',
                  'pedobear', 'pedophile', 'pegging', 'penis', 'pissing', 'pisspig', 'playboy', 'ponyplay', 'poof',
                  'poopchute', 'porn', 'porno', 'pornography',
                  'pthc', 'pubes', 'pussy', 'queaf', 'raghead', 'rape', 'raping', 'rapist', 'rectum', 'redtube',
                  'redtube.com', 'rimjob', 'rimming', 's&m', 'sadism', 'scat',
                  'schlong',
                  'scissoring', 'semen', 'sex', 'sexo', 'sexy', 'shemale', 'shibari', 'shit', 'shota', 'shrimping',
                  'slanteye', 'slut', 'smut', 'snatch', 'snowballing',
                  'sodomize', 'sodomy', 'spic', 'spooge', 'strapon', 'strappado', 'suck', 'sucks', 'swastika',
                  'swinger', 'threesome', 'throating', 'tit', 'tits',
                  'titties', 'titty', 'topless', 'tosser', 'towelhead', 'tranny', 'tribadism', 'tubgirl', 'tushy',
                  'twat', 'twink', 'twinkie', 'undressing',
                  'upskirt', 'urophilia', 'vagina', 'vibrator', 'vorarephilia', 'voyeur', 'vulva', 'wank', 'whore',
                  'wetback', 'xvideos', 'xvideo', 'xx', 'xxx', 'yaoi', 'yiffy', 'zoophilia']

PORN_PHRASE_LIST = ['1 guy 1 jar', '2 girls 1 cup', 'auto erotic', 'baby batter', 'ball gag', 'ball gravy',
                    'ball kicking', 'ball licking', 'ball sack', 'ball sucking',
                    'barely legal', 'beaver cleaver', 'beaver lips', 'bi curious', 'big black', 'big breasts',
                    'big knockers', 'big tits', 'black cock',
                    'blonde action', 'blonde on blonde action', 'blow j', 'blow your l', 'blue waffle', 'booty call',
                    'brown showers', 'brunette action',
                    'bullet vibe', 'bung hole', 'camel toe', 'carpet muncher', 'chocolate rosebuds',
                    'cleveland steamer', 'clover clamps', 'date rape',
                    'deep throat', 'dirty pillows', 'dirty sanchez', 'dog style', 'doggie style', 'doggy style',
                    'donkey punch', 'double dong',
                    'double penetration', 'dp action', 'eat my ass', 'ethical slut', 'female squirting', 'foot fetish',
                    'fuck buttons', 'fudge packer',
                    'gang bang', 'gay sex', 'giant cock', 'girl on', 'girl on top', 'girls gone wild', 'golden shower',
                    'goo girl', 'group sex', 'hand job',
                    'hard core', 'hot chick', 'how to kill', 'how to murder', 'huge fat', 'jack off', 'jail bait',
                    'jerk off', 'leather restraint',
                    'leather straight jacket', 'lemon party', 'make me come', 'male squirting', 'menage a trois',
                    'missionary position', 'mound of venus',
                    'mr hands', 'muff diver', 'nig nog', 'nsfw images', 'one cup two girls', 'one guy one jar',
                    'phone sex', 'piece of shit', 'piss pig',
                    'pleasure chest', 'pole smoker', 'poop chute', 'prince albert piercing', 'raging boner',
                    'reverse cowgirl', 'rosy palm',
                    'rosy palm and her 5 sisters', 'rusty trombone', 'shaved beaver', 'shaved pussy', 'spread legs',
                    'spread legs', 'strap on', 'strip club', 'style doggy',
                    'suicide girls', 'sultry women', 'tainted love', 'taste my', 'tea bagging', 'tied up',
                    'tight white', 'tongue in a', 'tub girl',
                    'two girls one cup', 'urethra play', 'venus mound', 'violet wand', 'wet dream',
                    'white power', 'women rapping',
                    'wrapping men', 'wrinkled starfish', 'yellow showers', 'pain olympics']

BAD_CONTENT_WORD_LIST = ["0-day", "cracks", "crackz", "dox", "fixedexe", "nocd", "nodvd", "keygens", "keygenz",
                         "isohunt", "kickass" "kat", "kickass.to", "kat.cr"
                         "serials", "serialz", "s0beit", "sobeit", "torrent", "piratebay.org", "piratebay.se",
                         "piratebay", "warez", "ware"]

BAD_CONTENT_PHRASE_LIST = ["ddos", "dvd rips", "bluray rips", "tv rips", "how to create botnet", "how to ddos",
                           "how to attack", "p2p", "pirate bay"]


def on_channel_pm(irc, user_mask, user_nick, channel, message):
    command = message.split()
    
    if command[0].lower() == "!google":
        if len(command) >= 2:
            command = message.split(' ', 1)
            query_str = command[1].lower()
            query = query_str.split()
            for query_str in query:
                if query_str in PORN_WORD_LIST or query_str in BAD_CONTENT_WORD_LIST:
                    irc.send_private_message(channel, "5ERROR: The search query requested contains explicit "
                                                      "content not allowed on this IRC network.")
                    return
                
            for phrase in PORN_PHRASE_LIST:
                if command[1].find(phrase) != -1:
                    irc.send_private_message(channel, "5ERROR: The search query requested contains explicit "
                                                      "content not allowed on this IRC network.")
                    return
            for phrase in BAD_CONTENT_PHRASE_LIST:
                if command[1].find(phrase) != -1:
                    irc.send_private_message(channel, "5ERROR: The search query requested contains explicit "
                                                      "content not allowed on this IRC network.")
                    return
            try:
                response = urllib.request.urlopen(GOOGLE_SEARCH_URL + str(command[1]))
                html_source = response.read().decode('utf-8')
                response.close()
            except IOError:
                irc.sendPrivateMessage(irc, channel, "5ERROR: Can't connect to Google at the moment. Try again later.")
                return
            
            results = json.loads(html_source)
            if len(results['responseData']['results']) > 0:
                num_blacklist_results = 0
                for resultNumber in range(len(results['responseData']['results'])):
                    if num_blacklist_results > BLACKLIST_RESULT_LIMIT:
                        irc.send_private_message(channel, "5ERROR: The search query requested contains explicit"
                                                          " content not allowed on this IRC network.")
                        break

                    if resultNumber > NUMBER_OF_RESULTS_PRINTED:
                        break

                    result_title = html.unescape(results['responseData']['results'][resultNumber]['titleNoFormatting'])
                    result_title_split = result_title.lower().split()

                    profanity_found = False

                    for resultTitleWord in result_title_split:
                        if resultTitleWord in PORN_WORD_LIST or resultTitleWord in BAD_CONTENT_WORD_LIST:
                            profanity_found = True
                            break
                    if not profanity_found:
                        for pornPhrase in PORN_PHRASE_LIST:
                            if result_title.lower().find(pornPhrase) != -1:
                                profanity_found = True
                                break
                    if not profanity_found:
                        for illegalContentPhrase in BAD_CONTENT_PHRASE_LIST:
                            if result_title.lower().find(illegalContentPhrase) != -1:
                                profanity_found = True
                                break

                    if profanity_found:
                        num_blacklist_results += 1
                        break

                    result_url = results['responseData']['results'][resultNumber]['url']
                    irc.send_private_message(channel, "10Result " + str(resultNumber+1) + ":1 "
                                             + str(result_title) + " 10Link:1 " + str(result_url))
            else:
                irc.send_private_message(channel, "5ERROR: No results found.")
        else:
            irc.send_private_message(channel, "USAGE: !google (Query)")
