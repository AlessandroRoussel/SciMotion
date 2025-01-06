"""
Generates a linear gradient between two colors.

This modifier takes two colors, a central position, and
cell dimensions, and generates a checkerboard pattern.
"""

_name_id = "linear_gradient"
_title = "Linear gradient"
_flags = ["writeonly"]
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
    },
    {
        "name_id": "interpolation",
        "title": "Interpolation",
        "data_type": "integer",
        "default_value": 0,
        "flags": ["dropdown"],
        "additional_data": {"options": ["Perceptual (okLab)",
                                        "Linear",
                                        "Gamma (sRGB)"]}
    }
]

def _apply(_render_context, color_a, color_b, point_a, point_b, interpolation):
    gl_context = _render_context.get_gl_context()
    width = _render_context.get_width()
    height = _render_context.get_height()

    glsl_code = """
    #version 430

    layout (local_size_x = 16, local_size_y = 16) in;
    layout (rgba32f, binding = 0) uniform writeonly image2D img_output;

    uniform vec4 color_a;
    uniform vec4 color_b;
    uniform vec2 point_a;
    uniform vec2 point_b;
    uniform int interpolation;

    const mat3 linear_to_lms_mat = mat3(.4122214708, .5363325363, .0514459929,
                                        .2119034982, .6806995451, .1073969566,
                                        .0883024619, .2817188376, .6299787005);
    
    const mat3 lms_to_oklab_mat = mat3(.2104542553, .793617785, -.0040720468,
                                       1.9779984951, -2.428592205, .4505937099,
                                       .0259040371, .7827717662, -.808675766);
    
    const mat3 oklab_to_lms_mat = mat3(1., .3963377774, .2158037573,
                                       1., -.1055613458, -.0638541728,
                                       1., -.0894841775, -1.291485548);
    
    const mat3 lms_to_linear_mat = mat3(4.0767416621, -3.3077115913, 0.2309699292,
                                        -1.2684380046, 2.6097574011, -0.3413193965,
                                        -0.0041960863, -0.7034186147, 1.7076147010);

    vec3 linear_to_oklab(vec3 linear){
        vec3 lms = linear_to_lms_mat * linear;
        lms = sign(lms) * pow(abs(lms), vec3(1./3.));
        return lms_to_oklab_mat * lms;
    }

    vec3 oklab_to_linear(vec3 oklab){
        vec3 lms = pow(oklab_to_lms_mat * oklab, vec3(3.));
        return lms_to_linear_mat * lms;
    }

    vec3 linear_to_srgb(vec3 linear){
        bvec3 cutoff = lessThan(linear, vec3(.0031308));
        vec3 higher = 1.055*pow(linear, vec3(1./2.4)) - .055;
        vec3 lower = linear * 12.92;
        return mix(higher, lower, cutoff);
    }

    vec3 srgb_to_linear(vec3 srgb){
        bvec3 cutoff = lessThan(srgb, vec3(.04045));
        vec3 higher = pow((srgb + .055)/1.055, vec3(2.4));
        vec3 lower = srgb / 12.92;
        return mix(higher, lower, cutoff);
    }

    void main() {
        ivec2 coords = ivec2(gl_GlobalInvocationID.xy);
        ivec2 dimensions = imageSize(img_output).xy;
        if(any(greaterThanEqual(coords, dimensions))){return;}

        vec2 dim = vec2(dimensions);
        vec2 uv = vec2(coords) / dim;
        vec2 axis = (point_b - point_a) * dim;
        vec2 vector = (uv - point_a) * dim;

        float t = 0.;
        float norm2 = dot(axis, axis);
        if(norm2 > 0.){
            t = clamp(dot(axis, vector) / norm2, 0., 1.);
        }else{
            if(vector.x > 0.){
                t = 1.;
            }
        }

        vec3 color;
        float alpha = mix(color_a.a, color_b.a, t);
        if(interpolation == 0){
            color = mix(linear_to_oklab(color_a.rgb),
                        linear_to_oklab(color_b.rgb), t);
            color = oklab_to_linear(color);
        }else if(interpolation == 1){
            color = mix(color_a.rgb, color_b.rgb, t);
        }else if(interpolation == 2){
            color = mix(linear_to_srgb(color_a.rgb),
                        linear_to_srgb(color_b.rgb), t);
            color = srgb_to_linear(color);
        }

        color = max(color, 0.);
        imageStore(img_output, coords, vec4(color, alpha));
    }
    """

    compute_shader = gl_context.compute_shader(glsl_code)
    compute_shader["color_a"] = color_a
    compute_shader["color_b"] = color_b
    compute_shader["point_a"] = point_a
    compute_shader["point_b"] = point_b
    compute_shader["interpolation"] = interpolation

    _render_context.get_dest_texture().bind_to_image(0, read=False, write=True)
    compute_shader.run(width//16+1, height//16+1, 1)
