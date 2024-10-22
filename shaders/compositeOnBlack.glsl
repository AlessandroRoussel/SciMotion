#version 430

layout (local_size_x = 1, local_size_y = 1) in;
layout (rgba32f, binding = 0) uniform writeonly image2D imgOutput;
layout (rgba32f, binding = 1) uniform readonly image2D imgInput;

void main() {
	ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);

	vec4 src_color = imageLoad(imgInput, pixel_coords);
	vec4 out_color = vec4(src_color.rgb * src_color.a, 1.);

	imageStore(imgOutput, pixel_coords, out_color);
}