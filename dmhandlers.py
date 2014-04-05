from tweepy import API
from settings import list_of_people

class DMHandler():
    def __init__(self, auth):
        self.auth = auth
        self.api = API(self.auth)

    def check_if_follows(self, screen_name=None):
        """
        Check if we follow a bunch of people, if not, send a DM
        """
        if screen_name == None:
            return
        out = {}
        for person in list_of_people:
            # This returns two friendship object, the first one tells us if source follows target
            # and the second one tells us if target follows source. We're only interested in the
            # first for now.
            output = self.api.show_friendship(source_screen_name=screen_name, target_screen_name=person)
            for item in output:
                if item.screen_name == screen_name:
                    out[person] = item.following
        return out





    def send_dm(self, screen_name = None, id = None, message = None):
        pass


