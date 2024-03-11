import os
import pytest
import requests.api as requests
import httpx._api as httpx
from requests import Response as RequestsResponse
from yarl import URL

from typing import Literal
from _pytest.monkeypatch import MonkeyPatch
from json import dumps

MOCK = os.getenv('MOCK_SWITCH', 'false') == 'true'

class MockedHttp:
    def requests_request(self, method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'], 
                         url: str, **kwargs) -> RequestsResponse:
        """
        Mocked requests.request
        """
        response = RequestsResponse()
        response.url = str(URL(url) % kwargs.get('params', {}))
        response.headers = kwargs.get('headers', {})

        if url == 'http://404.com':
            response.status_code = 404
            response._content = b'Not Found'
            return response
        
        # get data, files
        data = kwargs.get('data', None)
        files = kwargs.get('files', None)

        if data is not None:
            resp = dumps(data).encode('utf-8')
        if files is not None:
            resp = dumps(files).encode('utf-8')
        else:
            resp = b'OK'

        response.status_code = 200
        response._content = resp
        return response

    def httpx_request(self, method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'], 
                      url: str, **kwargs) -> httpx.Response:
        """
        Mocked httpx.request
        """
        response = httpx.Response()
        response.url = str(URL(url) % kwargs.get('params', {}))
        response.headers = kwargs.get('headers', {})

        if url == 'http://404.com':
            response.status_code = 404
            response.content = b'Not Found'
            return response
        
        # get data, files
        data = kwargs.get('data', None)
        files = kwargs.get('files', None)

        if data is not None:
            resp = dumps(data).encode('utf-8')
        if files is not None:
            resp = dumps(files).encode('utf-8')
        else:
            resp = b'OK'

        response.status_code = 200
        response.content = resp
        return response

@pytest.fixture
def setup_http_mock(request, monkeypatch: MonkeyPatch):
    if not MOCK:
        yield
        return

    monkeypatch.setattr(requests, "request", MockedHttp.requests_request)
    monkeypatch.setattr(httpx, "request", MockedHttp.httpx_request)
    yield
    monkeypatch.undo()