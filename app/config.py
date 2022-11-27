"""Création de la classe de configuration"""

# standard libs
from __future__ import annotations

# plugin libs
from helpers import debug
from helpers.app_config import AppConfig


class ZW164Config(AppConfig):
    """Classe de configuration"""

    def __init__(self: ZW164Config) -> None:
        """Initialisation de la classe"""
        AppConfig.__init__(self)

    def __enter__(self: ZW164Config) -> ZW164Config:
        """with wrapper"""
        self._refresh()
        return self

    def __exit__(self: ZW164Config, exc_type, exc_value, traceback) -> None:
        """with exit wrapper"""
        self._update_domoticz()

    @property
    def mqtt_id(self: ZW164Config) -> str:
        """mqtt_id getter"""
        if self._config is None:
            return ""
        if 'mqtt_id' not in self._config:
            self._config.update({'mqtt_id': ''})
        return self._config['mqtt_id']

    @mqtt_id.setter
    def mqtt_id(self: ZW164Config, value: str) -> None:
        """mqtt_id setter"""
        # type check
        if self._config is None:
            return
        if isinstance(value, str):
            # Mise à jour interne
            debug(f'Mise à jour - mqtt_id: {type(value)}{value}')
            self._config.update({'mqtt_id': value})
