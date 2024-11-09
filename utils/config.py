"""
Holds the configuration.

The Config static class holds all the useful
variables loaded from the configuration file.
"""

from types import SimpleNamespace

from configparser import ConfigParser


class Config():
    """Holds the configuration."""

    @classmethod
    def load(cls, config: ConfigParser):
        cls.store(config, "app", "title", str)
        cls.store(config, "app", "icon", str)
        cls.store(config, "app", "version_major", int)
        cls.store(config, "app", "version_minor", int)
        cls.store(config, "app", "modifiers_directory", str)

        cls.store(config, "window", "min_width", int)
        cls.store(config, "window", "min_height", int)
        cls.store(config, "window", "full_screen", bool)
        cls.store(config, "window", "second_screen", bool)
        cls.store(config, "window", "left_pane_width", int)
        cls.store(config, "window", "bottom_pane_height", int)
        cls.store(config, "window", "right_pane_width", int)
        cls.store(config, "window", "splitter_width", int)
        
        cls.store(config, "viewer", "checkerboard_size", float)
        cls.store(config, "viewer", "checkerboard_color_a", float)
        cls.store(config, "viewer", "checkerboard_color_b", float)
        cls.store(config, "viewer", "min_zoom", float)
        cls.store(config, "viewer", "max_zoom", float)
        cls.store(config, "viewer", "fit_padding", float)
        cls.store(config, "viewer", "zoom_around_cursor", bool)
        cls.store(config, "viewer", "zoom_sensitivity", float)
        
        cls.store(config, "sequence", "default_title", str)
        cls.store(config, "sequence", "default_width", int)
        cls.store(config, "sequence", "default_height", int)
        cls.store(config, "sequence", "default_frame_rate", float)
        cls.store(config, "sequence", "default_duration", int)

        cls.store(config, "timeline", "side_panel_width", int)
        cls.store(config, "timeline", "layer_height", int)
        cls.store(config, "timeline", "layer_spacing", int)
        cls.store(config, "timeline", "max_pixels_per_frame", int)
        cls.store(config, "timeline", "zoom_sensitivity", float)
        cls.store(config, "timeline", "scroll_sensitivity", float)
        cls.store(config, "timeline", "ruler_height", int)
        cls.store(config, "timeline", "time_grid_max_width", int)
        cls.store(config, "timeline", "time_text_max_width", int)
        cls.store(config, "timeline", "cursor_handle_width", int)
        cls.store(config, "timeline", "vertical_stripes", bool)
        cls.store(config, "timeline", "horizontal_stripes", bool)
        cls.store(config, "timeline", "horizontal_padding", int)

        cls.store(config, "solid_layer", "default_title", str)

        cls.store(config, "render", "anti_aliasing_samples", int)
    
    @classmethod
    def store(cls,
              config: ConfigParser,
              section: str,
              name: str,
              type: type = str):
        """Store a value from the config."""
        if not hasattr(cls, section):
            setattr(cls, section, SimpleNamespace())
        func = config.get
        if type is int:
            func = config.getint
        elif type is bool:
            func = config.getboolean
        elif type is float:
            func = config.getfloat
        setattr(getattr(cls, section), name, func(section, name))