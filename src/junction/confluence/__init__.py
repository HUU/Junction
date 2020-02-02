from junction.confluence.api import _ApiClient
from junction.confluence.api.content_api import ContentApi


class Confluence(object):
    """A Confluence API client.  Each area of the confluence API is accessed seperately
    via members of this class.
    """

    def __init__(self, api_url: str, username: str, password: str, space_key: str):
        """Initializes an instance of the Confluence class.

        Arguments:
            api_url {str} -- The full URL to the REST API for your wiki, usually https://<something>.atlassian.net/wiki/rest/api
            username {str} -- The username to connect with, usually an e-mail
            password {str} -- The API token to connect with, gathered from https://id.atlassian.com/manage/api-tokens
            space_key {str} -- The space key that all API calls from this client object will target
        """
        self.__api_client = _ApiClient(api_url, username, password)
        self.space_key = space_key
        self.content = ContentApi(self.__api_client, self.space_key)
