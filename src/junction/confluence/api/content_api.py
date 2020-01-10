from junction.confluence.models import Content

BASE_PATH = "content"

class ContentApi(object):

    def __init__(self, api_client):
        self.__api_client = api_client

    def add_content(self, content, **kwargs):
        pass

    def update_content(self, content, **kwargs):
        pass

    def delete_content(self, content_id, **kwargs):
        self.__api_client.delete(f"{BASE_PATH}/{content_id}", **kwargs)

    def get_content(self, **kwargs):
        pass

    def get_content_by_id(self, content_id, **kwargs):
        response = self.__api_client.get(f"{BASE_PATH}/{content_id}", **kwargs)
        return self.__api_client.decode(response.text, Content)
