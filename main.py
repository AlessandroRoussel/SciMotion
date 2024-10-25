from pathlib import Path

import configparser

from editing.services.effect_service import EffectService

config = configparser.ConfigParser()
config.read("config.cfg")

# print(config.getint("window", "min_width"))

# TODO : send the config to the editor, renderer, GUI
# TODO : create singletons editor, renderer, GUI

EffectService().load_effects_from_directory(Path("shaders"))