import settings
import psycopg2
import re
import binascii
import os
import utils

class DmCommandHandler():
    def __init__(self, messages):
        self.messages = messages
        self.conn = psycopg2.connect(settings.PGDBNAME)
        self._parse_messages()

    def _parse_messages(self):
        for message in self.messages:
            command = message.text.strip().lower()
            # For verifying users functionality
            match = re.search(r"i am +", command)
            if match is not None:
                email = re.sub(r'i am +', '', command)
                twitter_handle = message.sender.screen_name
                # DEBUG
                print "%s says they are %s@cigital.com" % (twitter_handle, email)
                self.verify_user(email, twitter_handle)

    @staticmethod
    def verify_user(email, twitter_handle):
        """
        Allow users to claim twitter IDs
        if they say I am rksinha, then the DM sender is mapped to that twitter ID
        """
        conn = psycopg2.connect(settings.PGDBNAME)
        cur = conn.cursor()
        cur.execute("SELECT email FROM VERIFIED WHERE email = %s", (email,))
        r = cur.fetchone()
        if r is not None:
            #random code for auth
            code = binascii.b2a_hex(os.urandom(3))
            # we might have dupe codes!!
            cur.execute("UPDATE VERIFIED SET twitter_handle = %s, CODE = %s WHERE email = %s",
                        (twitter_handle, code, email,))
            conn.commit()
            #send_dm.delay(twitter_handle, "I've sent you a code to claim your Twitter handle, please check your "
             #                             "Cigital email.")
            msg = """Hello %s,\nEither you, or someone claiming to be you asked to verify the twitter handle %s. If you
            own this twitter account, please send a DM to the Cigital Tech Ferret bot with the following code:
            \n
            %s
            """ % (email, twitter_handle, code)
            utils.send_email(email+"@cigital.com", "Your verification code", msg)
        else:
            print "I know nothing about this Cigital account you speak of."
            pass
        conn.close()


    @staticmethod
    def check_auth_code(twitter_handle, authcode):
        """
        :param twitter_handle: The twitter handle we're looking at
        :param authcode:
        :return:
        """
        conn = psycopg2.connect(settings.PGDBNAME)
        cur = conn.cursor()
        cur.execute("SELECT twitter_handle from VERIFIED WHERE authcode = %s", (authcode))
        result = cur.fetchone()
        if result is not None:
            cur.execute("UPDATE VERIFIED SET verified = TRUE where twitter_handle = %s", (twitter_handle,))