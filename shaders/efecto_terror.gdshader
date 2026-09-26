shader_type canvas_item;

uniform float vineta = 0.85;
uniform float grano = 0.05;

float azar(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	float distancia = distance(SCREEN_UV, vec2(0.5));
	float oscuridad = smoothstep(0.3, 0.85, distancia) * vineta;
	float ruido = azar(SCREEN_UV * 500.0 + fract(TIME) * 37.0);
	COLOR = vec4(vec3(ruido * 0.2), max(oscuridad, grano));
}
