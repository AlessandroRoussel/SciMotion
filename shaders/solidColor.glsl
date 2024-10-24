#version 430

layout (local_size_x = 1, local_size_y = 1) in;
layout (rgba32f, binding = 0) uniform writeonly image2D imgOutput;

uniform vec4 color;

void main() {
	ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);
	imageStore(imgOutput, pixel_coords, color);
}