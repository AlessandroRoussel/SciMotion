#version 430

layout (local_size_x = 1, local_size_y = 1) in;
layout (rgba32f, binding = 0) uniform writeonly image2D imgOutput;
layout (rgba32f, binding = 1) uniform readonly image2D imgInput;

void main() {
	ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);

	vec4 src_color = imageLoad(imgInput, pixel_coords);
	float maxRGB = max(src_color.r, max(src_color.g, src_color.b));

	vec4 out_color = vec4(0.);
	if(maxRGB > 0.){
		out_color = vec4(src_color.rgb/maxRGB, src_color.a*maxRGB);
	}

	imageStore(imgOutput, pixel_coords, out_color);
}