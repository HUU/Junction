import requests
from urllib.parse import urlencode, urljoin

from junction.confluence.api.content_api import ContentApi
from junction.confluence.models.json import ApiEncoder, ApiDecoder


class _ApiClient(object):

    default_headers = {
        "X-Atlassian-Token": "no-check",
        "Content-Type": "application/json",
    }

    def __init__(self, api_url, username, password):
        self.basic_auth = (username, password)
        self.api_url = api_url + "/" if not api_url.endswith("/") else api_url
        self.__json_encoder = ApiEncoder()

    def decode(self, s, klass):
        return ApiDecoder(klass)().decode(s)

    def get(self, resource_path, query_params=None, headers=None, body=None):
        return self.__call_api(
            resource_path, "GET", query_params=query_params, headers=headers, body=body
        )

    def post(self, resource_path, query_params=None, headers=None, body=None):
        return self.__call_api(
            resource_path, "POST", query_params=query_params, headers=headers, body=body
        )

    def put(self, resource_path, query_params=None, headers=None, body=None):
        return self.__call_api(
            resource_path, "PUT", query_params=query_params, headers=headers, body=body
        )

    def delete(self, resource_path, query_params=None, headers=None, body=None):
        return self.__call_api(
            resource_path,
            "DELETE",
            query_params=query_params,
            headers=headers,
            body=body,
        )

    def __call_api(
        self, resource_path, method, query_params=None, headers=None, body=None
    ):

        headers = headers or {}
        headers.update(self.default_headers)

        query_string = f"?{urlencode(query_params)}" if query_params else None
        url = urljoin(urljoin(self.api_url, resource_path), query_string)

        if method == "GET":
            response = requests.get(url, auth=self.basic_auth, headers=headers)
        elif method == "POST":
            response = requests.post(
                url,
                data=self.__json_encoder.encode(body),
                auth=self.basic_auth,
                headers=headers,
            )
        elif method == "PUT":
            response = requests.put(
                url,
                data=self.__json_encoder.encode(body),
                auth=self.basic_auth,
                headers=headers,
            )
        elif method == "DELETE":
            response = requests.delete(url, auth=self.basic_auth, headers=headers)
        else:
            raise NotImplementedError(
                "API client does not support {} method".format(method)
            )

        response.raise_for_status()

        return response


class Confluence(object):
    def __init__(self, api_url, username, password):
        self.__api_client = _ApiClient(api_url, username, password)
        self.content = ContentApi(self.__api_client)
