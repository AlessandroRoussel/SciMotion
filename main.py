from pathlib import Path

from matplotlib import pyplot as plt
import numpy as np
import configparser

from editing.services.modifier_service import ModifierService
from editing.entities.modifier_repository import ModifierRepository
from rendering.entities.render_context import RenderContext

config = configparser.ConfigParser()
config.read("config.cfg")

# print(config.getint("window", "min_width"))

# TODO : send the config to the editor, renderer, GUI
# TODO : create singletons editor, renderer, GUI


ModifierService().load_modifiers_from_directory(Path("modifiers"))
_context = RenderContext(0, 600, 500)
_modifier = ModifierService().modifier_from_template("checkerboard")
ModifierService().apply_modifier_to_render_context(_modifier, _context)


_modified_data = np.frombuffer(
    _context._result_texture.read(), dtype=np.float32).reshape(
        (_context.get_height(), _context.get_width(), 4))
plt.imshow(_modified_data)
plt.show()
