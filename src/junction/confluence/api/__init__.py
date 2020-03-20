import requests
import logging
from urllib.parse import urlencode, urljoin
from typing import Union, Sequence, Mapping, Any, Tuple, TypeVar, Type

from junction.confluence.models import ApiModel
from junction.confluence.models.json import ApiEncoder, ApiDecoder


logger = logging.getLogger(__name__)


T = TypeVar("T", bound=ApiModel)


class _ApiClient(object):

    default_headers = {
        "X-Atlassian-Token": "no-check",
        "Content-Type": "application/json",
    }

    def __init__(self, api_url: str, username: str, password: str):
        self.basic_auth = (username, password)
        self.api_url = api_url + "/" if not api_url.endswith("/") else api_url
        self.__json_encoder = ApiEncoder()

    def decode(self, s: str, klass: Type[T]) -> T:
        return ApiDecoder(klass).decode(s)

    def get(
        self,
        resource_path: str,
        query_params: Union[
            Mapping[Any, Any],
            Mapping[Any, Sequence[Any]],
            Sequence[Tuple[Any, Any]],
            Sequence[Tuple[Any, Sequence[Any]]],
        ] = None,
        headers: dict = None,
        body: ApiModel = None,
    ) -> requests.Response:
        return self.__call_api(
            resource_path, "GET", query_params=query_params, headers=headers, body=body
        )

    def post(
        self,
        resource_path: str,
        query_params: Union[
            Mapping[Any, Any],
            Mapping[Any, Sequence[Any]],
            Sequence[Tuple[Any, Any]],
            Sequence[Tuple[Any, Sequence[Any]]],
        ] = None,
        headers: dict = None,
        body: ApiModel = None,
    ) -> requests.Response:
        return self.__call_api(
            resource_path, "POST", query_params=query_params, headers=headers, body=body
        )

    def put(
        self,
        resource_path: str,
        query_params: Union[
            Mapping[Any, Any],
            Mapping[Any, Sequence[Any]],
            Sequence[Tuple[Any, Any]],
            Sequence[Tuple[Any, Sequence[Any]]],
        ] = None,
        headers: dict = None,
        body: ApiModel = None,
    ) -> requests.Response:
        return self.__call_api(
            resource_path, "PUT", query_params=query_params, headers=headers, body=body
        )

    def delete(
        self,
        resource_path: str,
        query_params: Union[
            Mapping[Any, Any],
            Mapping[Any, Sequence[Any]],
            Sequence[Tuple[Any, Any]],
            Sequence[Tuple[Any, Sequence[Any]]],
        ] = None,
        headers: dict = None,
        body: ApiModel = None,
    ) -> requests.Response:
        return self.__call_api(
            resource_path,
            "DELETE",
            query_params=query_params,
            headers=headers,
            body=body,
        )

    def __call_api(
        self,
        resource_path: str,
        method: str,
        query_params: Union[
            Mapping[Any, Any],
            Mapping[Any, Sequence[Any]],
            Sequence[Tuple[Any, Any]],
            Sequence[Tuple[Any, Sequence[Any]]],
        ] = None,
        headers: dict = None,
        body: ApiModel = None,
    ) -> requests.Response:

        headers = headers or {}
        headers.update(self.default_headers)

        query_string = f"?{urlencode(query_params)}" if query_params else None
        url = urljoin(urljoin(self.api_url, resource_path), query_string)

        logger.debug("Confluence API call %s %s with headers %s", method, url, headers)

        if method == "GET":
            response = requests.get(url, auth=self.basic_auth, headers=headers)
        elif method == "POST":
            data = self.__json_encoder.encode(body)
            logger.debug(data)
            response = requests.post(
                url, data=data, auth=self.basic_auth, headers=headers,
            )
        elif method == "PUT":
            data = self.__json_encoder.encode(body)
            logger.debug(data)
            response = requests.put(
                url, data=data, auth=self.basic_auth, headers=headers,
            )
        elif method == "DELETE":
            response = requests.delete(url, auth=self.basic_auth, headers=headers)
        else:
            raise NotImplementedError(
                "API client does not support {} method".format(method)
            )

        if response.status_code < 400:
            logger.debug("Confluence API response: %s", response.text)
        else:
            logger.error(
                "Confluence API failure response %s: %s",
                response.status_code,
                response.text,
            )
        response.raise_for_status()

        return response
