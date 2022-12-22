# -*- coding: UTF-8 -*-
"""Module Domoticz JSON/API:Plan"""

# standard libs
from __future__ import annotations

from dataclasses import dataclass
from enum import IntFlag, auto
from typing import Any, Dict, List, Optional
from urllib.parse import quote

# plugin libs
from app.plan import http
from Domoticz import Connection
from domoticz.responses import OnConnectResponse as OCTR
from domoticz.responses import OnDisconnectResponse as ODTR
from domoticz.responses import OnMessageResponse as OMER
from helpers import debug, error, log_func, status
from helpers.plugin_config import PluginConfig

# pylint:disable=invalid-name


@dataclass
class PlanDatas:
    """PlanDatas"""
    Devices: int
    Name: str
    Order: str
    idx: str


class PlanSteps(IntFlag):
    """Plans steps"""
    GET_PLANS = auto()
    ADD_PLAN = auto()
    ADD_DEVICE = auto()
    DELETE_PLAN = auto()
    FINISHED = auto()


class Plan:
    """Classe Domoticz JSON/API:Plan"""
    HEADERS = {
        'Accept': 'application/json',
        'Accept-Charset': 'utf-8',
        'Accept-Encoding': 'gzip',
        'Connection': 'keep-alive',
        'Host': '127.0.0.1',
        'User-Agent': f'Domoticz/{PluginConfig.domoticz_version}'
    }

    def __init__(self: Plan) -> None:
        """initialisation de la classe"""
        self._devices = set()
        self._finished = False
        self._con: Optional[Connection] = None
        self._plan_id = 0
        self.plan_name = ""

    def on_start(self: Plan, parameters: Dict[str, Any]) -> None:
        """on_start"""
        self.plan_name = parameters.get('Mode1')
        if self.plan_name:
            self._con = Connection(
                self.plan_name + '_API_PLAN',
                'TCP/IP',
                'HTTP',
                Address='127.0.0.1',
                Port='8080'
            )
            # FIXME: UNCOMMENT to continue Dev
            self._con.Connect()

    def on_connect(self: Plan, octr: OCTR) -> None:
        """on_connect"""
        status('<Plan.on_connect>', octr, octr.connection.Name)
        if self._check_con(octr.connection):
            status('API plan connection successfull!')
            if self._plan_id == 0:
                # TODO: (1) - retrive plan_id
                # Headers = {"Connection": "keep-alive", "Accept": "Content-Type: text/html; charset=UTF-8"}
                # myConn.Send({"Verb":"GET", "URL":"/page.html", "Headers": Headers})
                self._con.Send(
                    {
                        'Verb': 'GET',
                        'URL': '/json.htm?type=plans',
                        'Headers': self.HEADERS
                    }
                )

    def on_disconnect(self: Plan, odtr: ODTR) -> None:
        """on_disconnect"""
        if self._check_con(odtr.connection):
            if not self._finished:
                self._con.Connect()

    def on_message(self: Plan, omer: OMER) -> None:
        """on_message"""
        if self._check_con(omer.connection):
            http_response = http.Response(**omer.data)
            if http_response.Status == '200':
                http_datas = http_response.datas
                self._call_response(http_datas)
            else:
                error(f'Http error: {http_response.Status}')

    def add_device(self: Plan, device_list: List[int]) -> None:
        """set_device_list
        @arg device_list (List[int]): liste des device idx de Domoticz
        """
        self._devices.update(device_list)

    def del_device(self: Plan, device_id: int) -> None:
        """del_device"""
        # TODO: (latest) - remove device from plan
        self._devices.discard(device_id)

    def _check_con(self: Plan, connection: Connection) -> bool:
        """_check_con"""
        if connection is self._con:
            if self._con.Connected():
                return True
        return False

    # region -> on_messages private methods
    def _call_response(self: Plan, http_datas: http.HData) -> None:
        """_call_response"""
        if http_datas.status == 'OK':
            method_name = '_'+http_datas.title.lower()
            if hasattr(self, method_name):
                getattr(self, method_name)(http_datas)
            else:
                error(
                    f'<Plan._call_response> Unknown methods: {method_name}',
                    http_datas.result
                )
        else:
            error(
                f'<Plan._call_response> Data error: ({http_datas.status}){http_datas.title}',
                http_datas.result
            )

    def _plans(self: Plan, http_datas: http.HData) -> None:
        """_plans"""
        for plan in http_datas.result:
            plan = PlanDatas(**plan)
            if plan.Name == self.plan_name:
                self._plan_id = plan.idx
                status(
                    f'Plan id acquired: ({self._plan_id}){plan.Name}'
                )
                break
        # if plan_id not found then create
        if self._plan_id == 0:
            self._con.Send(
                {
                    'Verb': 'GET',
                    "URL": f'/json.htm?name={quote(self.plan_name)}&param=addplan&type=command',
                    'Headers': self.HEADERS
                }
            )

    # endregion
