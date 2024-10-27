"""
Generates a checkerboard pattern.

This modifier takes two colors, a central position, and
cell dimensions, and generates a checkerboard pattern.
"""

_name_id = "checkerboard"
_title = "Checkerboard"
_flags = ["WRITEONLY"]
_parameters = [
    {
        "name_id": "color_a",
        "title": "Color a",
        "data_type": "color",
        "default_value": [0.7, 0.7, 0.7, 1],
        "min_value": 0,
        "max_value": 1
    },
    {
        "name_id": "color_b",
        "title": "Color b",
        "data_type": "color",
        "default_value": [1, 1, 1, 1],
        "min_value": 0,
        "max_value": 1
    },
    {
        "name_id": "cell_size",
        "title": "Cell size",
        "data_type": "vector2",
        "default_value": [50, 50]
    },
    {
        "name_id": "center",
        "title": "Center",
        "data_type": "vector2",
        "default_value": [0.5, 0.5]
    }
]


def _apply(_render_context, color_a, color_b, cell_size, center):
    gl_context = _render_context.get_gl_context()
    width = _render_context.get_width()
    height = _render_context.get_height()

    glsl_code = """
    #version 430

    layout (local_size_x = 1, local_size_y = 1) in;
    layout (rgba32f, binding = 0) uniform writeonly image2D img_output;

    uniform vec4 color_a;
    uniform vec4 color_b;
    uniform vec2 center;
    uniform vec2 cell_size;

    void main() {
        ivec2 coords = ivec2(gl_GlobalInvocationID.xy);
        ivec2 dimensions = imageSize(img_output).xy;

        vec2 xy = vec2(coords) - center * vec2(dimensions);
        vec2 q = xy/cell_size - 2.*floor(xy/2./cell_size);
        bool checker = q.x < 1. ^^ q.y < 1.;

        vec4 color = mix(color_a, color_b, float(checker));
        imageStore(img_output, coords, color);
    }
    """

    compute_shader = gl_context.compute_shader(glsl_code)
    compute_shader["color_a"] = color_a
    compute_shader["color_b"] = color_b
    compute_shader["cell_size"] = cell_size
    compute_shader["center"] = center

    dest_texture = gl_context.texture((width, height), 4, dtype="f4")
    dest_texture.bind_to_image(0, read=False, write=True)
    _render_context.set_result_texture(dest_texture)
    compute_shader.run(width, height, 1)
