shader_type canvas_item;

uniform float ruido = 0.08;
uniform float lineas = 0.08;
uniform vec3 tinte : source_color = vec3(0.85, 1.0, 0.88);

float azar(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	vec3 color = texture(TEXTURE, UV).rgb;
	float gris = dot(color, vec3(0.3, 0.59, 0.11));
	color = mix(color, vec3(gris), 0.7) * tinte;
	color += (azar(UV + fract(TIME)) - 0.5) * ruido;
	color *= 1.0 - lineas + lineas * sin(UV.y * 900.0);
	float borde = distance(UV, vec2(0.5));
	color *= 1.0 - borde * 0.8;
	COLOR = vec4(color, 1.0);
}
