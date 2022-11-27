#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Domoticz images"""

# standard libs
from typing import Any, Iterator, Mapping, Optional

# Domoticz lib
import Domoticz


class Images(Mapping[str, Any]):
    """Collection des images"""
    _images: Mapping[str, Domoticz.Image] = {}
    # _images_folder = "plugins/Freebox_V4/helper/images/"
    _icons_files = {
        "Freebox_serverWIFI": "/helpers/images/Freebox_serverWIFI Icons.zip",
        "Freebox_serverFBXPlayer": "/helpers/images/Freebox_serverFBXPlayer Icons.zip",
    }

    def __new__(cls, images: Optional[Mapping[str, Domoticz.Image]] = None) -> object:
        """Initialisation de la classe"""
        if isinstance(images, dict):
            cls._images = images
            # find domoticz folder
            # build path
            # populate image list
            for key, value in cls._icons_files.items():
                if key not in cls._images:
                    Domoticz.Image(value).Create()
        return super(Images, cls).__new__(cls)

    @classmethod
    def __getitem__(cls, key: str) -> int:
        """Wrapper pour Images['']"""
        if key in cls._images:
            return cls._images[key].ID
        raise KeyError('Image index non trouvé: {}'.format(key))

    @classmethod
    def __len__(cls) -> int:
        return len(cls._images)

    @classmethod
    def __iter__(cls) -> Iterator[Domoticz.Image]:
        for image in cls._images.values():
            yield image

    @classmethod
    def __str__(cls) -> str:
        """Wrapper pour str()"""

    @classmethod
    def __repr__(cls) -> str:
        """Wrapper pour repr()"""
