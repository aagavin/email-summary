import os
from twilio.rest import Client
import imaplib


class TwillioSettings:
    def __init__(self):
        account = os.environ['TWILLIO_ACCOUNT_NUM']
        token = os.environ['TWILLIO_TOKEN']
        self.client = Client(account, token)
        self.to_number = os.environ['TO_NUMBER']
        self.from_number = os.environ['FROM_NUMBER']


class EmailSettings:
    def __init__(self):
        self.imap = imaplib.IMAP4_SSL(os.environ['EMAIL_IMAP_DOMAIN'], port=os.environ['EMAIL_IMAP_PORT'])

    def login(self):
        self.imap.login(os.environ['EMAIL_LOGIN'], os.environ['EMAIL_ACCOUNT_TOKEN'])
        self.imap.select(readonly=1)

    def logout(self):
        self.imap.close()
        self.imap.logout()
        exit(0)

    def search_unread(self):
        return self.imap.uid('search', '(UNSEEN)')

    def get_message(self, message_id: str):
        return self.imap.uid('fetch', str(message_id), '(RFC822)')
