from utils.singleton import Singleton
from editing.entities.modifier_repository import ModifierRepository
from editing.entities.modifier import Modifier
from rendering.entities.render_context import RenderContext


class RenderService(metaclass=Singleton):

    def apply_modifier_to_render_context(self,
                                         modifier: Modifier,
                                         context: RenderContext):
        """Execute the action of a Modifier on a RenderContext."""
        _name_id = modifier.get_template_id()
        _modifier_template = ModifierRepository().get_template(_name_id)
        _function = _modifier_template.get_apply_function()
        _arguments = []
        for _parameter in modifier.get_parameter_list():
            _raw_data = _parameter.get_current_value()
            _arguments.append(_raw_data.get_value())
        _function(context, *_arguments)
