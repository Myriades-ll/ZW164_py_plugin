#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module Domoticz JSON/API:Plan"""

# standard libs
from __future__ import annotations
from enum import IntFlag, auto
from typing import List, Optional, Union
from urllib.parse import quote
from dataclasses import dataclass

# local libs
from helpers.app_config import AppConfig
from helpers.common import debug, error, status
from helpers.requests import (RequestMethod, RequestRequest,
                              RequestResponse)
from helpers import api
# from domoticz.responses import OnMessageResponse as OMER


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
    """Création du plan pour les devices"""
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

    def next_step(self: Plan) -> None:
        """Execute next step to check Domoticz plan"""
        debug(f'Cur step: {self._step}')
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

    def message(self: Plan, reponse: RequestResponse) -> None:
        """Réception des données"""
        # retrieve plan list
        if self._step & PlanSteps.GET_PLANS:
            for plan in reponse.datas:
                debug(plan)
                plan_datas = PlanDatas(**plan)
                debug(plan_datas)
                if plan.get('Name', '') == self._plan_name:
                    with AppConfig() as app_config:
                        app_config.plan_id = plan.get('idx')
                        status(f'Plan ID ({app_config.plan_id}) acquired!')
                    self._step = PlanSteps.FINISHED
                    return
            self._step = PlanSteps.ADD_PLAN
            self.next_step()
        #
        elif self._step & PlanSteps.ADD_PLAN:
            debug(reponse)
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
                error('Plan id not acquired!')

    def _process_add_device(self: Plan) -> None:
        """"""
        # get next device_id
        try:
            device_id = self._device_list.pop()
        except IndexError:
            self._step = PlanSteps.FINISHED
        else:
            with AppConfig() as app_config:
                base_url = "".join(self._urls.get('addplanactivedevice'))
                base_url = base_url.format(device_id, app_config.plan_id)
                request = RequestRequest(
                    'Add device to plan',
                    base_url,
                    RequestMethod.GET
                )
                self._api_request.add(request)
                self._api_request.send()
