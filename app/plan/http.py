# -*- coding: UTF-8 -*-
"""HTTP helpers pour Module Domoticz JSON/API:Plan"""

# standard libs
from __future__ import annotations

from dataclasses import dataclass, field
from gzip import decompress
from json import loads
from typing import Any, Dict

# plugin libs
from helpers import debug, error, status


@dataclass
class HData:
    """HTTPData"""
    raw_data: bytes
    encoded: str
    result: list = field(default_factory=list, init=False)
    status: str = field(default_factory=str, init=False)
    title: str = field(default_factory=str, init=False)

    def __post_init__(self: HData) -> None:
        """post init"""
        status(f'<HData.__post_init__> status: {self.status}')
        tmp = self.raw_data
        if self.encoded == 'gzip':
            tmp = decompress(tmp)
        results: Dict[str, Any] = loads(tmp)
        for key, value in results.items():
            if hasattr(self, key):
                setattr(self, key, value)

# pylint:disable=invalid-name,too-many-instance-attributes


@dataclass
class HHeaders:
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
class Response:
    """HTTPResponse"""
    Data: bytes
    Headers: Dict[str, Any]
    Status: str
    datas: HData = field(default=None, init=False)
    headers: HHeaders = field(default=None, init=False)

    def __post_init__(self: Response) -> None:
        """post init"""
        if self:
            tmp = {}
            for old_key, value in self.Headers.items():
                new_key = old_key.replace('-', '_')
                tmp.update({new_key: value})
            self.headers = HHeaders(**tmp)
            self.datas = HData(
                raw_data=self.Data,
                encoded=self.headers.Content_Encoding
            )
        else:
            error('<HTTPResponse.__post_init__>')
            error(
                Status=self.Status,
                Headers=self.Headers,
                Data=self.Data
            )

    def __bool__(self: Response) -> bool:
        """bool test wrapper"""
        return self.Status == '200'
