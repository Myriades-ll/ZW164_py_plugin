"""Domoticz responses"""

# standards libs
from __future__ import annotations

from dataclasses import dataclass, field

# app libs
import Domoticz


@dataclass
class OnDisconnectResponse:
    """OnDisconnectResponse"""
    connection: Domoticz.Connection


@dataclass
class OnConnectResponse(OnDisconnectResponse):
    """OnConnectResponse"""
    status: int
    description: str

    def is_success(self: OnConnectResponse) -> bool:
        """is connection successfull
        @return True if `success`, else `False`
        """
        return not self.status


@dataclass
class OnMessageResponse(OnDisconnectResponse):
    """OnMessageResponse"""
    data: dict = field(default_factory=dict)


@dataclass
class OnTimeoutResponse(OnDisconnectResponse):
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
class OnDeviceAddedResponse:
    """OnDeviceAddedResponse"""
    unit: int


@dataclass
class OnCommandResponse(OnDeviceAddedResponse):
    """OnCommandResponse"""
    command: str
    level: int = field(default_factory=int)
    color: dict = field(default_factory=dict)


@dataclass
class OnDeviceModifiedResponse(OnDeviceAddedResponse):
    """onDeviceModifiedResponse"""


@dataclass
class OnDeviceRemovedResponse(OnDeviceAddedResponse):
    """onDeviceModifiedResponse"""


@dataclass
class OnSecurityEventResponse(OnDeviceAddedResponse):
    """onDeviceModifiedResponse"""
    level: int
    description: str
