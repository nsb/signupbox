import urllib, urllib2
from simplejson import loads

BASE_URL = 'http://rest.nexmo.com/sms'
JSON_END_POINT = BASE_URL + '/json'
XML_END_POINT = BASE_URL + '/xml'

class NexmoError(Exception):
    pass

class Client(object):
    """
    Send SMS using nexmo

    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def send_message(self, text, from_, to):
        data = {
            'username': self.username,
            'password': self.password,
            'text': text,
            'from': from_,
            'to': to,
        }
        response = urllib2.urlopen(JSON_END_POINT, urllib.urlencode(data))
        reply = loads(response.read())
        for m in reply['messages']:
            if m['status'] is not '0':
                raise NexmoError(m['error-text'])
