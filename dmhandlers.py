from tweepy import API
from settings import LIST_OF_PEOPLE
from commands import COMMANDS


class DmCommandHandler():
    def __init__(self, auth):
        self.auth = auth
        self.api = API(self.auth)
        self.commands = {
            "check me out": self.__check_if_follows,
            "i am": self.__verify_user,
        }

    def handle_dm_command(self, message):
        command = message.text.strip().lower()
        print "Command", command
        try:
            self.commands[command](message)
        except KeyError:
            print "No idea what what %s is meant to do." %s

    def __check_if_follows(self, message):
        """
        Check if screen_name follows the users we want (defined in settings)
        """
        if message.sender.screen_name is None:
            return
        out = {}
        for person in LIST_OF_PEOPLE:
            # This returns two friendship object, the first one tells us if source follows target
            # and the second one tells us if target follows source. We're only interested in the
            # first for now.
            output = self.api.show_friendship(source_screen_name=message.sender.screen_name,
                                              target_screen_name=person)
            for item in output:
                if item.screen_name == message.sender.screen_name:
                    out[person] = item.following
        print out
        return out

    def __verify_user(self, direct_message=None, email_verified=False):
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

    def send_dm(self, screen_name=None, message=None):
        pass
