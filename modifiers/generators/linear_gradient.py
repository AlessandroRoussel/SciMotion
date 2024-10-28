"""
Generates a linear gradient between two colors.

This modifier takes two colors, a central position, and
cell dimensions, and generates a checkerboard pattern.
"""

_name_id = "linear_gradient"
_title = "Linear gradient"
_flags = ["WRITEONLY"]
_parameters = [
    {
        "name_id": "color_a",
        "title": "Color a",
        "data_type": "color",
        "default_value": [1, 0, 0]
    },
    {
        "name_id": "color_b",
        "title": "Color b",
        "data_type": "color",
        "default_value": [0, 0, 1]
    },
    {
        "name_id": "point_a",
        "title": "Point a",
        "data_type": "vector2",
        "default_value": [0, .5]
    },
    {
        "name_id": "point_b",
        "title": "Point b",
        "data_type": "vector2",
        "default_value": [1, .5]
    }
]


def _apply(_render_context, color_a, color_b, point_a, point_b):
    gl_context = _render_context.get_gl_context()
    width = _render_context.get_width()
    height = _render_context.get_height()

    glsl_code = """
    #version 430

    layout (local_size_x = 1, local_size_y = 1) in;
    layout (rgba32f, binding = 0) uniform writeonly image2D img_output;

    uniform vec4 color_a;
    uniform vec4 color_b;
    uniform vec2 point_a;
    uniform vec2 point_b;

    void main() {
        ivec2 coords = ivec2(gl_GlobalInvocationID.xy);
        vec2 dimensions = vec2(imageSize(img_output).xy);

        vec2 uv = vec2(coords) / dimensions;
        vec2 axis = (point_b - point_a) * dimensions;
        vec2 vector = (uv - point_a) * dimensions;

        float t = 0.;
        float norm2 = dot(axis, axis);
        if(norm2 > 0.){
            t = clamp(dot(axis, vector) / norm2, 0., 1.);
        }else{
            if(vector.x > 0.){
                t = 1.;
            }
        }

        vec4 color = mix(color_a, color_b, t);
        imageStore(img_output, coords, color);
    }
    """

    compute_shader = gl_context.compute_shader(glsl_code)
    compute_shader["color_a"] = color_a
    compute_shader["color_b"] = color_b
    compute_shader["point_a"] = point_a
    compute_shader["point_b"] = point_b

    _render_context.get_dest_texture().bind_to_image(0, read=False, write=True)
    compute_shader.run(width, height, 1)
