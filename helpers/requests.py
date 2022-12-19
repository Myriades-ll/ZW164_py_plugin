#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module Requêtes"""

# standard libs
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from gzip import decompress
from json import dumps, loads
from time import sleep
from typing import Dict, List, Optional, Union

# domoticz lib
import Domoticz

# local libs
from helpers.common import debug, error
from helpers.plugin_config import PluginConfig
from helpers.decorators import log_func

CONS_DETAILS = {}


def register_connection(
        name: str, address: str, port: str,
        **kwargs: Dict[str, str]) -> None:
    """Enregistre une nouvelle connection"""
    if name in CONS_DETAILS:
        # raise error?
        return
    CONS_DETAILS.update({
        name: {
            'Address': address,
            'Port': port,
            **kwargs
        }
    })


class BaseRequestsError(Exception):
    """Classe de base pour les exceptions"""


class TargetError(BaseRequestsError):
    """Erreur de fonction cible de remplacement"""

    def __init__(self, message: str) -> None:
        """Initialisation de la classe"""
        BaseRequestsError.__init__(self)
        self._message = message

    def __str__(self) -> str:
        """str() wrapper"""
        return f'Erreur de fonction de destination: {self._message}'

    def __repr__(self) -> str:
        """repr() wrapper"""
        return self.__str__()


class RequestMethod(Enum):
    """Méthode de requête"""
    POST = 'POST'
    GET = 'GET'
    PUT = 'PUT'
    DELETE = 'DELETE'


class RequestResponseHeaders:
    """Analyse des headers de réponse"""

    def __init__(self, headers: Dict[str, str]) -> None:
        """Initialisation de la classe
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Encoding': 'gzip'
        """
        self.charset: Optional[str] = 'UTF-8'
        self.content_type: Optional[str] = None
        if 'Content-Type' in headers:
            tmp: str = headers.get('Content-Type')
            tmp: List[str] = tmp.split(';')
            for item in tmp:
                if 'charset' in item:
                    self.charset = (item.split('='))[1]
                    continue
                self.content_type = item
        self.encoding = headers.get('Content-Encoding', '')

    def __str__(self) -> str:
        """str() wrapper"""
        return f'charset: {self.charset}; encoding: {self.encoding}'

    def __repr__(self) -> str:
        """repr() wrapper"""
        return self.__str__()


class RequestResponseDatas:
    """Analyse des datas de réponse"""

    def __init__(self, headers: Dict[str, str], datas: Dict[str, str]) -> None:
        """Initialisation de la classe"""
        headers = RequestResponseHeaders(headers)
        if headers.encoding == 'gzip':
            datas = decompress(datas)
        if headers.charset is not None:
            datas: str = datas.decode(headers.charset)
        if headers.content_type == 'application/json':
            self._response: dict = loads(datas)
        elif headers.content_type == 'text/html':
            datas_list = datas.split('\n')
            error('Erreur de contenu: {}'.format(datas_list))
            self._response = {}
        # Common APIS
        self.datas: Union[dict, list] = self._response.get('result', None)
        # Domoticz JSON API
        self.success = (self._response.get('status', 'ERR') == 'OK')
        self.title = self._response.get('title', None)
        # Freebox API
        self.success |= bool(self._response.get('success', False))
        self.msg: str = self._response.get('msg', None)
        self.error_code: str = self._response.get('error_code', None)

    def __str__(self) -> str:
        """str() wrapper"""
        return 'réponse: {}'.format(self._response)

    def __repr__(self) -> str:
        """repr() wrapper"""
        return self.__str__()


class RequestResponse:
    """Analyse de la réponse"""

    def __init__(self: RequestResponse, connection: Domoticz.Connection, result: dict) -> None:
        """Initialisation de la classe"""
        self.app_name = connection.Name
        _, headers, datas, *_ = result.values()
        # requête http ok
        tmp = RequestResponseDatas(headers, datas)
        # debug(tmp)
        self.success = tmp.success
        self.datas: Union[dict, list] = tmp.datas
        self.message = tmp.msg
        self.title = tmp.title
        self.error_code = tmp.error_code

    def __str__(self: RequestResponse) -> str:
        """str() wrapper"""
        ret = "RequestResponse('App name': {} - 'Success': {}".format(
            self.app_name,
            self.success
        )
        if not self.success:
            ret += " - 'error_code': {} - 'message': {}".format(
                self.error_code,
                self.message
            )
        ret += ")"
        return ret

    def __repr__(self: RequestResponse) -> str:
        """str() wrapper"""
        return self.__str__()


@dataclass
class RequestRequest:
    """Assistant de mise en forme de requête"""
    action: str
    url: str
    method: RequestMethod
    datas: Optional[dict] = field(default_factory=dict)


class Request:
    """Classe request"""

    def __init__(self: Request, con_name: str) -> None:
        """Initialisation de la classe"""
        self._con_name = con_name
        self._con_details = CONS_DETAILS[self._con_name]
        self.__requests_queue = deque()
        self._con = Domoticz.Connection(
            Name=self._con_name,
            **self._con_details
        )

    @log_func()
    def add(self: Request, input_request: RequestRequest, headers: Optional[dict] = None) -> None:
        """Envoie de la requète
        {"Verb":"GET", "URL":"/page.html", "Headers": {Headers}, Datas: <JSON>}
        """
        base_headers = {
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8',
            'Accept-Encoding': 'gzip',
            'Connection': 'keep-alive',
            'Host': self._con_details['Address'],
            'User-Agent': 'Domoticz/{}'.format(PluginConfig.domoticz_version),
        }
        request = {
            'URL': input_request.url,
            'Verb': input_request.method.name
        }
        # headers
        if isinstance(headers, dict):
            base_headers.update(headers)
        request.update({'Headers': base_headers})
        # datas
        if isinstance(input_request.datas, dict):
            request.update({'Data': dumps(input_request.datas)})
        # debug(request)
        self.__requests_queue.append(request)

    @log_func(callback="str", log_return=True)
    def send(self: Request) -> bool:
        """Envoie des données
        [return]:
            - True if data sended, else False
        """
        if len(self.__requests_queue) > 0:
            request = self.__requests_queue.popleft()
            if self._con.Connected():
                self._con.Send(request)
                return True
            # FIXED: add pause to let time to release all calls
            sleep(0.5)
            self.connect()
        return False

    def auto_send(self: Request) -> None:
        """Parcour de la queue et envoie des données"""
        if self._con.Connected():
            while len(self.__requests_queue) > 0:
                request = self.__requests_queue.popleft()
                self._con.Send(request)
                sleep(0.3)
        else:
            self.connect()

    def connect(self: Request) -> None:
        """Domoticz.Connect() wrapper"""
        self._con.Connect()

    def close(self: Request) -> None:
        """Close connction"""
        if self._con.Connected():
            self._con.Disconnect()

    def is_connected(self: Request) -> bool:
        """Check if con has been opened"""
        return self._con.Connected()

    def listen(self: Request) -> None:
        """Listen() wrapper"""
        self._con.Listen()

    def __str__(self: Request) -> str:
        """Wrapper pour str()"""
        return f"{str(self._con_details)} - queue len: {len(self.__requests_queue)}"

    def __repr__(self: Request) -> str:
        """Wrapper pour repr()"""
        return self.__str__()
