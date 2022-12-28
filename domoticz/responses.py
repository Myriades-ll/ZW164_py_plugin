"""Domoticz responses"""

# standards libs
from __future__ import annotations

from dataclasses import dataclass, field
from sys import modules
from typing import Any, Callable

# app libs
import Domoticz
import helpers

__all__ = [
    'on_event',
    'OnCommandResponse',
    'OnConnectResponse',
    'OnDeviceAddedResponse',
    'OnDeviceModifiedResponse',
    'OnDeviceRemovedResponse',
    'OnDisconnectResponse',
    'OnMessageResponse',
    'OnNotificationResponse',
    'OnSecurityEventResponse',
    'OnTimeoutResponse'
]


@dataclass
class BaseConnectionReponse:
    """BaseConnectionReponse"""
    connection: Domoticz.Connection


@dataclass
class OnDisconnectResponse(BaseConnectionReponse):
    """OnDisconnectResponse"""


@dataclass
class OnConnectResponse(BaseConnectionReponse):
    """OnConnectResponse"""
    status: int
    description: str

    def is_success(self: OnConnectResponse) -> bool:
        """is connection successfull
        @return True if `success`, else `False`
        """
        return not self.status


@dataclass
class OnMessageResponse(BaseConnectionReponse):
    """OnMessageResponse"""
    data: dict = field(default_factory=dict)


@dataclass
class OnTimeoutResponse(BaseConnectionReponse):
    """OnTimeoutResponse"""


@dataclass
class OnNotificationResponse:
    """OnNotificationResponse"""
    name: str
    subject: str
    text: str
    status: int
    priority: int
    sound: str
    imagefile: str


@dataclass
class BaseDeviceReponse:
    """BaseDeviceReponse"""
    unit: int


@dataclass
class OnDeviceAddedResponse(BaseDeviceReponse):
    """OnDeviceAddedResponse"""


@dataclass
class OnCommandResponse(BaseDeviceReponse):
    """OnCommandResponse"""
    command: str
    level: int = field(default_factory=int)
    color: dict = field(default_factory=dict)


@dataclass
class OnDeviceModifiedResponse(BaseDeviceReponse):
    """onDeviceModifiedResponse"""


@dataclass
class OnDeviceRemovedResponse(BaseDeviceReponse):
    """onDeviceModifiedResponse"""


@dataclass
class OnSecurityEventResponse(BaseDeviceReponse):
    """onDeviceModifiedResponse"""
    level: int
    description: str


def on_event(func: Callable) -> Any:
    """This is a decorator"""

    def inner(*args: tuple, **_kwargs: dict) -> Any:
        """the inner func"""
        func_name: str = func.__name__
        class_name = func_name[0].upper() + func_name[1:] + 'Response'
        helpers.debug(modules.get('domoticz'))
        class_ = getattr(modules.get('domoticz'), class_name)
        helpers.debug(class_)
        if class_ is not None:
            return func(class_(*args))
        return func(*args)

    return inner
