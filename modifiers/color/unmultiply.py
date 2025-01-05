"""
Unmultiplies an image.

This modifier takes the input image and unmultiplies it,
which corresponds to making the dark areas transparent,
such that when re-composited onto a black background
we recover the original image.
"""

_name_id = "unmultiply"
_title = "Unmultiply"

def _apply(_render_context):
    gl_context = _render_context.get_gl_context()
    width = _render_context.get_width()
    height = _render_context.get_height()

    glsl_code = """
    #version 430

    layout (local_size_x = 16, local_size_y = 16) in;
    layout (rgba32f, binding = 0) uniform readonly image2D img_input;
    layout (rgba32f, binding = 1) uniform writeonly image2D img_output;

    void main() {
        ivec2 coords = ivec2(gl_GlobalInvocationID.xy);
        ivec2 dimensions = imageSize(img_output).xy;
        if(any(greaterThan(coords, dimensions))){return;}

        vec4 src_color = imageLoad(img_input, coords);
        float max_rgb = max(src_color.r, max(src_color.g, src_color.b));
        vec4 out_color = vec4(0.);
        if(max_rgb > 0.){
            out_color = vec4(src_color.rgb/max_rgb, src_color.a*max_rgb);
        }

        imageStore(img_output, coords, out_color);
    }
    """

    compute_shader = gl_context.compute_shader(glsl_code)
    _render_context.get_src_texture().bind_to_image(0, read=True, write=False)
    _render_context.get_dest_texture().bind_to_image(1, read=False, write=True)
    compute_shader.run(width//16+1, height//16+1, 1)
