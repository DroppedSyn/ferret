import settings
import psycopg2
import re
import binascii
import os
import utils
import tasks


class DmCommandHandler():
    def __init__(self, messages):
        self.messages = messages
        self.conn = psycopg2.connect(settings.PGDBNAME)
        self._parse_messages()

    def _parse_messages(self):
        # TODO: Rewrite this to parse more commands
        for message in self.messages:
            command = message.text.strip().lower()
            # For verifying users functionality
            match = re.search(r"i am +", command)
            if match is not None:
                email = re.sub(r'i am +', '', command)
                twitter_handle = message.sender.screen_name
                # DEBUG
                print "%s says they are %s@cigital.com" % (twitter_handle, email)
                print email, twitter_handle
                tasks.link_user.delay(email, twitter_handle)
            else:
                # Check if we have authcode
                match = re.search(r"^(?!0{8}).{8}$", command)
                if match is not None:
                    code = match.group(0)
                    tasks.check_auth_code.delay(message.sender.screen_name, code)


