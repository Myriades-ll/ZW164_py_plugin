# -*- coding: UTF-8 -*-
"""Module Domoticz JSON/API:Plan"""

# standard libs
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntFlag, auto
from gzip import decompress
from json import loads
from typing import Any, Dict, List, Optional

# plugin libs
from Domoticz import Connection
from helpers import debug

# pylint:disable=invalid-name


@dataclass
class PlanDatas:
    """PlanDatas"""
    Devices: int
    Name: str
    Order: str
    idx: str


@dataclass
class HTTPData:
    """HTTPData"""
    raw_data: bytes
    encoded: str
    result: list = field(default_factory=list, init=False)
    status: str = field(default_factory=str, init=False)
    title: str = field(default_factory=str, init=False)

    def __post_init__(self: HTTPData) -> None:
        """post init"""
        tmp = self.raw_data
        if self.encoded == 'gzip':
            tmp = decompress(tmp)
        results: Dict[str, Any] = loads(tmp)
        for key, value in results.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class HTTPHeaders:
    """HTTPHeaders
    TypeError: __init__() missing 6 required positional arguments:
    'Access_Control_Allow_Origin',
    'Cache_Control',
    'Connection',
    'Content_Encoding',
    'Keep_Alive',
    'Pragma'
    """
    Access_Control_Allow_Origin: str  # '*',
    Cache_Control: str  # 'no-cache',
    Connection: str  # 'Keep-Alive',
    Content_Length: str  # '401',
    Content_Type: str  # 'application/json;charset=UTF-8',
    Keep_Alive: str  # 'max=20, timeout=20'
    Pragma: str  # 'no-cache',
    Content_Encoding: str = field(default_factory=str)  # 'gzip',


@dataclass
class HTTPResponse:
    """HTTPResponse"""
    Data: bytes
    Headers: Dict[str, Any]
    Status: str
    datas: HTTPData = field(default=None, init=False)
    headers: HTTPHeaders = field(default=None, init=False)

    def __post_init__(self: HTTPResponse) -> None:
        """post init"""
        if self.Status == '200':
            tmp = {}
            for old_key, value in self.Headers.items():
                new_key = old_key.replace('-', '_')
                tmp.update({new_key: value})
            self.headers = HTTPHeaders(**tmp)
            self.datas = HTTPData(
                raw_data=self.Data,
                encoded=self.headers.Content_Encoding
            )
        else:
            debug(f'<HTTPResponse.__post_init__> Status: {self.Status}')
            debug(f'<HTTPResponse.__post_init__> Headers: {self.Headers}')
            debug(f'<HTTPResponse.__post_init__> Data: {self.Data}')

# pylint:enable=invalid-name


class PlanSteps(IntFlag):
    """Plans steps"""
    GET_PLANS = auto()
    ADD_PLAN = auto()
    ADD_DEVICE = auto()
    DELETE_PLAN = auto()
    FINISHED = auto()


class Plan:
    """Classe Domoticz JSON/API:Plan"""

    def __init__(self: Plan) -> None:
        """initialisation de la classe"""
        self._devices = set()
        self._finished = False
        self._con: Optional[Connection] = None
        self._plan_id = 0

    def on_start(self: Plan) -> None:
        """on_start"""
        self._con = Connection("DOM_API", 'HTTP', 'Protocol')

    def on_connect(self: Plan) -> None:
        """on_connect"""

    def on_disconnect(self: Plan) -> None:
        """on_disconnect"""
        if isinstance(self._con, Connection):
            if not self._finished:
                self._con.Connect()

    def on_message(self: Plan) -> None:
        """on_message"""

    def set_device_list(self: Plan, device_list: List[int]) -> None:
        """set_device_list
        @arg device_list (List[int]): liste des device idx de Domoticz
        """
        self._devices.update(device_list)
