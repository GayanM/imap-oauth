# main.py

from auth import get_access_token
from imap_client import IMAPClient


def main():
    print("🔐 Getting access token...")
    token = get_access_token()
    print("✅ Access token acquired")

    print("🔌 Connecting to IMAP...")
    client = IMAPClient()
    client.connect()

    client.authenticate(token)
    print("✅ IMAP authenticated")

    client.select_inbox()
    status, messages = client.search_all()
    print("📬 Messages:", messages)

    client.logout()


if __name__ == "__main__":
    main()