from junction.confluence.models import Content, ContentArray

BASE_PATH = "content"

class ContentApi(object):

    def __init__(self, api_client):
        self.__api_client = api_client

    def add_content(self, content, **kwargs):
        self.__api_client.post(BASE_PATH, body=content, **kwargs)

    def update_content(self, content, **kwargs):
        self.__api_client.put(f"{BASE_PATH}/{content.id}", body=content, **kwargs)
        pass

    def delete_content(self, content_id, **kwargs):
        self.__api_client.delete(f"{BASE_PATH}/{content_id}", **kwargs)

    def get_content(self, type=None, space_key=None, title=None, status=None, posting_day=None, expand=None, trigger=None, start=0, limit=25, **kwargs):

        query_params = {
            'type': type,
            'spaceKey': space_key,
            'title': title,
            'status': status,
            'postingDay': posting_day,
            'expand': expand,
            'trigger': trigger,
            'start': start,
            'limit': limit
        }

        if 'query_params' in kwargs:
            query_params.update(kwargs['query_params'])
            del kwargs['query_params']


        response = self.__api_client.get(
            BASE_PATH,
            query_params={k:v for k, v in query_params.items() if v is not None},
            **kwargs)
        return self.__api_client.decode(response.text, ContentArray)

    def get_content_by_id(self, content_id, **kwargs):
        response = self.__api_client.get(f"{BASE_PATH}/{content_id}", **kwargs)
        return self.__api_client.decode(response.text, Content)
