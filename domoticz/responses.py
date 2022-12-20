"""Domoticz responses"""

# standards libs
from __future__ import annotations

from dataclasses import dataclass, field

# app libs
import Domoticz


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
