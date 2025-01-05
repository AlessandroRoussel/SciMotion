"""
Adds a per pixel random simple noise.

This modifier adds a certain amount
of per pixel random simple noise.
"""

_name_id = "simple_noise"
_title = "Simple noise"
_parameters = [
    {
        "name_id": "amount",
        "title": "Amount",
        "data_type": "number",
        "default_value": .1,
        "min_value": 0
    },
    {
        "name_id": "chromaticity",
        "title": "Chromaticity",
        "data_type": "number",
        "default_value": .5,
        "min_value": 0,
        "max_value": 1
    },
    {
        "name_id": "space",
        "title": "Space",
        "data_type": "integer",
        "default_value": 0,
        "flags": ["dropdown"],
        "additional_data": {"options": ["Linear",
                                        "Gamma (sRGB)"]}
    },
    {
        "name_id": "distribution",
        "title": "Distribution",
        "data_type": "integer",
        "default_value": 1,
        "flags": ["dropdown"],
        "additional_data": {"options": ["Uniform",
                                        "Gaussian"]}
    },
    {
        "name_id": "animated",
        "title": "Animated",
        "data_type": "boolean",
        "default_value": 1
    },
    {
        "name_id": "seed",
        "title": "Seed",
        "data_type": "integer"
    }
]

def _apply(_render_context, amount, chromaticity, space, distribution,
           animated, seed):
    gl_context = _render_context.get_gl_context()
    width = _render_context.get_width()
    height = _render_context.get_height()

    glsl_code = """
    #version 430

    layout (local_size_x = 16, local_size_y = 16) in;
    layout (rgba32f, binding = 0) uniform readonly image2D img_input;
    layout (rgba32f, binding = 1) uniform writeonly image2D img_output;

    uniform int space;
    uniform float amount;
    uniform float chromaticity;
    uniform float frame;
    uniform int distribution;
    uniform bool animated;
    uniform int seed;

    vec3 srgb_to_linear(vec3 srgb){
        bvec3 cutoff = lessThan(srgb, vec3(.04045));
        vec3 higher = pow((srgb + .055)/1.055, vec3(2.4));
        vec3 lower = srgb / 12.92;
        return mix(higher, lower, cutoff);
    }

    vec3 linear_to_srgb(vec3 linear){
        bvec3 cutoff = lessThan(linear, vec3(.0031308));
        vec3 higher = 1.055*pow(linear, vec3(1./2.4)) - .055;
        vec3 lower = linear * 12.92;
        return mix(higher, lower, cutoff);
    }

    uint hash3(uint x, uint y, uint z){
        x += x >> 11;
        x ^= x << 7;
        x += y;
        x ^= x << 3;
        x += z ^ (x >> 14);
        x ^= x << 6;
        x += x >> 15;
        x ^= x << 5;
        x += x >> 12;
        x ^= x << 9;
        return x;
    }

    float random3(vec3 f){
        uint mantissaMask = 0x007FFFFFu;
        uint one = 0x3F800000u;
        uvec3 u = floatBitsToUint(f);
        uint h = hash3(u.x, u.y, u.z);
        return uintBitsToFloat((h & mantissaMask) | one) - 1.;
    }

    vec3 random_vec3(vec3 f){
        return vec3(random3(f),
                    random3(f*2.4+11.),
                    random3(f*.76+17.));
    }

    vec3 inverf(vec3 x){
        vec3 w = .99999999*x;
        vec3 u = log(1.-w*w);
        vec3 z = 4.54728408834 + .5*u;
        return sign(x)*sqrt(sqrt(z*z-u*7.14285714286) - z);
    }

    vec3 erf(vec3 x){
        vec3 x2 = x*x;
        return sign(x)*sqrt(1.-exp(-x2*(9.09456817668+x2)/(x2+7.14285714286)));
    }

    void main() {
        ivec2 coords = ivec2(gl_GlobalInvocationID.xy);
        vec2 dimensions = vec2(imageSize(img_output).xy);
        if(any(greaterThan(coords, dimensions))){return;}

        vec4 color = imageLoad(img_input, coords);
        if(amount > 0.){
            vec3 uvw = vec3(vec2(coords)/dimensions,
                            animated ? float(frame) : 0.);
            uvw.z += float(seed);

            vec3 chroma_noise = random_vec3(uvw);
            vec3 luma_noise = vec3(random3(uvw*13.2+5.4));
            chroma_noise = sqrt(2.)*inverf(2.*chroma_noise - 1.);
            luma_noise = sqrt(2.)*inverf(2.*luma_noise - 1.);
            vec3 noise = mix(luma_noise, chroma_noise, chromaticity);
            noise /= sqrt(1.-2.*chromaticity*(1.-chromaticity));

            if(distribution == 0){
                noise = erf(noise/sqrt(2.)) * sqrt(3.);
            }

            if(space == 1){
                color.rgb = linear_to_srgb(color.rgb);
                color.rgb += noise * amount * .5;
                color.rgb = srgb_to_linear(color.rgb);
            }else{
                color.rgb += noise * amount * .5;
            }
        }

        imageStore(img_output, coords, color);
    }
    """

    compute_shader = gl_context.compute_shader(glsl_code)
    compute_shader["amount"] = amount
    compute_shader["chromaticity"] = chromaticity
    compute_shader["space"] = space
    compute_shader["distribution"] = distribution
    compute_shader["animated"] = animated
    compute_shader["seed"] = seed

    _sequence_context = _render_context.get_sequence_context()
    compute_shader["frame"] = float(_sequence_context.get_current_frame())

    _render_context.get_src_texture().bind_to_image(0, read=True, write=False)
    _render_context.get_dest_texture().bind_to_image(1, read=False, write=True)
    compute_shader.run(width//16+1, height//16+1, 1)
