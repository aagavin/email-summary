import base64
import email
from objects import TwillioSettings, EmailSettings

tw = TwillioSettings()
em = EmailSettings()

em.login()

status, response = em.search_unread()

if status != 'OK' or response[0] == b'':
    em.logout()

messagesIds = response[0].decode("utf-8").split(' ')

unread_email = ''

for messageId in messagesIds:
    print('getting message for: ' + messageId)
    sts, res = em.get_message(messageId)
    msg = email.message_from_bytes(res[0][1])
    if msg.get_payload()[0]['Content-Transfer-Encoding'] == 'base64':
        body = base64.b64decode(msg.get_payload()[0].get_payload()).decode("utf-8")
    else:
        body = msg.get_payload()[0].get_payload()
    unread_email \
        += 'From:' + msg.get_all('FROM')[0] + '\n\n' \
           + str(body[:100]) + '...' + '\n\n------------------------------------------------------\n\n'

print(unread_email)

tw.client.messages.create(to=tw.to_number, from_=tw.from_number, body=unread_email)


em.logout()
