import os
import datetime
import imaplib
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from twilio.rest import Client


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


class SentMessageIds:
    def __init__(self):
        cred = credentials.Certificate({
            "type": os.getenv('type'),
            "project_id": os.getenv('project_id'),
            "private_key_id": os.getenv('private_key_id'),
            "private_key": os.getenv('private_key').replace('\\n', '\n'),
            "client_email": os.getenv('client_email'),
            "client_id": os.getenv('client_id'),
            "auth_uri": os.getenv('auth_uri'),
            "token_uri": os.getenv('token_uri'),
            "auth_provider_x509_cert_url": os.getenv('auth_provider_x509_cert_url'),
            "client_x509_cert_url": os.getenv('client_x509_cert_url')
        })

        firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv('databaseURL')
        })

        self.data = self.create_new_dict()
        self.ref = db.reference('/')
        if self.ref.get() and 'message_ids' in self.ref.get():
            d: dict = self.ref.get()
            db_date = datetime.datetime.strptime(d['last_update'], '%Y-%m-%d %H:%M:%S.%f')
            if abs((self.data['last_update']-db_date).days) > 1:
                self.data = self.create_new_dict()
            else:
                self.data['message_ids'] = set(d['message_ids'])
        else:
            self.save_sent_messages()

    @staticmethod
    def create_new_dict() -> dict:
        return {
            'message_ids': set(),
            'last_update': datetime.datetime.now()
        }

    def add_message_id(self, message_id: str) -> None:
        self.data['message_ids'].add(message_id)

    def get_message_ids(self) -> set:
        return self.data['message_ids']

    def save_sent_messages(self):
        self.ref.set({
            'message_ids': list(self.data['message_ids']),
            'last_update': str(self.data['last_update'])
        })
