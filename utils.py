__author__ = 'ritesh'
"""
Nicked from : http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
"""
import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

class PrettyPrint:
    @staticmethod
    def ratelimit(r, api_name, api_url):
        """
        Pretty print the twitter rate limit
        """
        reset = r['resources'][api_name][api_url]['reset']
        remaining= r['resources'][api_name][api_url]['remaining']
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reset))
        print "We have %d calls left until %s" % (remaining, t)
        return {'remaining': remaining, 'reset': reset}
