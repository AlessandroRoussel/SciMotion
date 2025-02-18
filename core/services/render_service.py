"""
Service concerning rendering in general.

The RenderService class defines services within the core
package, concerning the application of a Modifier, the
rendering of various types of Layer, the compositing
of layers within a Sequence...
"""

import time
import moderngl
import numpy as np

from core.entities.modifier_repository import ModifierRepository
from core.entities.modifier import Modifier
from core.entities.modifier_template import ModifierFlag
from core.entities.render_context import RenderContext
from core.entities.sequence_context import SequenceContext
from core.entities.visual_layer import VisualLayer
from core.entities.solid_layer import SolidLayer
from core.entities.sequence import Sequence
from core.entities.gl_context import GLContext
from core.entities.parameter import Parameter
from data_types.data_type import DataType
from core.services.animation_service import AnimationService
from core.services.modifier_service import ModifierService
from data_types.color import Color
from utils.image import Image
from utils.config import Config


class RenderService:
    """Service concerning rendering in general."""

    _transform_program: moderngl.Program = None
    _color_shader: moderngl.ComputeShader = None
    _compositing_shader: moderngl.ComputeShader = None
    _tonemapping_shader: moderngl.ComputeShader = None
    _transform_msaa_fbo: moderngl.Buffer = None
    _transform_fbo: moderngl.Buffer = None
    _transform_msaa_texture: moderngl.Texture = None
    _transform_texture: moderngl.Texture = None

    @classmethod
    def apply_modifier_to_render_context(cls,
                                         modifier: Modifier,
                                         context: RenderContext):
        """Execute the action of a Modifier on a RenderContext."""
        _name_id = modifier.get_template_id()
        _modifier_template = ModifierRepository.get_template(_name_id)
        _function = _modifier_template.get_apply_function()
        _arguments = []
        _sequence_ctx = context.get_sequence_context()
        for _parameter in modifier.get_parameter_list():
            _data = cls.get_parameter_value(_parameter, _sequence_ctx)
            _arguments.append(_data)
        _function(context, *_arguments)

    @staticmethod
    def _image_from_texture(texture: moderngl.Texture) -> Image:
        """Extract an Image object from a moderngl Texture."""
        _data_bytes = texture.read()
        _image = Image(texture.width, texture.height, data_bytes=_data_bytes)
        return _image

    @staticmethod
    def _texture_from_image(gl_context: moderngl.Context,
                            image: Image
                            ) -> moderngl.Texture:
        """Create a moderngl Texture from an Image."""
        _width = image.get_width()
        _height = image.get_height()
        _data = image.get_data_bytes()
        _texture = gl_context.texture((_width, _height), 4, _data, dtype="f4")
        return _texture

    @classmethod
    def render_visual_layer(cls,
                            layer: VisualLayer,
                            sequence_ctx: SequenceContext
                            ) -> moderngl.Texture:
        """Render a VisualLayer to a texture."""

        # TODO : render only the visible part of the layer
        # (don't render any potential offscreen pixels)

        if isinstance(layer, SolidLayer):
            return cls.render_solid_layer(layer, sequence_ctx)
        raise NotImplementedError(f"Rendering method for '{layer.__class__}' "
                                  f"not implemented")

    @classmethod
    def render_solid_layer(cls,
                           layer: SolidLayer,
                           sequence_ctx: SequenceContext
                           ) -> moderngl.Texture:
        """Render a SolidLayer to a texture."""
        _width = layer.get_property("width").get_value()
        _height = layer.get_property("height").get_value()
        _context = RenderContext(_width, _height, sequence_ctx)
        _color = cls.get_parameter_value(layer.get_property_parameter("color"),
                                         sequence_ctx)
        _texture = cls.create_color_texture(_width, _height, _color)
        _context.set_src_texture(_texture)
        _modifier_list = layer.get_modifier_list()
        _start_index = 0
        for _modifier_index in range(_start_index, len(_modifier_list)):
            _modifier = _modifier_list[_modifier_index]
            if ModifierService.modifier_has_flag(
                _modifier, ModifierFlag.WRITEONLY):
                _start_index = _modifier_index
        for _modifier_index in range(_start_index, len(_modifier_list)):
            _modifier = _modifier_list[_modifier_index]
            cls.apply_modifier_to_render_context(_modifier, _context)
            _context.roll_textures()
        _context.release_dest_texture()
        return _context.get_src_texture()
    
    @staticmethod
    def get_parameter_value(parameter: Parameter,
                            sequence_ctx: SequenceContext
                            ) -> DataType:
        """Get the value of a parameter according to a sequence context."""
        return AnimationService.get_value_at_frame(
            parameter, sequence_ctx.get_current_frame()).get_value()

    @classmethod
    def create_color_texture(cls,
                             width: int,
                             height: int,
                             color: tuple = (0, 0, 0, 0)
                             ) -> moderngl.Texture:
        """Render a SolidLayer to a texture using a fragment shader."""
        _gl_context = GLContext.get_context()
        if cls._color_shader is None:
            _glsl_code = """
            #version 430
            layout (local_size_x = 1, local_size_y = 1) in;
            layout (rgba32f, binding = 0) uniform writeonly image2D texture;
            uniform vec4 color;
            void main() {
                imageStore(texture, ivec2(gl_GlobalInvocationID.xy), color);
            }
            """
            cls._color_shader = _gl_context.compute_shader(_glsl_code)
        _texture = _gl_context.texture((width, height), 4, dtype="f4")
        _texture.bind_to_image(0, read=False, write=True)
        cls._color_shader["color"] = color
        cls._color_shader.run(width, height, 1)
        return _texture

    @classmethod
    def render_sequence_frame(cls,
                              sequence: Sequence,
                              frame: int
                              ) -> moderngl.Texture:
        """Render a frame of a Sequence to an OpenGL texture."""
        _width = sequence.get_width()
        _height = sequence.get_height()
        _sequence_ctx = SequenceContext(sequence, frame)
        _gl_context = GLContext.get_context()
        _result_texture = _gl_context.texture((_width, _height), 4, dtype="f4")

        # TODO : try avoiding doing this just to clear the texture
        _fbo = _gl_context.framebuffer(color_attachments=[_result_texture])
        _fbo.use()
        _fbo.clear()
        _fbo.release()

        _layer_list = sequence.get_layer_list()
        for _layer in _layer_list:
            if not isinstance(_layer, VisualLayer):
                continue
            _start = _layer.get_start_frame()
            _end = _layer.get_end_frame()
            if frame < _start or frame >= _end:
                continue
            _texture = cls.render_visual_layer(_layer, _sequence_ctx)
            cls._transform_visual_layer_texture(
                _layer, _texture, _sequence_ctx)
            _texture.release()
            cls._composite_over(cls._transform_texture, _result_texture)

        cls._tonemap(_result_texture)
        return _result_texture

    @classmethod
    def _tonemap(cls, texture: moderngl.Texture):
        """Apply tone mapping to convert linear RGB to sRGB."""
        # TODO : handle different tonemapping algorithms
        _gl_context = GLContext.get_context()
        if cls._tonemapping_shader is None:
            _glsl_code = """
            #version 430
            layout (local_size_x = 1, local_size_y = 1) in;
            layout (rgba32f, binding = 0) uniform image2D texture;
            void main() {
                ivec2 coords = ivec2(gl_GlobalInvocationID.xy);
                vec4 color = imageLoad(texture, coords);
                vec3 linear = color.rgb;

                bvec3 cutoff = lessThan(linear, vec3(.0031308));
                vec3 higher = 1.055*pow(linear, vec3(1./2.4)) - .055;
                vec3 lower = linear * 12.92;
                vec3 sRGB = mix(higher, lower, cutoff);

                vec4 out_color = clamp(vec4(sRGB, color.a), 0., 1.);
                imageStore(texture, coords.xy, out_color);
            }
            """
            cls._tonemapping_shader = _gl_context.compute_shader(_glsl_code)
        texture.bind_to_image(0, read=True, write=True)
        cls._tonemapping_shader.run(texture.width, texture.height, 1)

    @classmethod
    def _composite_over(cls,
                        texture_a: moderngl.Texture,
                        texture_b: moderngl.Texture):
        """Composite two equal size moderngl Texture on top of each other."""
        _gl_context = GLContext.get_context()
        if cls._compositing_shader is None:
            _glsl_code = """
            #version 430
            layout (local_size_x = 1, local_size_y = 1) in;
            layout (rgba32f, binding = 0) uniform readonly image2D texture_a;
            layout (rgba32f, binding = 1) uniform image2D texture_b;
            void main() {
                ivec2 coords = ivec2(gl_GlobalInvocationID.xy);
                vec4 color_a = imageLoad(texture_a, coords);
                vec4 out_color;
                if(color_a.a == 1.){
                    out_color = color_a;
                }else{
                    vec4 color_b = imageLoad(texture_b, coords);

                    vec3 rgb_a = color_a.rgb;
                    vec3 rgb_b = color_b.rgb;
                    float alpha_a = color_a.a;
                    float alpha_b = color_b.a;

                    float out_alpha = alpha_a + alpha_b*(1.-alpha_a);
                    vec3 out_rgb = (rgb_a*alpha_a+rgb_b*alpha_b*(1.-alpha_a));
                    if(out_alpha > 0.){
                        out_rgb /= out_alpha;
                    }
                    out_color = vec4(out_rgb, out_alpha);
                }
                imageStore(texture_b, coords.xy, out_color);
            }
            """
            cls._compositing_shader = _gl_context.compute_shader(_glsl_code)
        texture_a.bind_to_image(0, read=True, write=False)
        texture_b.bind_to_image(1, read=True, write=True)
        cls._compositing_shader.run(texture_a.width, texture_a.height, 1)

    @classmethod
    def _transform_visual_layer_texture(cls,
                                        visual_layer: VisualLayer,
                                        texture: moderngl.Texture,
                                        sequence_ctx: SequenceContext):
        """Transform a texture based on a VisualLayer geometry."""
        out_width = sequence_ctx.get_width()
        out_height = sequence_ctx.get_height()
        _gl_context = GLContext.get_context()
        _tex_width = texture.width
        _tex_height = texture.height
        if cls._transform_program is None:
            _vertex_code = """
            #version 330 core
            in vec2 in_uv;
            out vec2 uv;
            uniform vec2 context_size;
            uniform vec2 texture_size;
            uniform vec2 position;
            uniform vec2 anchor;
            uniform vec2 scale;
            uniform float rotation;
            void main() {
                mat2 rot = mat2(cos(rotation), sin(rotation),
                                -sin(rotation), cos(rotation));
                vec2 transformed_pos = texture_size*scale*(in_uv-anchor);
                transformed_pos = rot*transformed_pos;
                transformed_pos += position*context_size;
                transformed_pos = transformed_pos*2./context_size - 1.;
                transformed_pos.y *= -1.;
                gl_Position = vec4(transformed_pos, 0., 1.);
                uv = in_uv;
            }
            """
            _fragment_code = """
            #version 330 core
            in vec2 uv;
            out vec4 out_color;
            uniform sampler2D in_texture;
            uniform float opacity;
            void main() {
                vec4 tex_color = texture(in_texture, uv);
                out_color = vec4(tex_color.rgb, tex_color.a * opacity);
            }
            """
            cls._transform_program = _gl_context.program(
                vertex_shader=_vertex_code,
                fragment_shader=_fragment_code
            )
        _quad_vertices = np.array([0,0,1,0,0,1,1,1], dtype=np.float32)
        _vbo = _gl_context.buffer(_quad_vertices.tobytes())
        _vao = _gl_context.vertex_array(cls._transform_program, _vbo, "in_uv")
        texture.use(location=0)

        # TODO : make this part thread safe, by storing the geometrical info
        # about the layer inside the RenderContext
        _position = cls.get_parameter_value(
            visual_layer.get_property_parameter("position"), sequence_ctx)
        _anchor = cls.get_parameter_value(
            visual_layer.get_property_parameter("anchor"), sequence_ctx)
        _scale = cls.get_parameter_value(
            visual_layer.get_property_parameter("scale"), sequence_ctx)
        _rotation = cls.get_parameter_value(
            visual_layer.get_property_parameter("rotation"), sequence_ctx)
        _opacity = cls.get_parameter_value(
            visual_layer.get_property_parameter("opacity"), sequence_ctx)

        cls._transform_program["in_texture"] = 0
        cls._transform_program["context_size"] = out_width, out_height
        cls._transform_program["texture_size"] = _tex_width, _tex_height
        cls._transform_program["position"] = _position
        cls._transform_program["anchor"] = _anchor
        cls._transform_program["scale"] = _scale
        cls._transform_program["rotation"] = _rotation
        cls._transform_program["opacity"] = _opacity

        if (cls._transform_texture is not None
            and (cls._transform_texture.width != out_width
                 or cls._transform_texture.height != out_height)):
            cls._transform_msaa_texture.release()
            cls._transform_msaa_fbo.release()
            cls._transform_texture.release()
            cls._transform_fbo.release()
            cls._transform_msaa_texture = None
            cls._transform_msaa_fbo = None
            cls._transform_texture = None
            cls._transform_fbo = None

        if cls._transform_texture is None:
            cls._transform_msaa_texture = _gl_context.texture(
                (out_width, out_height), 4, dtype="f4",
                samples=Config.render.anti_aliasing_samples)
            cls._transform_msaa_fbo = _gl_context.framebuffer(
                color_attachments=[cls._transform_msaa_texture])
            cls._transform_texture = _gl_context.texture(
                (out_width, out_height), 4, dtype="f4")
            cls._transform_fbo = _gl_context.framebuffer(
                color_attachments=[cls._transform_texture])

        cls._transform_msaa_fbo.use()
        cls._transform_msaa_fbo.clear(0, 0, 0, 0)
        _vao.render(moderngl.TRIANGLE_STRIP)
        _gl_context.copy_framebuffer(cls._transform_fbo,
                                     cls._transform_msaa_fbo)
