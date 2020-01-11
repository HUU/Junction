from junction.confluence.models import (
    Content,
    ContentArray,
    UpdateContent,
    CreateContent,
)

BASE_PATH = "content"


class ContentApi(object):
    def __init__(self, api_client):
        self.__api_client = api_client

    def add_content(self, content: CreateContent, **kwargs):
        self.__api_client.post(BASE_PATH, body=content, **kwargs)

    def update_content(self, content_id: str, content: UpdateContent, **kwargs):
        self.__api_client.put(f"{BASE_PATH}/{content_id}", body=content, **kwargs)

    def delete_content(self, content_id: str, **kwargs):
        self.__api_client.delete(f"{BASE_PATH}/{content_id}", **kwargs)

    def get_content(
        self,
        type: str = None,
        space_key: str = None,
        title: str = None,
        status: str = None,
        posting_day: str = None,
        expand: str = None,
        trigger: str = None,
        start: int = 0,
        limit: int = 25,
        **kwargs,
    ):
        query_params = {
            "type": type,
            "spaceKey": space_key,
            "title": title,
            "status": status,
            "postingDay": posting_day,
            "expand": expand,
            "trigger": trigger,
            "start": start,
            "limit": limit,
        }

        if "query_params" in kwargs:
            query_params.update(kwargs["query_params"])
            del kwargs["query_params"]

        response = self.__api_client.get(
            BASE_PATH,
            query_params={k: v for k, v in query_params.items() if v is not None},
            **kwargs,
        )
        return self.__api_client.decode(response.text, ContentArray)

    def get_content_by_id(self, content_id: str, **kwargs):
        response = self.__api_client.get(f"{BASE_PATH}/{content_id}", **kwargs)
        return self.__api_client.decode(response.text, Content)
