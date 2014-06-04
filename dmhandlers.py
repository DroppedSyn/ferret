import settings
import psycopg2
import re

class DmCommandHandler():
    def __init__(self, messages):
        self.messages = messages
        self.conn = psycopg2.connect(settings.PGDBNAME)
        self._parse_messages()

    def _parse_messages(self):
        command = None
        for message in self.messages:
            command = message.text.strip().lower()
            if re.search(r"^i am", command) is not None:
                i = command.split()
                email = i[2]
                twitter_handle = message.sender.screen_name
                print "TW Handle", twitter_handle
                self.verify_user(email, twitter_handle, email_verified=False)

    @staticmethod
    def verify_user(email, twitter_handle, email_verified=False):
        """
        Allow users to claim twitter IDs
        if they say I am rksinha, then the DM sender is mapped to that twitter ID
        """

        conn = psycopg2.connect(settings.PGDBNAME)
        cur = conn.cursor()
        if email_verified is True:
            cur.execute("UPDATE VERIFIED SET verified = TRUE where twitter_handle = %s", (twitter_handle,))
            conn.commit()
        else:
            cur.execute("SELECT email FROM VERIFIED WHERE email = %s", (email,))
            r = cur.fetchone()
            print r
            if r is not None:
                cur.execute("UPDATE VERIFIED SET twitter_handle = %s WHERE email = %s", (twitter_handle, email,))
                conn.commit()
# Send email to verify
        conn.close()
