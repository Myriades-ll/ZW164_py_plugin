#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module Domoticz JSON/API:Plan"""

# standard libs
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntFlag, auto
from gzip import decompress
from json import loads
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote

# local libs
from domoticz.responses import OnMessageResponse as OMER
from helpers import api
from helpers.app_config import AppConfig
from helpers.common import debug, error, status
from helpers.decorators import log_func
from helpers.requests import RequestMethod, RequestRequest


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
    """Création du plan pour les devices
    /json.htm?name=ZW164&param=addplan&type=command
    """
    _urls = {
        "plans": "/json.htm?type=plans",
        "addplan": "/json.htm?name={}&param=addplan&type=command",
        "addplanactivedevice": [
            "/json.htm?",
            "activeidx={}&",  # device_id
            "activetype=0&",
            "idx={}&",  # plan_id
            "param=addplanactivedevice&type=command"
        ],
        "deleteplan": "json.htm?idx={}&param=deleteplan&type=command"
    }
    _request_list = [
        'Plans',
        'addplan',
        'addplanactivedevice'
    ]

    def __init__(self: Plan, plan_name: str) -> None:
        """Initialisation de la classe"""
        self._plan_name = plan_name
        self._step = PlanSteps.GET_PLANS
        self._device_list = []
        self._api_request = api.API_REQUEST

    def __bool__(self: Plan) -> bool:
        """bool() wrapper"""
        return bool(self._step & PlanSteps.FINISHED)

    def create(self: Plan) -> None:
        """Création du plan"""
        self._api_request.connect()

    def delete(self: Plan) -> None:
        """Delete plan
        /json.htm?idx=<plan_id>&param=deleteplan&type=command
        """
        self._step = PlanSteps.DELETE_PLAN
        with AppConfig() as app_config:
            request = RequestRequest(
                'Delete plans',
                self._urls['deleteplan'].format(app_config.plan_id),
                RequestMethod.GET
            )
        self._api_request.add(request)
        self._api_request.send()

    @log_func('debug', True, True)
    def next_step(self: Plan) -> None:
        """Execute next step to check Domoticz plan
        #ignore_self_arg
        """
        debug(f'Cur step: {repr(self._step)}')
        if self._step & PlanSteps.GET_PLANS:
            request = RequestRequest(
                'Get plans',
                self._urls['plans'],
                RequestMethod.GET
            )
            self._api_request.add(request)
            self._api_request.send()
        elif self._step & PlanSteps.ADD_PLAN:
            request = RequestRequest(
                'Add plan',
                (self._urls['addplan']).format(quote(self._plan_name)),
                RequestMethod.GET
            )
            self._api_request.add(request)
            self._api_request.send()
        elif self._step & PlanSteps.ADD_DEVICE:
            self._process_add_device()

    def message(self: Plan, omer: OMER) -> None:
        """Réception des données"""
        http_reponse = HTTPResponse(**omer.data)
        # retrieve plan list
        if self._step & PlanSteps.GET_PLANS:
            for plan in http_reponse.datas.result:
                plan_datas = PlanDatas(**plan)
                if plan_datas.Name == self._plan_name:
                    with AppConfig() as app_config:
                        app_config.plan_id = plan_datas.idx
                        status(f'Plan ID ({app_config.plan_id}) acquired!')
                    self._step = PlanSteps.FINISHED
                    return
            self._step = PlanSteps.ADD_PLAN
            self.next_step()
        elif self._step & PlanSteps.ADD_PLAN:
            debug(f'<PLan.message> {omer}')
            self._step = PlanSteps.GET_PLANS
            self.next_step()
        # we can perform any other actions
        elif self._step & PlanSteps.ADD_DEVICE:
            self.add_device()
        # delete plan
        elif self._step & PlanSteps.DELETE_PLAN:
            self._step = PlanSteps.FINISHED

    def add_device(self: Plan, device_ids: Optional[Union[int, List[int]]] = None) -> None:
        """Ajoute un device au plan"""
        with AppConfig() as app_config:
            if app_config.plan_id > 0:
                self._step = PlanSteps.ADD_DEVICE
                # add device_ids to device_list for future usage
                if isinstance(device_ids, list):
                    self._device_list.extend(device_ids)
                elif isinstance(device_ids, int):
                    self._device_list.append(device_ids)
                self._process_add_device()
            else:
                error('<Plan.add_device> Plan id not acquired!')

    def _process_add_device(self: Plan) -> None:
        """_process_add_device"""
        # get next device_id
        try:
            device_id = self._device_list.pop()
        except IndexError:
            self._step = PlanSteps.FINISHED
        else:
            with AppConfig() as app_config:
                base_url = "".join(self._urls.get('addplanactivedevice'))
                base_url = base_url.format(device_id, app_config.plan_id)
                debug(base_url)
                request = RequestRequest(
                    'Add device to plan',
                    base_url,
                    RequestMethod.GET
                )
                self._api_request.add(request)
                self._api_request.send()
