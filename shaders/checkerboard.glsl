#version 430

layout (local_size_x = 1, local_size_y = 1) in;
layout (rgba32f, binding = 0) uniform writeonly image2D imgOutput;

uniform vec4 color_A;
uniform vec4 color_B;
uniform vec2 center;
uniform vec2 cell_size;

void main() {
	ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);
	ivec2 dimensions = imageSize(imgOutput).xy;

	vec2 xy = vec2(pixel_coords) - center * vec2(dimensions);
	vec2 q = xy/cell_size-2.*floor(xy/2./cell_size);
    bool checker = q.x < 1. ^^ q.y < 1.;
    
    vec4 color = mix(color_A, color_B, float(checker));
	imageStore(imgOutput, pixel_coords, color);
}