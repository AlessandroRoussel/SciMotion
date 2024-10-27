from pathlib import Path

from matplotlib import pyplot as plt
import numpy as np
import configparser

from editing.services.modifier_service import ModifierService
from editing.services.render_service import RenderService
from rendering.entities.render_context import RenderContext

config = configparser.ConfigParser()
config.read("config.cfg")

# print(config.getint("window", "min_width"))

# TODO : send the config to the editor, renderer, GUI
# TODO : create singletons editor, renderer, GUI


ModifierService().load_modifiers_from_directory(Path("modifiers"))
_context = RenderContext(0, 600, 500)

_modifier1 = ModifierService().modifier_from_template("checkerboard")
RenderService().apply_modifier_to_render_context(_modifier1, _context)

_context.roll_textures()

_modifier2 = ModifierService().modifier_from_template("unmultiply")
RenderService().apply_modifier_to_render_context(_modifier2, _context)


_modified_data = np.frombuffer(
    _context.get_dest_texture().read(), dtype=np.float32).reshape(
        (_context.get_height(), _context.get_width(), 4))
plt.imshow(_modified_data)
plt.show()
