import hashlib
import base64


def on_channel_pm(irc, user_mask, user, channel, message):
    del user_mask
    command = message.split()

    if command[0].lower() == '!md5':
        if len(command) == 2:
            command = message.split(' ', 1)
            irc.send_private_message(channel, "MD5: " + str(hashlib.md5(str(command[1])).hexdigest()))
        else:
            irc.send_private_message(channel, "USAGE: !md5 (String)")

    elif command[0].lower() == '!sha':
        if len(command) == 2:
            command = message.split(' ', 1)
            irc.send_private_message(channel, "SHA-1: " + str(hashlib.sha1(str(command[1])).hexdigest()))
            irc.send_private_message(channel, "SHA-256: " + str(hashlib.sha256(str(command[1])).hexdigest()))
            irc.send_private_message(user, "SHA-384: " + str(hashlib.sha384(str(command[1])).hexdigest()))
            irc.send_private_message(user, "SHA-512: " + str(hashlib.sha512(str(command[1])).hexdigest()))
        else:
            irc.send_private_message(channel, "USAGE: !sha (String)")
            irc.send_private_message(channel, "USAGE: This command encodes the string to SHA1, SHA256, "
                                              "SHA384, SHA512. SHA384 and SHA512 are sent to the user privately.")

    elif command[0].lower() == '!baseencode':
        if len(command) >= 2:
            command = message.split(' ', 1)
            irc.send_private_message(channel, 'BASE64: ' + str(base64.b64encode(command[1])))
            irc.send_private_message(channel, 'BASE32: ' + str(base64.b32encode(command[1])))
            irc.send_private_message(channel, 'BASE16: ' + str(base64.b16encode(command[1])))
        else:
            irc.send_private_message(channel, "USAGE: !baseencode (String)")

    elif command[0].lower() == '!basedecode':
        if len(command) >= 2:
            command = message.split(' ', 1)
            irc.send_private_message(channel, "DECODED BASE64: " + str(base64.b64decode(command[1])))
            irc.send_private_message(channel, "DECODED BASE32: " + str(base64.b32decode(command[1])))
            irc.send_private_message(channel, "DECODED BASE16: " + str(base64.b16decode(command[1])))
        else:
            irc.send_private_message(channel, "USAGE: !base64encode (Base64 String)")
