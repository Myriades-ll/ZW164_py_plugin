#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Freebox Python Plugin
"""Module FreeBox application settings"""

# standard libs
from __future__ import annotations

from typing import Any, Dict, Union

# Domoticz lib
import Domoticz
# helpers libs
from helpers.common import debug, error


class AppConfig:
    """Classe de définition des propriétés

    Always use this class to extend your own app_config_class

    see: https://github.com/Myriades-ll/FreeBox/blob/Dev/freebox/app_config.py

    Important: don't forget the __enter__ and __exit__ methods
    """

    def __init__(self: AppConfig) -> None:
        """Initialisation de la classe"""
        self._config = {}

    def _refresh(self: AppConfig) -> None:
        """Mise à jour config interne"""
        self._config = Domoticz.Configuration()

    def _update_domoticz(self: AppConfig) -> None:
        """Mise à jour de la configuration Domoticz"""
        Domoticz.Configuration(self._config)

    def __str__(self: AppConfig) -> str:
        """Wrapper pour str()"""
        return f'{self.__repr__()}{self._config}'

    def __repr__(self: AppConfig) -> str:
        """Wrapper pour repr()"""
        return f"<class 'AppConfig' @{hex(id(self)).lower()}>"

    def __enter__(self: AppConfig) -> AppConfig:
        """with wrapper"""
        self._refresh()
        return self

    def __exit__(self: AppConfig, exc_type, exc_value, traceback) -> None:
        """with exit wrapper"""
        self._update_domoticz()

    @property
    def device_mapping(self: AppConfig) -> dict:
        """Renvoie le device_mapping"""
        # set default value if not exists
        if 'device_mapping' not in self._config:
            self._config.update({'device_mapping': {}})
        return self._config['device_mapping']

    @device_mapping.setter
    def device_mapping(self: AppConfig, value: Dict[str, Any]) -> None:
        """Positionne le device_mapping sur sa valeur"""
        if not isinstance(value, dict):
            raise TypeError(
                f'value doit être du type dict; pas {type(value)}'
            )
        # debug(f'Mise à jour - device_mapping: {type(value)}{value}')
        # Mise à jour interne
        self._config.update({'device_mapping': value})

    @property
    def plan_id(self: AppConfig) -> int:
        """Renvoie le plan_id"""
        # set default value if not exists
        if 'plan_id' not in self._config:
            self._config.update({'plan_id': 0})
        return int(self._config['plan_id'])

    @plan_id.setter
    def plan_id(self: AppConfig, value: Union[int, str]) -> None:
        """positionne le plan_id"""
        # type check
        try:
            assert type(value) in (int, str)
        except AssertionError as exc:
            error(exc)
        else:
            # convert str to int
            if isinstance(value, str):
                value = int(value)
            # Mise à jour interne
            debug(f'Mise à jour - plan_id: {type(value)}{value}')
            self._config.update({'plan_id': value})
