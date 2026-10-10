shader_type spatial;

uniform vec4 color_base : source_color = vec4(0.6, 0.6, 0.6, 1.0);
uniform int tipo = 0;
uniform float desgaste = 0.12;
varying vec3 posicion;

float ruido(vec2 punto) {
	vec2 celda = floor(punto);
	vec2 mezcla = smoothstep(vec2(0.0), vec2(1.0), fract(punto));
	float primero = fract(sin(dot(celda, vec2(127.1, 311.7))) * 43758.5453);
	float segundo = fract(sin(dot(celda + vec2(1.0, 0.0), vec2(127.1, 311.7))) * 43758.5453);
	float tercero = fract(sin(dot(celda + vec2(0.0, 1.0), vec2(127.1, 311.7))) * 43758.5453);
	float cuarto = fract(sin(dot(celda + vec2(1.0), vec2(127.1, 311.7))) * 43758.5453);
	return mix(mix(primero, segundo, mezcla.x), mix(tercero, cuarto, mezcla.x), mezcla.y);
}

void vertex() {
	posicion = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec3 color = color_base.rgb;
	float mancha = ruido(posicion.xz * 6.0 + posicion.y * 3.0);
	float grano = ruido((posicion.xz + posicion.xy) * 145.0);
	if (tipo == 1) {
		vec2 baldosa = posicion.xz / 0.4;
		vec2 borde = min(fract(baldosa), 1.0 - fract(baldosa));
		float junta = 1.0 - smoothstep(0.009, 0.022, min(borde.x, borde.y));
		float variacion = ruido(floor(baldosa) * 3.17);
		color *= 0.88 + variacion * 0.18;
		if (posicion.x > 3.2 && (abs(posicion.z + 3.4) < 0.19 || (posicion.z < -3.2 && mod(floor(baldosa.x), 3.0) == 0.0))) {
			color *= vec3(0.52, 0.70, 0.79);
		}
		color = mix(color, vec3(0.19, 0.21, 0.20), junta * 0.7);
	} else if (tipo == 2) {
		float veta = ruido(vec2(posicion.x * 75.0 + posicion.z * 40.0, posicion.y * 2.2));
		color *= 0.76 + veta * 0.35;
	} else {
		float suciedad_baja = 1.0 - smoothstep(0.0, 0.4, posicion.y);
		color *= 1.0 - suciedad_baja * mancha * 0.2;
	}
	ALBEDO = color * (1.0 - mancha * desgaste - grano * 0.045);
	ROUGHNESS = 0.78 + mancha * 0.18;
}