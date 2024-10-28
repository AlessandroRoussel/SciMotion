import matplotlib.pyplot as plt
import moderngl
import numpy as np

_context = moderngl.create_context(standalone=True)

_compute_shader_source = """
#version 430

layout(local_size_x = 16, local_size_y = 16) in;

layout(rgba32f, binding = 0) uniform image2D img_output;

void main() {
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    vec4 color = imageLoad(img_output, pos);
    color.rgb = color.rgb;
    color.a = 1.;
    imageStore(img_output, pos, color);
}
"""
_compute_shader = _context.compute_shader(_compute_shader_source)

_width, _height = 512, 512
_data = np.zeros(shape=(_width, _height, 4)).astype("f4")
_texture = _context.texture((_width, _height), 4, dtype="f4")
_texture.bind_to_image(0, read=True, write=True)

_workgroup_size_x = (_width + 15) // 16
_workgroup_size_y = (_height + 15) // 16
_compute_shader.run(_workgroup_size_x, _workgroup_size_y, 1)
_modified_data = np.frombuffer(
    _texture.read(), dtype=np.float32).reshape((_height, _width, 4))

plt.imshow(_modified_data)
plt.show()
