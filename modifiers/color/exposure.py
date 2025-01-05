"""Adjust the exposure and gamma."""

_name_id = "exposure"
_title = "Exposure"
_parameters = [
    {
        "name_id": "exposure",
        "title": "Exposure",
        "data_type": "number",
        "default_value": 1,
        "min_value": 0
    },
    {
        "name_id": "offset",
        "title": "Offset",
        "data_type": "number",
        "default_value": 0
    },
    {
        "name_id": "gamma",
        "title": "Gamma",
        "data_type": "number",
        "default_value": 1,
        "min_value": 0
    }
]

def _apply(_render_context, exposure, offset, gamma):
    gl_context = _render_context.get_gl_context()
    width = _render_context.get_width()
    height = _render_context.get_height()

    glsl_code = """
    #version 430

    layout (local_size_x = 16, local_size_y = 16) in;
    layout (rgba32f, binding = 0) uniform readonly image2D img_input;
    layout (rgba32f, binding = 1) uniform writeonly image2D img_output;

    uniform float exposure;
    uniform float offset;
    uniform float gamma;

    void main() {
        ivec2 coords = ivec2(gl_GlobalInvocationID.xy);
        vec2 dimensions = vec2(imageSize(img_output).xy);
        if(any(greaterThan(coords, dimensions))){return;}

        vec4 color = imageLoad(img_input, coords);
        color.rgb = pow(exposure*color.rgb + offset, vec3(gamma));

        imageStore(img_output, coords, color);
    }
    """

    compute_shader = gl_context.compute_shader(glsl_code)
    compute_shader["exposure"] = exposure
    compute_shader["offset"] = offset
    compute_shader["gamma"] = gamma

    _render_context.get_src_texture().bind_to_image(0, read=True, write=False)
    _render_context.get_dest_texture().bind_to_image(1, read=False, write=True)
    compute_shader.run(width//16+1, height//16+1, 1)
