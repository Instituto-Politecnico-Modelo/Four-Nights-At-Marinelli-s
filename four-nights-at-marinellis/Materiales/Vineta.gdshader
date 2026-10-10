sshader_type canvas_item;
render_mode unshaded;

void fragment() {
	float distancia = length((UV - 0.5) * vec2(1.1, 0.85));
	COLOR = vec4(0.015, 0.024, 0.018, smoothstep(0.22, 0.72, distancia) * 0.46);
}