"""Apply a fast box blur."""

_name_id = "box_blur"
_title = "Box blur"
_parameters = [
    {
        "name_id": "horizontal_radius",
        "title": "Horizontal radius",
        "data_type": "integer",
        "default_value": 2,
        "min_value": 0
    },
    {
        "name_id": "vertical_radius",
        "title": "Vertical radius",
        "data_type": "integer",
        "default_value": 2,
        "min_value": 0
    },
    {
        "name_id": "iterations",
        "title": "Iterations",
        "data_type": "integer",
        "default_value": 1,
        "min_value": 1,
        "max_value": 5
    }
]

def _apply(_render_context, horizontal_radius, vertical_radius, iterations):
    gl_context = _render_context.get_gl_context()
    width = _render_context.get_width()
    height = _render_context.get_height()

    glsl_code = """
    #version 430

    layout (local_size_x = 64) in;
    layout (rgba32f, binding = 0) uniform readonly image2D img_input;
    layout (rgba32f, binding = 1) uniform writeonly image2D img_output;

    uniform int radius;
    uniform bool horizontal;

    void main() {
        int j = int(gl_GlobalInvocationID.x);
        ivec2 dimensions = ivec2(imageSize(img_output).xy);
        int length = horizontal ? dimensions.x : dimensions.y;
        if(j >= (horizontal ? dimensions.y : dimensions.x)){return;}

        vec4 color = vec4(0.);
        float kernel_size = float(2*radius + 1);

        for(int i=0; i<=min(radius, length-1); i+=1){
            ivec2 xy = horizontal ? ivec2(i, j) : ivec2(j, i);
            color += imageLoad(img_input, xy);
        }

        for(int i=0; i<length; i+=1){
            ivec2 xy = horizontal ? ivec2(i, j) : ivec2(j, i);
            imageStore(img_output, xy, color/kernel_size);
            if(i-radius >= 0){
                ivec2 coords = horizontal ? ivec2(i-radius, j)
                                          : ivec2(j, i-radius);
                color -= imageLoad(img_input, coords);
            }
            if(i+radius+1 < length){
                ivec2 coords = horizontal ? ivec2(i+radius+1, j)
                                          : ivec2(j, i+radius+1);
                color += imageLoad(img_input, coords);
            }
        }
    }
    """

    compute_shader = gl_context.compute_shader(glsl_code)

    if horizontal_radius == 0 and vertical_radius == 0:
        _render_context.pass_through()
        return

    for i in range(iterations):
        
        if horizontal_radius > 0:
            if i > 0:
                _render_context.roll_textures()
            compute_shader["radius"] = horizontal_radius
            compute_shader["horizontal"] = True
            _render_context.get_src_texture().bind_to_image(0, read=True, write=False)
            _render_context.get_dest_texture().bind_to_image(1, read=False, write=True)
            compute_shader.run(height//64+1, 1, 1)

        if vertical_radius > 0:
            if horizontal_radius > 0:
                _render_context.roll_textures()
            compute_shader["radius"] = vertical_radius
            compute_shader["horizontal"] = False
            _render_context.get_src_texture().bind_to_image(0, read=True, write=False)
            _render_context.get_dest_texture().bind_to_image(1, read=False, write=True)
            compute_shader.run(width//64+1, 1, 1)