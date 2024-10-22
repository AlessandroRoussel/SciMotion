#version 430

layout (local_size_x = 1, local_size_y = 1) in;
layout (rgba32f, binding = 0) uniform writeonly image2D imgOutput;

uniform vec2 point_A;
uniform vec2 point_B;
uniform vec4 color_A;
uniform vec4 color_B;

void main() {
	ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);
	ivec2 dimensions = imageSize(imgOutput).xy;

	vec2 uv = vec2(pixel_coords) / vec2(dimensions);
	vec2 axis = (point_B - point_A) * vec2(dimensions);
	vec2 vector = (uv - point_A) * vec2(dimensions);

	float t = 0.;
	float norm2 = dot(axis,axis);
	if(norm2 > 0.){
		t = clamp(dot(axis, vector) / norm2, 0., 1.);
	}else{
		if(vector.x > 0.){
			t = 1.;
		}
	}

	vec4 color = color_A*(1.-t) + color_B*t;
	imageStore(imgOutput, pixel_coords, color);
}