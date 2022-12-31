# -*- coding: UTF-8 -*-
"""HTML page"""

# standard libs
from __future__ import annotations

import os
import shutil

# plugin libs
from domoticz.parameters import PluginParameters
import helpers

HTML_NAME = 'ZW164_py_plugin'
HTML_SOUCRE = f'./plugins/{HTML_NAME}/app/html/index.html'
HTML_DEST = f'./www/templates/{HTML_NAME}.html'


class HtmlPage:
    """The Html page"""
    parameters: PluginParameters
    src_path: str
    dst_path: str

    def on_start(self: HtmlPage, parameters: PluginParameters) -> None:
        """onStart event"""
        self.parameters = parameters
        self.__install()

    def on_stop(self: HtmlPage) -> None:
        """onStop event"""
        self.__uninstall()

    def __install(self: HtmlPage) -> None:
        """installation des fichiers"""
        self.src_path = os.path.join(
            self.parameters.HomeFolder, 'app/html/files'
        )
        self.dst_path = os.path.join(
            self.parameters.StartupFolder, 'www/templates'
        )
        shutil.copy2(
            os.path.join(self.src_path, 'index.html'),
            os.path.join(self.dst_path, self.parameters.Name + '.html')
        )
        shutil.copy2(
            os.path.join(self.src_path, 'zigbee2mqtt.js'),
            os.path.join(self.dst_path, self.parameters.Name + '.js')
        )
        dst_path_extras = os.path.join(
            self.dst_path,
            self.parameters.Name
        )
        helpers.debug(
            dst_path_extras=dst_path_extras,
            isdir_dst_path_extras=os.path.isdir(dst_path_extras)
        )
        if os.path.isdir(dst_path_extras):
            os.makedirs(dst_path_extras)
        shutil.copytree(
            os.path.join(self.src_path, 'libs'),
            dst_path_extras
        )

    def __uninstall(self: HtmlPage) -> None:
        """suppression des fichiers"""
