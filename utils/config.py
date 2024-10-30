"""
Holds the configuration.

The Config singleton class holds all the useful
variables loaded from the configuration file.
"""

from types import SimpleNamespace

from configparser import ConfigParser

from utils.singleton import Singleton


class Config(metaclass=Singleton):
    """Holds the configuration."""

    def __init__(self, config: ConfigParser):
        self.store(config, "app", "title", str)
        self.store(config, "app", "icon", str)
        self.store(config, "app", "version_major", int)
        self.store(config, "app", "version_minor", int)

        self.store(config, "window", "min_width", int)
        self.store(config, "window", "min_height", int)
        self.store(config, "window", "full_screen", bool)
        self.store(config, "window", "second_screen", bool)
        self.store(config, "window", "left_pane_width", int)
        self.store(config, "window", "bottom_pane_height", int)
        self.store(config, "window", "right_pane_width", int)
        self.store(config, "window", "splitter_width", int)
        
        self.store(config, "viewer", "checkerboard_size", float)
        self.store(config, "viewer", "checkerboard_color_a", float)
        self.store(config, "viewer", "checkerboard_color_b", float)
        self.store(config, "viewer", "min_zoom", float)
        self.store(config, "viewer", "max_zoom", float)
        self.store(config, "viewer", "fit_padding", float)
        self.store(config, "viewer", "zoom_around_cursor", bool)
        self.store(config, "viewer", "zoom_sensitivity", float)
    
    def store(self,
              config: ConfigParser,
              section: str,
              name: str,
              type: type = str):
        """Store a value from the config."""
        if not hasattr(self, section):
            setattr(self, section, SimpleNamespace())
        func = config.get
        if type is int:
            func = config.getint
        elif type is bool:
            func = config.getboolean
        elif type is float:
            func = config.getfloat
        setattr(getattr(self, section), name, func(section, name))