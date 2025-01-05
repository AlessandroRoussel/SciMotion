"""
Generates a checkerboard pattern.

This modifier takes two colors, a central position, and
cell dimensions, and generates a checkerboard pattern.
"""

_name_id = "checkerboard"
_title = "Checkerboard"
_flags = ["writeonly"]
_parameters = [
    {
        "name_id": "color_a",
        "title": "Color a",
        "data_type": "color",
        "default_value": [.448, .448, .448]
    },
    {
        "name_id": "color_b",
        "title": "Color b",
        "data_type": "color",
        "default_value": [1, 1, 1]
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
    },
    {
        "name_id": "antialiasing",
        "title": "Anti-aliasing",
        "data_type": "boolean",
        "default_value": True
    }
]

# TODO : add rotation

def _apply(_render_context, color_a, color_b, cell_size, center, antialiasing):
    gl_context = _render_context.get_gl_context()
    width = _render_context.get_width()
    height = _render_context.get_height()

    glsl_code = """
    #version 430

    layout (local_size_x = 16, local_size_y = 16) in;
    layout (rgba32f, binding = 0) uniform writeonly image2D img_output;

    uniform vec4 color_a;
    uniform vec4 color_b;
    uniform vec2 center;
    uniform vec2 cell_size;
    uniform bool antialiasing;

    void main() {
        ivec2 coords = ivec2(gl_GlobalInvocationID.xy);
        ivec2 dimensions = imageSize(img_output).xy;
        if(any(greaterThan(coords, dimensions))){return;}

        vec2 xy = vec2(coords) + .5 - center * vec2(dimensions);
        float checker = .5;

        if(cell_size.x != 0. && cell_size.y != 0.){
            if(!antialiasing){
                vec2 q = 2.*fract(xy/2./cell_size);
                checker = float(q.x < 1. ^^ q.y < 1.);
            }else{
                vec2 q1 = abs(fract((xy*.5 + .25)/cell_size) - .5);
                vec2 q2 = abs(fract((xy*.5 - .25)/cell_size) - .5);
                vec2 q = 2.*cell_size*(q1 - q2);
                checker = clamp(.5*(1. - q.x*q.y), 0., 1.);
            }
        }

        vec4 color = mix(color_a, color_b, checker);
        imageStore(img_output, coords, color);
    }
    """

    compute_shader = gl_context.compute_shader(glsl_code)
    compute_shader["color_a"] = color_a
    compute_shader["color_b"] = color_b
    compute_shader["cell_size"] = cell_size
    compute_shader["center"] = center
    compute_shader["antialiasing"] = antialiasing

    _render_context.get_dest_texture().bind_to_image(0, read=False, write=True)
    compute_shader.run(width//16+1, height//16+1, 1)
