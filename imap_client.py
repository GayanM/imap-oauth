# imap_client.py

import imaplib
from multiprocessing import context
import ssl
from config import IMAP_SERVER, IMAP_PORT, USERNAME


class IMAPClient:

    def __init__(self):
        self.mail = None

    def _build_xoauth2(self, token):
        return (
            b"user=" + USERNAME.encode() +
            b"\x01auth=Bearer " + token.encode() +
            b"\x01\x01"
        )

    def connect(self):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        self.mail = imaplib.IMAP4_SSL(
            IMAP_SERVER,
            IMAP_PORT,
            ssl_context=context
        )

    def authenticate(self, access_token):
        self.mail.authenticate(
            "XOAUTH2",
            lambda x: self._build_xoauth2(access_token)
        )

    def select_inbox(self):
        return self.mail.select("INBOX")

    def search_all(self):
        return self.mail.search(None, "ALL")

    def logout(self):
        if self.mail:
            self.mail.logout()