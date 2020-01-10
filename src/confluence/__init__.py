import requests
import json
from pathlib import Path

class Confluence(object):

    def __init__(self, api_url, username, password):
        self.basic_auth = (username, password)
        self.api_url = api_url