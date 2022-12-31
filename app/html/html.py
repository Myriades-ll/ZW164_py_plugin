# -*- coding: UTF-8 -*-
"""HTML page"""

# standard libs
from __future__ import annotations

import os
import shutil

# plugin libs
from domoticz.parameters import PluginParameters


class HtmlPage:
    """The Html page"""

    def __init__(self: HtmlPage) -> None:
        """Initialisation de la classe"""
        self.dst_path: str
        self.dst_templates_path: str
        self.parameters: PluginParameters
        self.src_path: str
        self.src_templates_path: str

    def on_start(self: HtmlPage, parameters: PluginParameters) -> None:
        """onStart event"""
        self.parameters = parameters
        self.__install()

    def on_stop(self: HtmlPage) -> None:
        """onStop event"""
        self.__uninstall()

    def __install(self: HtmlPage) -> None:
        """installation des fichiers"""
        # create str path's
        self.dst_path = os.path.join(
            self.parameters.StartupFolder, 'www/templates'
        )
        self.src_path = os.path.join(
            self.parameters.HomeFolder, 'app/html/files'
        )
        self.dst_templates_path = os.path.join(self.dst_path, 'ccss_libs')
        self.src_templates_path = os.path.join(self.src_path, 'ccss_libs')
        # coyping files
        shutil.copy2(
            os.path.join(self.src_path, 'index.html'),
            os.path.join(self.dst_path, self.parameters.Name + '.html')
        )
        shutil.copy2(
            os.path.join(self.src_path, 'ccss.js'),
            self.dst_path
        )
        shutil.copytree(
            self.src_templates_path,
            self.dst_templates_path
        )

    def __uninstall(self: HtmlPage) -> None:
        """suppression des fichiers"""
        os.remove(os.path.join(self.dst_path, self.parameters.Name + '.html'))
        os.remove(os.path.join(self.dst_path, 'ccss.js'))
        if os.path.isdir(self.dst_templates_path):
            shutil.rmtree(self.dst_templates_path)
