from typing import Optional

import requests
import json

import param

from typing import Optional, List

import requests
from requests import Request, Session
import json

import param


class API(param.Parameterized):
    ip = param.String("localhost")
    port = param.Integer(7410)
    headers = {"Content-Type": "application/json", "charset": "utf-8"}

    @property
    def api_url(self) -> str:
        url = f"http://{self.ip}:{self.port}/api"
        return url

    @property
    def tags_url(self):
        return f"{self.api_url}/tags/"

    @property
    def tag_values_url(self):
        return f"{self.api_url}/tag/values"

    @property
    def tag_values_by_name_url(self):
        return f"{self.tag_values_url}/by-name"

    def request_tags(
        self, name: Optional[str] = None, type: Optional[str] = None, kind: Optional[str] = None
    ):
        payload = {}
        if name is not None:
            payload["name"] = name
        if type is not None:
            payload["type"] = type
        if kind is not None:
            payload["kind"] = kind
        return requests.get(self.tags_url, params=payload)

    def request_tags_id(self, id: str):
        return requests.get(f"{self.tags_url}/{id}")

    def request_get_tag_values(self, url, data):
        s = Session()
        req = Request("GET", url, json=data, headers=self.headers)
        prepped = s.prepare_request(req)
        settings = s.merge_environment_settings(prepped.url, {}, None, None, None)
        resp = s.send(prepped, **settings)
        return resp

    def get_tags(
        self,
        name: Optional[str] = None,
        type: Optional[str] = None,
        kind: Optional[str] = None,
        id: Optional[str] = None,
    ):
        if id is None:
            resp = self.request_tags(name=name, type=type, kind=kind)
        else:
            resp = self.request_tags_id(id=id)
        values = resp.json()
        return values

    def get_tag_values(self, ids: Optional[List[str]] = None, names: Optional[str] = None):
        if ids is not None:
            response = self.request_get_tag_values(url=self.tag_values_url, data=ids)
        else:
            response = self.request_get_tag_values(url=self.tag_values_by_name_url, data=names)
        return response.json()

    def set_tag_values(self, data: List[str]):
        url = self.tag_values_url if "id" in data[0] else self.tag_values_by_name_url
        res = requests.put(url, data=json.dumps(data), headers=self.headers)
        if res.status_code != 200:
            raise ValueError(f"Response returned status code {res.status_code}: {res.content}")
