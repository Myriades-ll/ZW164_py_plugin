# -*- coding: UTF-8 -*-
"""Module Domoticz JSON/API:Plan"""

# standard libs
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import quote

# plugin libs
from app.plan import http
from Domoticz import Connection
from domoticz.responses import OnConnectResponse as OCTR
from domoticz.responses import OnDisconnectResponse as ODTR
from domoticz.responses import OnMessageResponse as OMER
from helpers import error, status
from helpers.plugin_config import PluginConfig

# pylint:disable=invalid-name


@dataclass
class GetPlanDevicesData:
    """GetPlanDevicesData"""
    DevSceneRowID: str  # "1034"
    Name: str  # "N32E1: tone"
    devidx: str  # "1034"
    idx: str  # "278"
    order: str  # "284"
    type: int  # 0


@dataclass
class PlanDatas:
    """PlanDatas"""
    Devices: int
    Name: str
    Order: str
    idx: str


class Plan:
    """Classe Domoticz JSON/API:Plan
    This class is intended to be used with your own automation class.
    Use it as a class extension.
    Below you find see a functional automation class.
    """
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
        self._con: Optional[Connection] = None
        self._devices = set()
        self._finished = False
        self._plan_devices = set()
        self._plan_id = 0
        self.plan_name = ""

    def add_device(self: Plan, device_list: Union[List[int], int]) -> None:
        """set_device_list
        @arg device_list (List[int]): liste des device idx de Domoticz
        """
        if isinstance(device_list, int):
            self._finished = False
            self._devices.add(device_list)
            self._connect(self._getplandevices_call)
        elif isinstance(device_list, list):
            self._finished = False
            self._devices.update(device_list)
            self._connect(self._getplandevices_call)
        else:
            error(
                '<Plan.add_device>',
                f'Unknown model datas: ({type(device_list)}){device_list}'
            )

    # region -> private methods
    def _connect(self: Plan, allready_conneted_callback: Optional[Callable] = None) -> None:
        """_connect"""
        if self.plan_name:
            if not self._con.Connected():
                self._con.Connect()
            elif callable(allready_conneted_callback):
                allready_conneted_callback()

    def _check_con(self: Plan, connection: Connection) -> bool:
        """_check_con"""
        if self.plan_name:
            if connection is self._con:
                if self._con.Connected():
                    return True
        return False

    def _call_response(self: Plan, http_datas: http.HData) -> None:
        """_call_response"""
        method_name = '_' + http_datas.title.lower() + '_response'
        if hasattr(self, method_name):
            getattr(self, method_name)(http_datas)
        else:
            error(
                f'<Plan._call_response> Unknown method: {method_name}',
                http_datas.result
            )

    def _plans_call(self: Plan) -> None:
        """_plans_call
        # Headers = {"Connection": "keep-alive", "Accept": "Content-Type: text/html; charset=UTF-8"}
        # myConn.Send({"Verb":"GET", "URL":"/page.html", "Headers": Headers})
        """
        self._con.Send(
            {
                'Verb': 'GET',
                'URL': '/json.htm?type=plans',
                'Headers': self.HEADERS
            }
        )

    def _plans_response(self: Plan, http_datas: http.HData) -> None:
        """_plans_response"""
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
            self._addplan_call()
        else:
            self._getplandevices_call()

    def _addplan_call(self: Plan) -> None:
        """_addplan_call"""
        self._con.Send(
            {
                'Verb': 'GET',
                "URL": f'/json.htm?name={quote(self.plan_name)}&param=addplan&type=command',
                'Headers': self.HEADERS
            }
        )
        status(f'Creating plan {self.plan_name}')

    def _addplan_response(self: Plan, _http_datas: http.HData) -> None:
        """_addplan"""
        self._plans_call()

    def _deleteplan_call(self: Plan) -> None:
        """_deleteplan_call
        /json.htm?idx=<plan_id>&param=deleteplan&type=command
        """
        self._con.Send(
            {
                'Verb': 'GET',
                "URL": f'/json.htm?idx={self._plan_id}&param=deleteplan&type=command',
                'Headers': self.HEADERS
            }
        )

    def _deleteplan_response(self: Plan, _http_datas: http.HData) -> None:
        """_deleteplan_response"""
        self._plan_id = 0
        status(f'Plan deleted {self.plan_name}')

    def _addplanactivedevice_call(self: Plan) -> None:
        """_addplanactivedevice_add
        /json.htm?activeidx=1034&activetype=0&idx=21&param=addplanactivedevice&type=command
        """
        next_devices = self._devices - self._plan_devices
        if len(next_devices) > 0:
            self._con.Send(
                {
                    'Verb': 'GET',
                    "URL": ''.join([
                        f'/json.htm?activeidx={min(next_devices)}',
                        f'&activetype=0&idx={self._plan_id}',
                        '&param=addplanactivedevice&type=command'
                    ]),
                    'Headers': self.HEADERS
                }
            )
        else:  # finished
            self._finished = True
            self._con.Disconnect()
            if self._devices == self._plan_devices and len(self._plan_devices) > 0:
                status(f'All devices added to {self.plan_name} location')

    def _addplanactivedevice_response(self: Plan, _http_datas: http.HData) -> None:
        """_addplanactivedevice_response"""
        self._getplandevices_call()

    def _getplandevices_call(self: Plan) -> None:
        """_getplandevices_call
        /json.htm?idx=21&param=getplandevices&type=command
        """
        self._con.Send(
            {
                'Verb': 'GET',
                "URL": f'/json.htm?idx={self._plan_id}&param=getplandevices&type=command',
                'Headers': self.HEADERS
            }
        )

    def _getplandevices_response(self: Plan, http_datas: http.HData) -> None:
        """_getplandevices_response"""
        for item in http_datas.result:
            datas = GetPlanDevicesData(**item)
            devidx = int(datas.devidx)
            if devidx not in self._plan_devices:
                self._plan_devices.add(int(devidx))
        self._addplanactivedevice_call()
    # endregion


class PlanAutomation(Plan):
    """Automation for domoticz location"""

    def __init__(self: PlanAutomation) -> None:
        """initialisation de la classe"""
        Plan.__init__(self)

    def on_start(self: PlanAutomation, parameters: Dict[str, Any]) -> None:
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
            self._connect()
        else:
            status("No plan! Don't forget to add your devices.")

    def on_connect(self: PlanAutomation, octr: OCTR) -> None:
        """on_connect"""
        if self._check_con(octr.connection):
            status('API plan connection successfull!')
            if self._plan_id == 0:
                self._plans_call()
            else:
                self._getplandevices_call()

    def on_disconnect(self: PlanAutomation, odtr: ODTR) -> None:
        """on_disconnect"""
        if self._check_con(odtr.connection):
            if not self._finished:
                self._con.Connect()

    def on_message(self: PlanAutomation, omer: OMER) -> None:
        """on_message"""
        if self._check_con(omer.connection):
            http_response = http.Response(**omer.data)
            if http_response:
                http_datas = http_response.datas
                if http_datas:
                    self._call_response(http_datas)
