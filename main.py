import os
import base64
import email
import imaplib
from twilio.rest import Client

# twillio settings
account = os.environ['TWILLIO_ACCOUNT_NUM']
token = os.environ['TWILLIO_TOKEN']
client = Client(account, token)

# email settings
imap = imaplib.IMAP4_SSL(os.environ['EMAIL_IMAP_DOMAIN'], port=os.environ['EMAIL_IMAP_PORT'])
imap.login(os.environ['EMAIL_LOGIN'], os.environ['EMAIL_ACCOUNT_TOKEN'])
imap.select(readonly=1)


def logout_email():
    imap.close()
    imap.logout()


status, response = imap.uid('search', '(UNSEEN)')

if status != 'OK':
    logout_email()

messagesIds = response[0].decode("utf-8").split(' ')

unread_email = ''

for messageId in messagesIds:
    print('getting message for: ' + messageId)
    sts, res = imap.uid('fetch', str(messageId), '(RFC822)')
    msg = email.message_from_bytes(res[0][1])
    if msg.get_payload()[0]['Content-Transfer-Encoding'] == 'base64':
        body = base64.b64decode(msg.get_payload()[0].get_payload()).decode("utf-8")
    else:
        body = msg.get_payload()[0].get_payload()
    unread_email \
        += 'From:' + msg.get_all('FROM')[0] + '\n\n' \
           + body[:100] + '...' + '\n\n------------------------------------------------------\n\n'

print(unread_email)

client.messages.create(to= os.environ['TO_NUMBER'],  from_=os.environ['FROM_NUMBER'], body=unread_email)


logout_email()
