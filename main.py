from pathlib import Path

from matplotlib import pyplot as plt
import numpy as np
import configparser

from core.services.modifier_service import ModifierService
from core.services.layer_service import LayerService
from core.services.render_service import RenderService
from core.entities.solid_layer import SolidLayer
from core.entities.sequence import Sequence
from data_types.color import Color
from data_types.number import Number

config = configparser.ConfigParser()
config.read("config.cfg")

# print(config.getint("window", "min_width"))

# TODO : send the config to the editor, renderer, GUI
# TODO : create singletons editor, renderer, GUI


ModifierService().load_modifiers_from_directory(Path("modifiers"))


_layer1 = SolidLayer("", 0, 0, 1280, 720, Color.BLACK)

_modifier = ModifierService().modifier_from_template("linear_gradient")
ModifierService().add_modifier_to_layer(_modifier, _layer1)


_layer2 = SolidLayer("", 0, 0, 1280, 100, Color.BLACK)

_modifier = ModifierService().modifier_from_template("checkerboard")
ModifierService().add_modifier_to_layer(_modifier, _layer2)
_modifier = ModifierService().modifier_from_template("unmultiply")
ModifierService().add_modifier_to_layer(_modifier, _layer2)
_layer2._rotation.set_current_value(Number(.5))


_layer3 = SolidLayer("", 0, 0, 300, 300, Color.BLACK)

_modifier = ModifierService().modifier_from_template("checkerboard")
ModifierService().add_modifier_to_layer(_modifier, _layer3)
_layer3._rotation.set_current_value(Number(-.3))


_sequence = Sequence("", 1280, 720, 0, 0)
LayerService().add_layer_to_sequence(_layer1, _sequence)
LayerService().add_layer_to_sequence(_layer3, _sequence)
LayerService().add_layer_to_sequence(_layer2, _sequence)

_image = RenderService().render_sequence_frame(_sequence)
plt.imshow(_image.get_data_array())
plt.show()
