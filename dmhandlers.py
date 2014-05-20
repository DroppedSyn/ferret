import settings
import psycopg2

class DmCommandHandler():
    def __init__(self, messages):
        self.messages = messages
        self.commands = {
                "check me out": self._check_if_follows,
                "i am": self._verify_user,
                }
        self.conn = psycopg2.connect(settings.PGDBNAME)
        self._parse_messages()

    def _parse_messages(self):
        command = None
        for message in self.messages:
            command = message.text.strip().lower()
            try:
                self.commands[command](message)
            except KeyError:
                print "Not a command, plain ol DM"

    def _check_if_follows(self, message):
        """
        Check if screen_name follows the users we want (defined in settings)
        """
        print "Entering CHECK IF FOLLOWS"
        screen_name = message.sender.screen_name
        print screen_name
        cur = self.conn.cursor()
        cur.execute("SET TIMEZONE='UTC'")
        cur.execute("""INSERT INTO TASKS(name, data, completed, tstamp) VALUES (%s, %s,
                        %s, %s)""", ('checkiffollows', screen_name, 'FALSE', 'NOW()',))
        self.conn.commit()
        #tasks.check_if_follows.delay(message.sender.screen_name)

    def _verify_user(self, direct_message=None, email_verified=False):
        """
        Allow users to claim twitter IDs
        if they say I am rksinha, then the DM sender is mapped to that twitter ID
        Expects a tweepy direct message object
        """
        if direct_message is not None:
            sender = direct_message["sender_screen_name"]
            text = direct_message["text"]
            # Use a regex match, instead of a simple split
            email = text.split()[2]
            # If email not in DB, return False
            # Else map email to twitter ID but mark email verified as False in DB
            # Send verification email
        if email_verified is True:
            # Mark email as verified! They are who they say they are.
            pass
